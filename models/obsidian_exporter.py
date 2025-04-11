"""Module for exporting notes to Obsidian vault."""
import os
import re
import datetime
from typing import Dict, Optional, Union

class ObsidianExporter:
    """Class for exporting notes to Obsidian vault in Markdown format."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the Obsidian exporter with the path to your vault.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = vault_path
        
    def sanitize_filename(self, title: str) -> str:
        """
        Convert title to a valid filename.
        
        Args:
            title: Original title
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        title = re.sub(r'[\\/*?:"<>|]', '', title)
        # Replace spaces with hyphens
        title = re.sub(r'\s+', '-', title)
        return title.strip('-')
    
    def create_frontmatter(self, title: str, metadata: Optional[Dict] = None) -> str:
        """
        Create YAML frontmatter for Obsidian note.
        
        Args:
            title: Note title
            metadata: Additional metadata
            
        Returns:
            YAML frontmatter string
        """
        if metadata is None:
            metadata = {}
        
        # Default tags
        tags = ["coursera", "lecture-notes"]
        
        # Add course as tag
        if 'course_name' in metadata:
            course_tag = metadata['course_name'].lower().replace(' ', '-')
            tags.append(course_tag)
        
        # Add topics as tags
        if 'topics' in metadata and isinstance(metadata['topics'], list):
            topic_tags = [topic.lower().replace(' ', '-') for topic in metadata['topics']]
            tags.extend(topic_tags)
        
        # Create YAML frontmatter
        frontmatter = "---\n"
        frontmatter += f"title: {title}\n"
        frontmatter += f"date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
        
        # Add course and lecture info
        if 'course_name' in metadata:
            frontmatter += f"course: {metadata['course_name']}\n"
        if 'lecture_title' in metadata:
            frontmatter += f"lecture: {metadata['lecture_title']}\n"
            
        # frontmatter += f"tags: [{', '.join([f'"{tag}"' for tag in tags])}]\n"
        # frontmatter += f"tags: [{', '.join(['"' + tag + '"' for tag in tags])}]\n"
        tag_strings = [f'"{tag}"' for tag in tags]  
        frontmatter += f"tags: [{', '.join(tag_strings)}]\n"
        frontmatter += "---\n\n"
        
        return frontmatter
    
    def export_note(self, content: str, metadata: Optional[Dict] = None, folder: Optional[str] = None) -> Optional[str]:
        """
        Export notes to Obsidian vault.
        
        Args:
            content: Note content in Markdown format
            metadata: Note metadata
            folder: Optional subfolder within vault
            
        Returns:
            Path to saved file or None if failed
        """
        if metadata is None:
            metadata = {}
            
        # Generate title based on lecture info
        if 'lecture_title' in metadata and 'course_name' in metadata:
            title = f"{metadata['course_name']} - {metadata['lecture_title']}"
        elif 'lecture_title' in metadata:
            title = metadata['lecture_title']
        else:
            title = f"Lecture Notes {datetime.datetime.now().strftime('%Y-%m-%d')}"
        
        # Create folder path
        target_dir = self.vault_path
        if folder:
            target_dir = os.path.join(target_dir, folder)
        elif 'course_name' in metadata:
            # Organize by course name
            course_folder = self.sanitize_filename(metadata['course_name'])
            target_dir = os.path.join(target_dir, course_folder)
            
        # Ensure directory exists
        os.makedirs(target_dir, exist_ok=True)
        
        # Create filename
        filename = self.sanitize_filename(title) + ".md"
        file_path = os.path.join(target_dir, filename)
        
        # Add frontmatter
        content_with_frontmatter = self.create_frontmatter(title, metadata) + content
        
        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_with_frontmatter)
            print(f"Notes saved to {file_path}")
            return file_path
        except Exception as e:
            print(f"Error saving notes: {e}")
            return None