"""Final video composer that syncs video clips with audio and adds background music."""

import logging
import os
from typing import Optional

from moviepy.editor import AudioFileClip, CompositeVideoClip, VideoClip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Background music volume (10% of original)
MUSIC_VOLUME = 0.1


def compose_video(
    video_clip: VideoClip,
    audio_path: str,
    output_path: str,
    background_music: Optional[str] = None
) -> str:
    """
    Compose final video by syncing video clips to audio and optionally adding background music.
    
    Args:
        video_clip: VideoClip to compose (should be sequence of Ken Burns clips)
        audio_path: Path to narration audio file
        output_path: Path to save final video
        background_music: Optional path to background music file
        
    Returns:
        Path to the final composed video file
    """
    try:
        logger.info("Composing final video...")
        
        # Load audio
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        # Sync video to audio duration
        video_duration = video_clip.duration
        
        if video_duration < audio_duration:
            # Video is shorter - loop or extend last frame
            logger.info(f"Video ({video_duration:.2f}s) is shorter than audio ({audio_duration:.2f}s), extending...")
            # Loop the video to match audio duration
            num_loops = int(audio_duration / video_duration) + 1
            from moviepy.editor import concatenate_videoclips
            video_clips = [video_clip] * num_loops
            video_clip = concatenate_videoclips(video_clips, method="compose")
            # Trim to exact audio duration
            video_clip = video_clip.subclip(0, audio_duration)
        elif video_duration > audio_duration:
            # Video is longer - trim to audio duration
            logger.info(f"Video ({video_duration:.2f}s) is longer than audio ({audio_duration:.2f}s), trimming...")
            video_clip = video_clip.subclip(0, audio_duration)
        
        # Set audio
        video_clip = video_clip.set_audio(audio_clip)
        
        # Add background music if provided
        if background_music and os.path.exists(background_music):
            logger.info(f"Adding background music from {background_music}")
            video_clip = _add_background_music(video_clip, background_music, audio_duration)
        
        # Ensure correct dimensions (1080x1920)
        if video_clip.size != (1080, 1920):
            logger.warning(f"Video size is {video_clip.size}, resizing to 1080x1920")
            video_clip = video_clip.resize((1080, 1920))
        
        # Write final video
        logger.info(f"Rendering final video to {output_path}...")
        video_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None  # Suppress moviepy's verbose output
        )
        
        # Clean up
        audio_clip.close()
        video_clip.close()
        
        logger.info(f"Final video saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error composing video: {e}")
        raise


def _add_background_music(
    video: VideoClip,
    music_path: str,
    duration: float
) -> VideoClip:
    """
    Add background music to video at 10% volume.
    
    Args:
        video: Video clip to add music to
        music_path: Path to background music file
        duration: Duration to loop music for
        
    Returns:
        Video clip with background music added
    """
    try:
        music_clip = AudioFileClip(music_path)
        
        # Loop music if needed
        if music_clip.duration < duration:
            from moviepy.editor import concatenate_audioclips
            num_loops = int(duration / music_clip.duration) + 1
            music_clips = [music_clip] * num_loops
            music_clip = concatenate_audioclips(music_clips)
            music_clip = music_clip.subclip(0, duration)
        else:
            music_clip = music_clip.subclip(0, duration)
        
        # Reduce volume to 10%
        music_clip = music_clip.volumex(MUSIC_VOLUME)
        
        # Composite with existing audio
        if video.audio is not None:
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip([video.audio, music_clip])
            video = video.set_audio(final_audio)
        else:
            video = video.set_audio(music_clip)
        
        return video
        
    except Exception as e:
        logger.warning(f"Failed to add background music: {e}")
        return video

