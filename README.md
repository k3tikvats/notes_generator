# Coursera to Obsidian Notes Generator

This tool automatically generates high-quality notes from Coursera lecture transcripts and saves them to your Obsidian vault in Markdown format. It uses Claude API for intelligent processing and a RAG (Retrieval Augmented Generation) system to enhance notes with connections to previous lectures.

## Features

- **Transcript Processing**: Extract and clean transcripts from clipboard or file
- **Intelligent Note Generation**: Uses Claude API to create structured, comprehensive notes
- **RAG Enhancement**: Links current lecture content with previous lectures
- **Obsidian Integration**: Automatically saves notes to your vault with proper frontmatter
- **Automatic Organization**: Structures notes by courses and topics

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/coursera-notes-generator.git
   cd coursera-notes-generator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
   ```

## Usage

### Basic Usage

Run the tool with the default options (gets transcript from clipboard):

```bash
python main.py
```

### Command-line Options

- `--file` or `-f`: Path to a transcript file instead of clipboard
- `--title` or `-t`: Override the auto-detected lecture title
- `--course` or `-c`: Override the auto-detected course name
- `--folder`: Custom folder within your Obsidian vault
- `--clipboard`: Explicitly get transcript from clipboard (this is the default)

### Examples

1. Process transcript from clipboard for a specific course:
   ```bash
   python main.py --course "Machine Learning Specialization"
   ```

2. Process a transcript file with a custom title:
   ```bash
   python main.py --file lectures/week1.txt --title "Introduction to Deep Learning"
   ```

3. Save to a specific folder in your vault:
   ```bash
   python main.py --folder "Courses/Computer Science"
   ```

## Development

The project follows object-oriented design principles with a clear separation of concerns:

- `models/`: Data structures for the application
- `services/`: Core functionality components
- `utils/`: Helper functions and utilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.