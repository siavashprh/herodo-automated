"""Script generator for converting Wikipedia summaries into narration scripts."""

import logging
import re
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_script(summary: str, llm_client=None) -> Dict[str, any]:
    """
    Generate a script from Wikipedia summary.
    
    For now, extracts first 3 sentences. Future-proofed to accept LLM client
    for more sophisticated script generation.
    
    Args:
        summary: Wikipedia article summary text
        llm_client: Optional LLM client for future script generation (not used yet)
        
    Returns:
        Dictionary with keys: text (full script), sentences (list of sentences)
    """
    if llm_client:
        # Future: Use LLM to generate script
        logger.info("LLM client provided, but not yet implemented")
        # Placeholder for future implementation
        pass
    
    # Extract first 3 sentences
    sentences = _extract_sentences(summary)
    
    if len(sentences) >= 3:
        script_sentences = sentences[:3]
    else:
        script_sentences = sentences
    
    script_text = " ".join(script_sentences)
    
    logger.info(f"Generated script with {len(script_sentences)} sentences")
    
    return {
        "text": script_text,
        "sentences": script_sentences
    }


def _extract_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex.
    
    Args:
        text: Input text to split
        
    Returns:
        List of sentences
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split on sentence endings (., !, ?) followed by space and capital letter
    # This is a simple approach - could be improved with NLP libraries
    sentence_endings = r'([.!?])\s+([A-Z])'
    
    # Add markers for splitting
    marked_text = re.sub(sentence_endings, r'\1|||\2', text)
    
    # Split on markers
    parts = marked_text.split('|||')
    
    sentences = []
    for part in parts:
        part = part.strip()
        if part:
            # Ensure sentence ends with punctuation
            if not re.search(r'[.!?]$', part):
                part += '.'
            sentences.append(part)
    
    # Fallback: if regex didn't work well, split on periods
    if len(sentences) == 1 and '.' in sentences[0]:
        sentences = [s.strip() + '.' for s in sentences[0].split('.') if s.strip()]
    
    return sentences

