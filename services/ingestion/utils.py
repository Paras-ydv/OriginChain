"""
Utility functions for News Ingestion Service.
"""

import re
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import html2text
from dateutil import parser as date_parser

from config import ISO_DATE_FORMAT, MIN_ARTICLE_LENGTH, MAX_ARTICLE_LENGTH, TRANSLATION_ENABLED, TARGET_LANGUAGE

# Translation import with fallback (using deep-translator for Python 3.13 compatibility)
try:
    from deep_translator import GoogleTranslator
    from langdetect import detect as langdetect_detect
    TRANSLATION_AVAILABLE = True
except ImportError:
    GoogleTranslator = None
    langdetect_detect = None
    TRANSLATION_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_html(html_content: str) -> str:
    """
    Convert HTML to clean plain text.
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Cleaned plain text
    """
    if not html_content:
        return ""
    
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    # Get text using html2text for better formatting
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    
    text = h.handle(str(soup))
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
    text = re.sub(r' +', ' ', text)  # Remove excessive spaces
    text = text.strip()
    
    # Truncate if too long
    if len(text) > MAX_ARTICLE_LENGTH:
        text = text[:MAX_ARTICLE_LENGTH] + "..."
    
    return text


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent comparison.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Parse URL
    parsed = urlparse(url.lower().strip())
    
    # Remove common tracking parameters
    if parsed.query:
        # Strip common tracking params but keep content params
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 
                          'utm_content', 'fbclid', 'gclid', 'ref', 'source']
        query_parts = [q for q in parsed.query.split('&') 
                      if not any(q.startswith(param) for param in tracking_params)]
        query = '&'.join(query_parts) if query_parts else ''
    else:
        query = ''
    
    # Reconstruct URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip('/'),
        parsed.params,
        query,
        ''  # Remove fragment
    ))
    
    return normalized


def parse_date(date_string: str) -> Optional[str]:
    """
    Parse various date formats to ISO 8601.
    
    Args:
        date_string: Date string in various formats
        
    Returns:
        ISO 8601 formatted date string or None
    """
    if not date_string:
        return None
    
    try:
        # Use dateutil parser for flexible parsing
        dt = date_parser.parse(date_string)
        return dt.strftime(ISO_DATE_FORMAT)
    except (ValueError, TypeError):
        return None


def get_current_iso_time() -> str:
    """
    Get current time in ISO 8601 format.
    
    Returns:
        Current timestamp in ISO format
    """
    return datetime.utcnow().strftime(ISO_DATE_FORMAT)


def generate_article_id(url: str, title: str) -> str:
    """
    Generate unique article ID from URL and title.
    
    Args:
        url: Article URL
        title: Article title
        
    Returns:
        Unique article ID
    """
    # Create hash from URL and title
    content = f"{normalize_url(url)}|{title}".encode('utf-8')
    hash_obj = hashlib.sha256(content)
    return f"art_{hash_obj.hexdigest()[:12]}"


def generate_case_id(query: str, timestamp: str) -> str:
    """
    Generate unique case ID from query and timestamp.
    
    Args:
        query: Search query
        timestamp: ISO timestamp
        
    Returns:
        Unique case ID
    """
    content = f"{query}|{timestamp}".encode('utf-8')
    hash_obj = hashlib.sha256(content)
    return f"case_{hash_obj.hexdigest()[:12]}"


def is_valid_article_text(text: str) -> bool:
    """
    Check if article text is valid (meets minimum length).
    
    Args:
        text: Article text
        
    Returns:
        True if valid, False otherwise
    """
    if not text:
        return False
    return len(text.strip()) >= MIN_ARTICLE_LENGTH


def extract_domain(url: str) -> str:
    """
    Extract domain name from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "unknown"


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of text.
    
    Args:
        text: Text to detect language for
        
    Returns:
        Language code (e.g., 'en', 'es', 'fr') or None if detection fails
    """
    if not text or not TRANSLATION_AVAILABLE or langdetect_detect is None:
        return None
    
    try:
        # Use first 500 chars for detection (faster)
        sample = text[:500] if len(text) > 500 else text
        # Remove any HTML/special chars that might confuse detection
        sample = re.sub(r'<[^>]+>', '', sample)
        sample = sample.strip()
        
        if len(sample) < 10:  # Need minimum text for reliable detection
            return None
            
        detected = langdetect_detect(sample)
        return detected
    except Exception as e:
        logger.debug(f"Language detection failed: {str(e)}")
        return None


def translate_to_english(text: str, source_lang: Optional[str] = None) -> str:
    """
    Translate text to English.
    
    Args:
        text: Text to translate
        source_lang: Source language code (optional, auto-detected if not provided)
        
    Returns:
        Translated text in English, or original text if translation fails
    """
    if not text or not TRANSLATION_AVAILABLE or GoogleTranslator is None:
        return text
    
    try:
        # Skip if already English
        if source_lang == 'en' or source_lang == TARGET_LANGUAGE:
            return text
        
        # Translate using deep-translator
        translator = GoogleTranslator(source=source_lang or 'auto', target=TARGET_LANGUAGE)
        result = translator.translate(text)
        return result if result else text
    except Exception as e:
        logger.warning(f"Translation failed: {str(e)}")
        return text


def translate_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate article title and clean_text to English if not already in English.
    
    Args:
        article: Article dictionary with 'title', 'clean_text', and 'language' fields
        
    Returns:
        Article dictionary with translated content
    """
    if not TRANSLATION_ENABLED or not TRANSLATION_AVAILABLE:
        return article
    
    try:
        # Detect language from title or clean_text
        text_sample = article.get('title', '') or article.get('clean_text', '')[:200]
        detected_lang = detect_language(text_sample)
        
        # Skip if already English or detection failed
        if detected_lang is None or detected_lang == 'en':
            if article.get('language') != 'en':
                article['language'] = detected_lang or 'en'
            return article
        
        logger.info(f"Translating article from '{detected_lang}' to English")
        
        # Store original language
        article['original_language'] = detected_lang
        
        # Translate title
        if article.get('title'):
            article['title'] = translate_to_english(article['title'], detected_lang)
        
        # Translate clean_text
        if article.get('clean_text'):
            # Translate in chunks if text is very long (Google Translate limit)
            clean_text = article['clean_text']
            if len(clean_text) > 5000:
                # Translate in 5000 char chunks
                chunks = [clean_text[i:i+5000] for i in range(0, len(clean_text), 5000)]
                translated_chunks = [translate_to_english(chunk, detected_lang) for chunk in chunks]
                article['clean_text'] = ''.join(translated_chunks)
            else:
                article['clean_text'] = translate_to_english(clean_text, detected_lang)
        
        # Update language to English
        article['language'] = 'en'
        
    except Exception as e:
        logger.warning(f"Article translation failed: {str(e)}")
    
    return article
