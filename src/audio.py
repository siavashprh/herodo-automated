"""Text-to-speech narrator using Microsoft Edge TTS."""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional

import edge_tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default voice for documentary feel
DEFAULT_VOICE = "en-GB-RyanNeural"


def generate_narration(
    text: str,
    output_path: Optional[str] = None,
    voice: str = DEFAULT_VOICE,
    cache_dir: str = "cache/audio"
) -> Dict[str, any]:
    """
    Generate narration audio file from text using Edge TTS.
    
    Args:
        text: Text to convert to speech
        output_path: Optional output file path. If None, generates temp file in cache_dir
        voice: Voice to use (default: en-GB-RyanNeural for documentary feel)
        cache_dir: Directory for caching audio files
        
    Returns:
        Dictionary with keys: file_path (path to audio file), duration (duration in seconds)
    """
    try:
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate output path if not provided
        if output_path is None:
            # Use hash of text as filename for caching
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            output_path = os.path.join(cache_dir, f"{text_hash}.mp3")
        
        # Generate speech
        logger.info(f"Generating narration with voice '{voice}'...")
        
        # Use communicate to generate audio
        communicate = edge_tts.Communicate(text, voice)
        communicate.save(output_path)
        
        # Get actual duration from the audio file
        duration = get_audio_duration(output_path)
        if duration == 0:
            # Fallback to estimate if we can't read the file
            duration = _estimate_audio_duration(text)
        
        logger.info(f"Narration saved to {output_path} (duration: {duration:.2f}s)")
        
        return {
            "file_path": output_path,
            "duration": duration
        }
        
    except Exception as e:
        logger.error(f"Error generating narration: {e}")
        raise


def _estimate_audio_duration(text: str) -> float:
    """
    Estimate audio duration based on text length.
    Average speaking rate is ~150 words per minute.
    
    Args:
        text: Text to estimate duration for
        
    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    # Average speaking rate: 150 words per minute = 2.5 words per second
    words_per_second = 2.5
    estimated_duration = word_count / words_per_second
    
    return estimated_duration


def get_audio_duration(file_path: str) -> float:
    """
    Get actual duration of audio file.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        from moviepy.editor import AudioFileClip
        with AudioFileClip(file_path) as audio:
            return audio.duration
    except Exception as e:
        logger.warning(f"Could not get audio duration from file, using estimate: {e}")
        # Fallback: read file and estimate
        return 0.0

