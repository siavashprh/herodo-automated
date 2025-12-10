"""Ken Burns effect video generator for creating cinematic pan and zoom effects."""

import logging
import os
import random
import tempfile
from pathlib import Path
from typing import List, Optional

import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip, VideoClip
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target dimensions for vertical format (9:16)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


def create_ken_burns_clip(
    image_path: str,
    duration: float,
    start_zoom: float = 1.0,
    end_zoom: float = 1.3,
    pan_direction: str = "random"
) -> VideoClip:
    """
    Create a video clip with Ken Burns effect (slow pan and zoom).
    
    Args:
        image_path: Path to the source image
        duration: Duration of the clip in seconds
        start_zoom: Starting zoom level (1.0 = no zoom)
        end_zoom: Ending zoom level (1.3 = 30% zoom)
        pan_direction: Pan direction - "random", "left", "right", "up", "down", or "center"
        
    Returns:
        VideoClip with Ken Burns effect, cropped to 1080x1920
    """
    try:
        # Crop/resize image to target aspect ratio
        cropped_image_path = _crop_to_vertical(image_path)
        
        # Load image
        img = Image.open(cropped_image_path)
        img_array = np.array(img)
        
        # Create base clip from image
        clip = ImageClip(img_array, duration=duration)
        
        # Determine pan direction
        if pan_direction == "random":
            pan_direction = random.choice(["left", "right", "up", "down", "center"])
        
        # Calculate pan and zoom parameters
        pan_x, pan_y = _calculate_pan(img.width, img.height, pan_direction, start_zoom, end_zoom)
        
        # Apply zoom and pan effect using resize and crop
        def make_frame(t):
            # Calculate current zoom (linear interpolation with easing)
            progress = min(1.0, t / duration)
            # Easing function for smoother motion
            eased_progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
            current_zoom = start_zoom + (end_zoom - start_zoom) * eased_progress
            
            # Calculate current pan position
            current_pan_x = pan_x * eased_progress
            current_pan_y = pan_y * eased_progress
            
            # Calculate crop region
            crop_width = int(img.width / current_zoom)
            crop_height = int(img.height / current_zoom)
            
            # Center point with pan offset
            center_x = img.width / 2 + current_pan_x
            center_y = img.height / 2 + current_pan_y
            
            # Crop boundaries
            x1 = max(0, int(center_x - crop_width / 2))
            y1 = max(0, int(center_y - crop_height / 2))
            x2 = min(img.width, int(center_x + crop_width / 2))
            y2 = min(img.height, int(center_y + crop_height / 2))
            
            # Extract and resize cropped region
            if y2 <= y1 or x2 <= x1:
                return np.zeros((TARGET_HEIGHT, TARGET_WIDTH, 3), dtype=np.uint8)
            
            cropped = img_array[y1:y2, x1:x2]
            if cropped.size == 0 or cropped.shape[0] == 0 or cropped.shape[1] == 0:
                return np.zeros((TARGET_HEIGHT, TARGET_WIDTH, 3), dtype=np.uint8)
            
            # Resize to target dimensions
            from PIL import Image as PILImage
            pil_cropped = PILImage.fromarray(cropped)
            resized = pil_cropped.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            
            return np.array(resized)
        
        # Create video clip with custom frame function
        video_clip = clip.fl(make_frame)
        video_clip = video_clip.set_duration(duration)
        video_clip = video_clip.set_fps(24)  # Standard frame rate
        
        # Clean up temp file if we created one
        if cropped_image_path != image_path and os.path.exists(cropped_image_path):
            try:
                os.remove(cropped_image_path)
            except:
                pass
        
        return video_clip
        
    except Exception as e:
        logger.error(f"Error creating Ken Burns clip: {e}")
        raise


def create_visual_sequence(image_paths: List[str], total_duration: float) -> VideoClip:
    """
    Create a sequence of video clips from multiple images, distributing duration evenly.
    
    Args:
        image_paths: List of paths to source images
        total_duration: Total duration for all clips combined
        
    Returns:
        Composite VideoClip with all clips concatenated
    """
    if not image_paths:
        raise ValueError("No image paths provided")
    
    # Calculate duration per image
    num_images = len(image_paths)
    duration_per_image = total_duration / num_images
    
    clips = []
    
    for i, image_path in enumerate(image_paths):
        try:
            # Vary zoom and pan for visual interest
            start_zoom = random.uniform(1.0, 1.1)
            end_zoom = random.uniform(1.2, 1.4)
            pan_direction = random.choice(["left", "right", "up", "down", "center"])
            
            clip = create_ken_burns_clip(
                image_path,
                duration=duration_per_image,
                start_zoom=start_zoom,
                end_zoom=end_zoom,
                pan_direction=pan_direction
            )
            
            clips.append(clip)
            logger.info(f"Created clip {i+1}/{num_images} from {os.path.basename(image_path)}")
            
        except Exception as e:
            logger.warning(f"Failed to create clip from {image_path}: {e}")
            continue
    
    if not clips:
        raise ValueError("No valid clips created from images")
    
    # Concatenate clips
    from moviepy.editor import concatenate_videoclips
    final_clip = concatenate_videoclips(clips, method="compose")
    
    return final_clip


def _crop_to_vertical(image_path: str) -> str:
    """
    Crop/resize image to 1080x1920 (9:16) aspect ratio.
    Uses center cropping to preserve important content.
    
    Args:
        image_path: Path to source image
        
    Returns:
        Path to cropped image (may be temp file or original if already correct)
    """
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            target_aspect = TARGET_WIDTH / TARGET_HEIGHT  # 9:16 = 0.5625
            
            # Calculate crop dimensions
            img_aspect = img_width / img_height
            
            if abs(img_aspect - target_aspect) < 0.01:
                # Already correct aspect ratio, just resize
                if img_width != TARGET_WIDTH or img_height != TARGET_HEIGHT:
                    resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
                    temp_path = tempfile.mktemp(suffix=".jpg")
                    resized.save(temp_path, quality=95)
                    return temp_path
                return image_path
            
            # Need to crop
            if img_aspect > target_aspect:
                # Image is wider - crop width
                new_width = int(img_height * target_aspect)
                left = (img_width - new_width) // 2
                crop_box = (left, 0, left + new_width, img_height)
            else:
                # Image is taller - crop height
                new_height = int(img_width / target_aspect)
                top = (img_height - new_height) // 2
                crop_box = (0, top, img_width, top + new_height)
            
            # Crop and resize
            cropped = img.crop(crop_box)
            resized = cropped.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            
            # Save to temp file
            temp_path = tempfile.mktemp(suffix=".jpg")
            resized.save(temp_path, quality=95)
            
            return temp_path
            
    except Exception as e:
        logger.error(f"Error cropping image to vertical: {e}")
        raise


def _calculate_pan(
    img_width: int,
    img_height: int,
    direction: str,
    start_zoom: float,
    end_zoom: float
) -> tuple:
    """
    Calculate pan offset in pixels for given direction and zoom levels.
    
    Args:
        img_width: Image width
        img_height: Image height
        direction: Pan direction
        start_zoom: Starting zoom level
        end_zoom: Ending zoom level
        
    Returns:
        Tuple of (pan_x, pan_y) offsets in pixels
    """
    # Maximum pan distance (as percentage of image dimension)
    max_pan_percent = 0.15  # 15% of image dimension
    
    if direction == "center":
        return (0, 0)
    elif direction == "left":
        return (-img_width * max_pan_percent, 0)
    elif direction == "right":
        return (img_width * max_pan_percent, 0)
    elif direction == "up":
        return (0, -img_height * max_pan_percent)
    elif direction == "down":
        return (0, img_height * max_pan_percent)
    else:
        # Random diagonal
        return (
            random.uniform(-img_width * max_pan_percent, img_width * max_pan_percent),
            random.uniform(-img_height * max_pan_percent, img_height * max_pan_percent)
        )

