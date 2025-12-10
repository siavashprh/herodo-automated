"""Wikipedia content fetcher with image extraction and caching."""

import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
import wikipedia
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_wikipedia_content(page_title: str, cache_dir: str = "cache/images") -> Dict[str, any]:
    """
    Fetch Wikipedia article summary and extract image URLs.
    
    Args:
        page_title: Title of the Wikipedia page to fetch
        cache_dir: Directory to cache downloaded images
        
    Returns:
        Dictionary with keys: title, summary, image_urls
    """
    try:
        # Fetch page summary using wikipedia-api
        page = wikipedia.page(page_title)
        title = page.title
        summary = page.summary
        
        logger.info(f"Fetched Wikipedia page: {title}")
        
        # Extract image URLs using Wikipedia API directly
        image_urls = _extract_image_urls(page_title)
        
        # Download and cache images
        cached_image_paths = []
        os.makedirs(cache_dir, exist_ok=True)
        
        for url in image_urls:
            try:
                cached_path = _download_image(url, cache_dir)
                if cached_path:
                    cached_image_paths.append(cached_path)
            except Exception as e:
                logger.warning(f"Failed to download image {url}: {e}")
        
        return {
            "title": title,
            "summary": summary,
            "image_urls": image_urls,
            "cached_image_paths": cached_image_paths
        }
        
    except wikipedia.exceptions.PageError:
        logger.error(f"Wikipedia page not found: {page_title}")
        raise ValueError(f"Wikipedia page '{page_title}' not found")
    except wikipedia.exceptions.DisambiguationError as e:
        logger.error(f"Disambiguation error for '{page_title}': {e.options}")
        raise ValueError(f"'{page_title}' is ambiguous. Please specify a more specific title.")
    except Exception as e:
        logger.error(f"Error fetching Wikipedia content: {e}")
        raise


def _extract_image_urls(page_title: str) -> List[str]:
    """
    Extract image URLs from Wikipedia page using Wikipedia API.
    
    Args:
        page_title: Title of the Wikipedia page
        
    Returns:
        List of filtered image URLs
    """
    # Wikipedia API endpoint
    api_url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "images",
        "imlimit": "max"
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            logger.warning(f"No pages found for '{page_title}'")
            return []
        
        # Get page ID (first key in pages dict)
        page_id = list(pages.keys())[0]
        images = pages[page_id].get("images", [])
        
        if not images:
            logger.warning(f"No images found for '{page_title}'")
            return []
        
        # Get image info to filter and get full URLs
        image_titles = [img["title"] for img in images]
        
        # Fetch image info (dimensions, URL)
        image_info_params = {
            "action": "query",
            "format": "json",
            "titles": "|".join(image_titles),
            "prop": "imageinfo",
            "iiprop": "url|size|mime"
        }
        
        info_response = requests.get(api_url, params=image_info_params, timeout=10)
        info_response.raise_for_status()
        info_data = info_response.json()
        
        info_pages = info_data.get("query", {}).get("pages", {})
        filtered_urls = []
        
        for img_id, img_data in info_pages.items():
            imageinfo = img_data.get("imageinfo", [])
            if not imageinfo:
                continue
                
            img_info = imageinfo[0]
            width = img_info.get("width", 0)
            mime_type = img_info.get("mime", "")
            url = img_info.get("url", "")
            
            # Filter images
            if _is_valid_image(url, width, mime_type, img_data.get("title", "")):
                filtered_urls.append(url)
        
        logger.info(f"Found {len(filtered_urls)} valid images out of {len(images)} total")
        return filtered_urls
        
    except requests.RequestException as e:
        logger.error(f"Error fetching image URLs from Wikipedia API: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error extracting image URLs: {e}")
        return []


def _is_valid_image(url: str, width: int, mime_type: str, title: str) -> bool:
    """
    Filter out invalid images (icons, flags, small thumbnails, etc.).
    
    Args:
        url: Image URL
        width: Image width in pixels
        mime_type: MIME type of the image
        title: Image title from Wikipedia
        
    Returns:
        True if image is valid, False otherwise
    """
    # Check MIME type
    if not mime_type.startswith("image/"):
        return False
    
    # Exclude small images
    if width < 200:
        return False
    
    # Exclude common non-historical images
    title_lower = title.lower()
    exclude_keywords = [
        "icon", "logo", "flag", "svg", "button", "arrow",
        "symbol", "emblem", "badge", "seal", "coat of arms"
    ]
    
    for keyword in exclude_keywords:
        if keyword in title_lower:
            return False
    
    # Exclude file type indicators in URL
    url_lower = url.lower()
    if any(ext in url_lower for ext in [".svg", ".gif"]):
        # Allow GIFs if they're large enough (could be historical photos)
        if ".gif" in url_lower and width >= 500:
            return True
        return False
    
    return True


def _download_image(url: str, cache_dir: str) -> Optional[str]:
    """
    Download and cache an image locally.
    
    Args:
        url: URL of the image to download
        cache_dir: Directory to cache the image
        
    Returns:
        Path to cached image file, or None if download failed
    """
    try:
        # Create hash-based filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed_url = urlparse(url)
        file_ext = os.path.splitext(parsed_url.path)[1] or ".jpg"
        filename = f"{url_hash}{file_ext}"
        filepath = os.path.join(cache_dir, filename)
        
        # Skip if already cached
        if os.path.exists(filepath):
            logger.debug(f"Image already cached: {filename}")
            return filepath
        
        # Download image
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Save to cache
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Validate image
        try:
            with Image.open(filepath) as img:
                img.verify()
            logger.info(f"Cached image: {filename}")
            return filepath
        except Exception as e:
            logger.warning(f"Invalid image file {filename}, removing: {e}")
            os.remove(filepath)
            return None
            
    except requests.RequestException as e:
        logger.warning(f"Failed to download image from {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Error caching image {url}: {e}")
        return None

