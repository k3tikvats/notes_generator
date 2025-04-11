"""Module for extracting metadata from lecture transcripts."""
import re
import json
import google.generativeai as genai
from typing import Dict

class MetadataExtractor:
    """Class responsible for extracting metadata from transcripts."""
    
    def __init__(self, api_key: str):
        """
        Initialize the metadata extractor with Gemini API.
        
        Args:
            api_key: Gemini API key
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
    
    def extract_metadata(self, transcript: str) -> Dict:
        """
        Extract course and lecture metadata from transcript.
        
        Args:
            transcript: Lecture transcript
            
        Returns:
            Dictionary containing metadata
        """
        metadata_prompt = f"""
        Given the following lecture transcript, extract:
        1. The course name/title
        2. The lecture number and/or title
        3. The main topic(s) covered (as a list of strings)
        
        Format your response as a JSON object with "course_name", "lecture_title", and "topics" keys.
        
        Transcript (beginning excerpt):
        {transcript[:1500]}
        
        Return ONLY the JSON object, with no additional text.
        """
        
        try:
            response = self.model.generate_content(metadata_prompt)
            
            # Extract JSON response
            json_str = response.text
            
            # Find JSON if it's embedded in text
            json_match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find just the JSON object
                json_match = re.search(r'(\{\s*".*})', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
            
            metadata = json.loads(json_str)
            return metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                "course_name": "Unknown Course",
                "lecture_title": "Untitled Lecture",
                "topics": []
            }