"""Main pipeline orchestrator for generating history documentaries."""

import argparse
import logging
import os
import sys
from pathlib import Path

try:
    # Try relative imports (when run as module)
    from .audio import generate_narration, get_audio_duration
    from .editor import compose_video
    from .research import fetch_wikipedia_content
    from .script import generate_script
    from .visuals import create_visual_sequence
except ImportError:
    # Fall back to absolute imports (when run directly)
    from audio import generate_narration, get_audio_duration
    from editor import compose_video
    from research import fetch_wikipedia_content
    from script import generate_script
    from visuals import create_visual_sequence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_historical_event(
    page_title: str,
    output_path: str,
    background_music: str = None
) -> str:
    """
    Process a historical event through the full pipeline.
    
    Args:
        page_title: Wikipedia page title to process
        output_path: Path to save final video
        background_music: Optional path to background music file
        
    Returns:
        Path to the generated video file
    """
    try:
        logger.info(f"Starting pipeline for: {page_title}")
        
        # Step 1: Research - Fetch Wikipedia content and images
        logger.info("Step 1: Fetching Wikipedia content...")
        research_data = fetch_wikipedia_content(page_title)
        
        if not research_data.get("cached_image_paths"):
            raise ValueError(f"No valid images found for '{page_title}'. Cannot create video.")
        
        logger.info(f"Found {len(research_data['cached_image_paths'])} images")
        
        # Step 2: Script - Generate script from summary
        logger.info("Step 2: Generating script...")
        script_data = generate_script(research_data["summary"])
        script_text = script_data["text"]
        
        logger.info(f"Generated script: {script_text[:100]}...")
        
        # Step 3: Audio - Generate narration
        logger.info("Step 3: Generating narration...")
        audio_data = generate_narration(script_text)
        audio_path = audio_data["file_path"]
        
        # Get actual audio duration
        audio_duration = get_audio_duration(audio_path)
        if audio_duration == 0:
            audio_duration = audio_data["duration"]  # Fallback to estimate
        
        logger.info(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Step 4: Visuals - Create Ken Burns video sequence
        logger.info("Step 4: Creating visual sequence with Ken Burns effect...")
        video_clip = create_visual_sequence(
            research_data["cached_image_paths"],
            total_duration=audio_duration
        )
        
        logger.info(f"Video clip created: {video_clip.duration:.2f} seconds")
        
        # Step 5: Editor - Compose final video
        logger.info("Step 5: Composing final video...")
        final_video_path = compose_video(
            video_clip,
            audio_path,
            output_path,
            background_music
        )
        
        logger.info(f"Pipeline complete! Video saved to: {final_video_path}")
        return final_video_path
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate vertical history documentaries from Wikipedia articles"
    )
    parser.add_argument(
        "page_title",
        type=str,
        help="Wikipedia page title to process (e.g., 'Battle of Gettysburg')"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output.mp4",
        help="Output video file path (default: output.mp4)"
    )
    parser.add_argument(
        "-m", "--music",
        type=str,
        default=None,
        help="Optional path to background music file"
    )
    
    args = parser.parse_args()
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output) if os.path.dirname(args.output) else "."
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the historical event
        video_path = process_historical_event(
            args.page_title,
            args.output,
            args.music
        )
        
        print(f"\n✓ Success! Video generated: {video_path}")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

