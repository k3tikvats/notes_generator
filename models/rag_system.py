"""Module implementing the Retrieval-Augmented Generation system."""
import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Union
import json

class RagSystem:
    """Class implementing a Retrieval-Augmented Generation system for course notes."""
    
    def __init__(self, vector_db_path: str = "./chroma_db"):
        """
        Initialize the RAG system with a ChromaDB instance.
        
        Args:
            vector_db_path: Path to store the vector database
        """
        self.vector_db_path = vector_db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=vector_db_path)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name="course_notes", 
                embedding_function=self.embedding_function
            )
            print(f"Using existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="course_notes", 
                embedding_function=self.embedding_function
            )
            print("Created new collection for course notes")
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Add a document to the vector database.
        
        Args:
            doc_id: Unique identifier for the document
            content: Text content of the document
            metadata: Additional metadata for the document
        """
        if metadata is None:
            metadata = {}
            
        # Convert any non-supported types in metadata to strings
        processed_metadata = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                processed_metadata[k] = v
            else:
                # Convert lists, dicts and other objects to JSON strings
                processed_metadata[k] = json.dumps(v)
            
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[processed_metadata]
        )
        print(f"Added document '{doc_id}' to the vector database")
    
    def retrieve_relevant_context(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: The query text
            k: Number of results to retrieve
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        if self.collection.count() == 0:
            print("Vector database is empty. No context to retrieve.")
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        documents = []
        for i, doc in enumerate(results['documents'][0]):
            documents.append({
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
            })
            
        return documents
    
    def chunk_and_index_text(self, text: str, doc_id: str, metadata: Optional[Dict] = None) -> None:
        """
        Chunk text and index it in the vector database.
        
        Args:
            text: Text to chunk and index
            doc_id: Base identifier for the document
            metadata: Metadata to associate with the chunks
        """
        # Simple chunking by paragraphs for now
        chunks = [p for p in text.split('\n\n') if p.strip()]
        
        # If only one chunk or text is small, don't chunk
        if len(chunks) <= 1 or len(text) < 1000:
            self.add_document(doc_id, text, metadata)
            return
            
        # Add each chunk with its own ID but shared metadata
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['parent_id'] = doc_id
            chunk_metadata['chunk_index'] = i
            
            self.add_document(chunk_id, chunk, chunk_metadata)