"""
Coursera to Obsidian Notes Generator
Converts lecture transcripts to structured markdown notes and saves them to Obsidian.
"""
import argparse
from utils.config import load_config
from models.transcript_parser import TranscriptParser
from models.notes_generator import NotesGenerator
from models.obsidian_exporter import ObsidianExporter

def main():
    """Main function to run the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert Coursera transcripts to Obsidian notes')
    parser.add_argument('--file', '-f', help='Path to transcript file')
    parser.add_argument('--title', '-t', help='Title for the notes')
    parser.add_argument('--course', '-c', help='Course name')
    parser.add_argument('--folder', help='Folder in Obsidian vault to save notes')
    parser.add_argument('--clipboard', action='store_true', help='Get transcript from clipboard')
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Initialize components
    transcript_parser = TranscriptParser()
    notes_generator = NotesGenerator(
        api_key=config['gemini_api_key'],
        rag_db_path=config['rag_db_path']
    )
    obsidian_exporter = ObsidianExporter(config['obsidian_vault_path'])
    
    # Get transcript content
    transcript = None
    if args.file:
        transcript = transcript_parser.from_file(args.file)
    elif args.clipboard:
        transcript = transcript_parser.from_clipboard()
    else:
        print("Getting transcript from clipboard (default)")
        transcript = transcript_parser.from_clipboard()
    
    if not transcript:
        print("Failed to get transcript content")
        return
    
    print("Generating notes... (this may take a moment)")
    
    # Generate notes
    result = notes_generator.generate_complete_notes(
        transcript, 
        title=args.title, 
        course_name=args.course
    )
    
    # Export notes to Obsidian
    file_path = obsidian_exporter.export_note(
        content=result['notes'],
        metadata=result['metadata'],
        folder=args.folder
    )
    
    if file_path:
        print(f"Success! Notes saved to: {file_path}")
    else:
        print("Failed to save notes to Obsidian")

if __name__ == "__main__":
    main()