"""Module for generating lecture notes using Gemini API and RAG."""
import datetime
import google.generativeai as genai
from typing import Dict, Optional

from .rag_system import RagSystem
from .metadata_extractor import MetadataExtractor

class NotesGenerator:
    """Class for generating structured notes from transcripts using Gemini API and RAG."""
    
    def __init__(self, api_key: str, rag_db_path: str = "./chroma_db"):
        """
        Initialize the notes generator with Gemini API.
        
        Args:
            api_key: Gemini API key
            rag_db_path: Path to the RAG database
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Configure the model
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config
        )
        
        # Initialize RAG system and metadata extractor
        self.rag_system = RagSystem(rag_db_path)
        self.metadata_extractor = MetadataExtractor(api_key)
        
    def generate_basic_notes(self, transcript: str, metadata: Optional[Dict] = None) -> str:
        """
        Generate structured notes using Gemini API.
        
        Args:
            transcript: Lecture transcript
            metadata: Optional metadata about the lecture
            
        Returns:
            Markdown formatted notes
        """
        if metadata is None:
            metadata = self.metadata_extractor.extract_metadata(transcript)
        
        prompt = f"""
        I have a transcript from a Coursera lecture. Please convert it into well-structured 
        Markdown notes with the following:
        - A clear title based on the lecture content
        - A brief summary (2-3 sentences)
        - Key concepts and definitions in a list or table
        - Main points organized into logical sections with headings
        - Any important examples, applications, or case studies mentioned
        - Key takeaways at the end
        
        Course: {metadata.get('course_name', 'Unspecified')}
        Lecture: {metadata.get('lecture_title', 'Unspecified')}
        
        Here's the transcript:
        {transcript}
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def enhance_with_rag(self, notes: str, transcript: str, metadata: Dict) -> str:
        """
        Enhance notes with context from previous lectures using RAG.
        
        Args:
            notes: Generated notes content
            transcript: Original transcript
            metadata: Lecture metadata
            
        Returns:
            Enhanced notes with connections to previous content
        """
        # Get relevant context
        relevant_docs = self.rag_system.retrieve_relevant_context(transcript[:1000], k=3)
        
        if not relevant_docs:
            return notes  # No relevant context found
        
        # Format the context
        context_text = ""
        for i, doc in enumerate(relevant_docs):
            doc_metadata = doc['metadata']
            context_text += f"--- Document {i+1} ---\n"
            context_text += f"Source: {doc_metadata.get('course_name', 'Unknown Course')}, "
            context_text += f"Lecture: {doc_metadata.get('lecture_title', 'Unknown Lecture')}\n\n"
            context_text += f"{doc['content']}\n\n"
        
        # Create enhancement prompt
        enhancement_prompt = f"""
        I have notes from a lecture, and I'd like to enhance them with connections
        to previous lectures in the course. 
        
        Current lecture:
        - Course: {metadata.get('course_name', 'Unknown')}
        - Lecture: {metadata.get('lecture_title', 'Unknown')}
        
        Here are my current notes:
        {notes}
        
        Here is relevant information from previous lectures:
        {context_text}
        
        Please enhance the notes by:
        1. Adding a new section called "Connections to Previous Lectures" that explains how this lecture builds on previous content
        2. Adding cross-references where concepts relate to previous lectures
        3. Clarifying any concepts that were introduced earlier but are used again here
        
        Return the complete enhanced notes, not just the new sections.
        """
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            return response.text
        except Exception as e:
            print(f"Error enhancing notes with RAG: {e}")
            return notes  # Return original notes if enhancement fails
    
    def generate_complete_notes(self, transcript: str, title: Optional[str] = None, course_name: Optional[str] = None) -> Dict:
        """
        Generate complete notes using both Gemini and RAG if available.
        
        Args:
            transcript: Lecture transcript
            title: Optional lecture title
            course_name: Optional course name
            
        Returns:
            Dictionary with notes content and metadata
        """
        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata(transcript)
        
        # Override metadata with provided information
        if title:
            metadata['lecture_title'] = title
        if course_name:
            metadata['course_name'] = course_name
            
        # Generate basic notes
        notes = self.generate_basic_notes(transcript, metadata)
        
        # Enhance with RAG if we have previous documents
        enhanced_notes = self.enhance_with_rag(notes, transcript, metadata)
        
        # Index this document for future reference
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        doc_id = f"{metadata['course_name']}_{metadata['lecture_title']}_{current_date}".replace(" ", "_")
        
        # Add notes to RAG system
        self.rag_system.chunk_and_index_text(
            enhanced_notes, 
            doc_id, 
            {
                'course_name': metadata['course_name'],
                'lecture_title': metadata['lecture_title'],
                'date': current_date,
                'topics': metadata.get('topics', [])
            }
        )
        
        return {
            'notes': enhanced_notes,
            'metadata': metadata
        }