"""
Utility functions for News Ingestion Service.
"""

import re
import hashlib
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import html2text
from dateutil import parser as date_parser

from .config import ISO_DATE_FORMAT, MIN_ARTICLE_LENGTH, MAX_ARTICLE_LENGTH


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
