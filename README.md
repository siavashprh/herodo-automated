# Herodo Automated - History Documentary Generator

An autonomous Python pipeline that generates vertical (9:16) short-form history documentaries from Wikipedia articles. The system automatically fetches historical content, creates cinematic Ken Burns effect videos, generates narration, and composes professional-looking documentaries.

## Features

- **Wikipedia Integration**: Automatically fetches article summaries and extracts relevant images
- **Ken Burns Effect**: Creates cinematic pan and zoom effects on historical images
- **Text-to-Speech**: Uses Microsoft Edge TTS for natural-sounding narration
- **Smart Image Caching**: Local caching system to avoid re-downloading images
- **Background Music Support**: Optional background music at 10% volume
- **Vertical Format**: All videos output in 1080x1920 (9:16) format for short-form platforms

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd herodo-automated-1
```

2. Set up a virtual environment (recommended):
```bash
# On Ubuntu/Debian, you may need to install python3-venv first:
sudo apt install python3-venv

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** If you're on a system with externally-managed Python (like newer Ubuntu), you must use a virtual environment. If you prefer not to use a venv, you can use `pip install --break-system-packages -r requirements.txt`, but this is not recommended.

## Usage

### Basic Usage

Generate a documentary from a Wikipedia article:

```bash
python -m src.main "Battle of Gettysburg"
```

### With Custom Output Path

```bash
python -m src.main "World War II" -o my_documentary.mp4
```

### With Background Music

```bash
python -m src.main "Renaissance" -o output.mp4 -m background_music.mp3
```

## Testing

Run the test suite to verify all modules work correctly:

```bash
python test_pipeline.py
```

The test script will:
1. Test each module individually (research, script, audio, visuals)
2. Optionally run a full end-to-end test that creates a sample video
3. Verify that images are downloaded and cached
4. Check that audio generation works
5. Test the Ken Burns effect on a sample image

The end-to-end test creates a short test video (`test_output.mp4`) that you can review to verify the pipeline works correctly.

## Project Structure

```
herodo-automated-1/
├── src/
│   ├── __init__.py
│   ├── research.py      # Wikipedia content fetcher
│   ├── script.py        # Script generator
│   ├── visuals.py       # Ken Burns effect video generator
│   ├── audio.py         # Text-to-speech narrator
│   ├── editor.py        # Final video composer
│   └── main.py          # Pipeline orchestrator
├── cache/
│   ├── images/          # Cached Wikipedia images
│   └── audio/           # Cached audio files
├── requirements.txt
└── README.md
```

## Module Details

### `research.py`
- Fetches Wikipedia article summaries using `wikipedia-api`
- Extracts image URLs using Wikipedia API
- Downloads and caches images locally
- Filters out icons, flags, and small thumbnails

### `script.py`
- Generates scripts from Wikipedia summaries
- Currently extracts first 3 sentences (future-proofed for LLM integration)
- Returns structured script with sentences

### `visuals.py`
- Implements Ken Burns effect (slow pan and zoom)
- Handles multiple images, distributing them evenly
- Crops/resizes all images to 1080x1920 (9:16) format
- Creates smooth cinematic transitions

### `audio.py`
- Uses Microsoft Edge TTS (`edge-tts`)
- Default voice: `en-GB-RyanNeural` (documentary feel)
- Caches audio files for efficiency

### `editor.py`
- Syncs video clips to audio duration
- Adds background music at 10% volume (optional)
- Composes final video in 1080x1920 format

### `main.py`
- Orchestrates the entire pipeline
- Command-line interface
- Error handling and logging

## Dependencies

- `wikipedia-api`: Wikipedia content fetching
- `requests`: HTTP requests for image downloads
- `Pillow`: Image processing
- `moviepy`: Video editing and composition
- `edge-tts`: Microsoft Edge Text-to-Speech
- `numpy`: Numerical operations

## Notes

- Images are cached locally in `cache/images/` to avoid re-downloading
- Audio files are cached in `cache/audio/` based on text hash
- The system handles multiple images automatically, creating visual variety
- Video duration is flexible and determined by the script/audio length
- All videos are output in vertical format (1080x1920) for short-form platforms

## Future Enhancements

- LLM integration for more sophisticated script generation
- Cloud integration for caching
- Custom voice selection
- Advanced video effects and transitions
- Batch processing for multiple articles

## License

MIT License - see LICENSE file for details
