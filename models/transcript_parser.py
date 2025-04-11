"""Module for parsing and extracting transcripts from various sources."""
import re
import pyperclip
from typing import Optional

class TranscriptParser:
    """Class responsible for parsing and cleaning transcripts."""
    
    def clean_transcript(self, text: str) -> str:
        """
        Clean and format the raw transcript text.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned transcript text
        """
        if not text:
            return ""
            
        # Remove timestamps if present (format [MM:SS])
        text = re.sub(r'\[\d+:\d+\]', '', text)
        
        # Remove speaker identifiers if present
        text = re.sub(r'^.+?:', '', text, flags=re.MULTILINE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def from_clipboard(self) -> Optional[str]:
        """
        Get transcript from clipboard.
        
        Returns:
            Cleaned transcript text or None if failed
        """
        try:
            transcript = pyperclip.paste()
            if not transcript:
                print("Clipboard is empty")
                return None
                
            return self.clean_transcript(transcript)
        except Exception as e:
            print(f"Error getting text from clipboard: {e}")
            return None
    
    def from_file(self, file_path: str) -> Optional[str]:
        """
        Read transcript from a file.
        
        Args:
            file_path: Path to the transcript file
            
        Returns:
            Cleaned transcript text or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
            return self.clean_transcript(transcript)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None