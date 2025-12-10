"""Test script for the history documentary pipeline."""

import os
import sys
import logging

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from research import fetch_wikipedia_content
from script import generate_script
from audio import generate_narration
from visuals import create_ken_burns_clip
from editor import compose_video

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_research():
    """Test Wikipedia content fetching."""
    print("\n" + "="*60)
    print("TEST 1: Research Module - Fetching Wikipedia Content")
    print("="*60)
    
    try:
        result = fetch_wikipedia_content("Battle of Gettysburg")
        print(f"✓ Successfully fetched: {result['title']}")
        print(f"✓ Summary length: {len(result['summary'])} characters")
        print(f"✓ Found {len(result['image_urls'])} image URLs")
        print(f"✓ Cached {len(result['cached_image_paths'])} images")
        
        if result['cached_image_paths']:
            print(f"  First cached image: {result['cached_image_paths'][0]}")
        
        return result
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def test_script():
    """Test script generation."""
    print("\n" + "="*60)
    print("TEST 2: Script Module - Generating Script")
    print("="*60)
    
    try:
        sample_summary = """
        The Battle of Gettysburg was a major battle of the American Civil War.
        It was fought from July 1 to July 3, 1863, in and around the town of Gettysburg, Pennsylvania.
        The battle had the largest number of casualties in the entire war.
        It is often considered the turning point of the Civil War.
        """
        
        result = generate_script(sample_summary)
        print(f"✓ Generated script with {len(result['sentences'])} sentences")
        print(f"✓ Script text: {result['text'][:100]}...")
        
        return result
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def test_audio():
    """Test audio generation."""
    print("\n" + "="*60)
    print("TEST 3: Audio Module - Generating Narration")
    print("="*60)
    
    try:
        test_text = "The Battle of Gettysburg was a major battle of the American Civil War."
        result = generate_narration(test_text, output_path="test_audio.mp3")
        print(f"✓ Generated audio file: {result['file_path']}")
        print(f"✓ Audio duration: {result['duration']:.2f} seconds")
        
        if os.path.exists(result['file_path']):
            file_size = os.path.getsize(result['file_path']) / 1024  # KB
            print(f"✓ File size: {file_size:.2f} KB")
        
        return result
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None


def test_visuals(research_result):
    """Test Ken Burns effect."""
    print("\n" + "="*60)
    print("TEST 4: Visuals Module - Ken Burns Effect")
    print("="*60)
    
    if not research_result or not research_result.get('cached_image_paths'):
        print("✗ Skipped: No images available from research test")
        return None
    
    try:
        image_path = research_result['cached_image_paths'][0]
        print(f"Testing with image: {os.path.basename(image_path)}")
        
        # Create a short clip (2 seconds for testing)
        clip = create_ken_burns_clip(image_path, duration=2.0)
        print(f"✓ Created Ken Burns clip")
        print(f"✓ Clip duration: {clip.duration:.2f} seconds")
        print(f"✓ Clip size: {clip.size}")
        print(f"✓ Clip fps: {clip.fps}")
        
        # Clean up
        clip.close()
        
        return clip
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_end_to_end():
    """Test the full pipeline with a simple article."""
    print("\n" + "="*60)
    print("TEST 5: End-to-End Pipeline Test")
    print("="*60)
    print("This will create a short test video. It may take a few minutes...")
    
    try:
        # Use a simple, well-known article
        test_article = "Python (programming language)"
        
        print(f"\nFetching: {test_article}...")
        research_result = fetch_wikipedia_content(test_article)
        
        if not research_result.get('cached_image_paths'):
            print("✗ No images found, cannot create video")
            return False
        
        print(f"✓ Found {len(research_result['cached_image_paths'])} images")
        
        print("\nGenerating script...")
        script_result = generate_script(research_result['summary'])
        script_text = script_result['text']
        print(f"✓ Script: {script_text[:80]}...")
        
        print("\nGenerating audio...")
        audio_result = generate_narration(script_text, output_path="test_narration.mp3")
        audio_duration = audio_result['duration']
        print(f"✓ Audio duration: {audio_duration:.2f} seconds")
        
        print("\nCreating visual sequence...")
        video_clip = create_visual_sequence(
            research_result['cached_image_paths'],
            total_duration=min(audio_duration, 10.0)  # Cap at 10 seconds for testing
        )
        print(f"✓ Video clip created: {video_clip.duration:.2f} seconds")
        
        print("\nComposing final video...")
        output_path = "test_output.mp4"
        final_path = compose_video(
            video_clip,
            audio_result['file_path'],
            output_path
        )
        
        if os.path.exists(final_path):
            file_size = os.path.getsize(final_path) / (1024 * 1024)  # MB
            print(f"✓ Final video created: {final_path}")
            print(f"✓ File size: {file_size:.2f} MB")
            print(f"\n🎉 SUCCESS! Test video created at: {final_path}")
            return True
        else:
            print("✗ Video file not found")
            return False
            
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("HERODO AUTOMATED - PIPELINE TEST SUITE")
    print("="*60)
    
    # Run individual module tests
    research_result = test_research()
    script_result = test_script()
    audio_result = test_audio()
    visuals_result = test_visuals(research_result)
    
    # Ask user if they want to run end-to-end test
    print("\n" + "="*60)
    response = input("Run full end-to-end test? This will create a test video (y/n): ").strip().lower()
    
    if response == 'y':
        test_end_to_end()
    else:
        print("Skipping end-to-end test.")
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    cleanup_files = ["test_audio.mp3", "test_narration.mp3"]
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Removed {file}")
            except:
                print(f"✗ Could not remove {file}")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print("\nNote: test_output.mp4 (if created) was not removed.")
    print("You can review it to verify the pipeline works correctly.")


if __name__ == "__main__":
    main()

