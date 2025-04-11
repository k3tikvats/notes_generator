"""Configuration utilities for the application."""
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    
    config = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'obsidian_vault_path': os.getenv('OBSIDIAN_VAULT_PATH'),
        'rag_db_path': os.getenv('RAG_DB_PATH', './chroma_db')
    }
    
    # Validate required configuration
    if not config['gemini_api_key']:
        raise ValueError("Missing GEMINI_API_KEY in environment variables")
    
    if not config['obsidian_vault_path']:
        print("Warning: OBSIDIAN_VAULT_PATH not set in environment variables")
        config['obsidian_vault_path'] = input("Please enter your Obsidian vault path: ")
    
    return config