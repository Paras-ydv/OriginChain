"""
Data source handlers for GDELT API and RSS feeds.
"""

import time
import requests
import feedparser
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from .config import (
    RSS_FEEDS, GDELT_API_URL, GDELT_MODE, GDELT_FORMAT,
    GDELT_MAX_RECORDS, REQUEST_TIMEOUT, MAX_RETRIES,
    RETRY_DELAY, USER_AGENT
)
from .utils import parse_date, extract_domain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GDELTClient:
    """Client for GDELT API."""
    
    def __init__(self):
        self.api_url = GDELT_API_URL
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(
        self,
        query: str,
        max_records: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search GDELT for articles matching query.
        
        Args:
            query: Search query
            max_records: Maximum number of records to return
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            # Build query parameters
            params = {
                'query': query,
                'mode': GDELT_MODE,
                'format': GDELT_FORMAT,
                'maxrecords': min(max_records, GDELT_MAX_RECORDS)
            }
            
            # Add date range if provided
            if start_date and end_date:
                # GDELT uses YYYYMMDDHHMMSS format
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                params['startdatetime'] = start_dt.strftime('%Y%m%d000000')
                params['enddatetime'] = end_dt.strftime('%Y%m%d235959')
            
            # Make request with retry logic
            response = self._make_request(params)
            
            if response and 'articles' in response:
                for item in response['articles']:
                    article = self._parse_gdelt_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"GDELT: Fetched {len(articles)} articles for query '{query}'")
            
        except Exception as e:
            logger.error(f"GDELT search error: {str(e)}")
        
        return articles
    
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Make HTTP request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    self.api_url,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"GDELT request attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("GDELT request failed after all retries")
                    return None
    
    def _parse_gdelt_article(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Parse GDELT article into standard format."""
        try:
            url = item.get('url', '')
            if not url:
                return None
            
            # Extract metadata
            title = item.get('title', '').strip()
            source = item.get('domain', extract_domain(url))
            
            # Parse date
            date_str = item.get('seendate', '')
            published_at = parse_date(date_str) if date_str else None
            
            return {
                'url': url,
                'title': title,
                'source_name': source,
                'published_at': published_at,
                'author': None,  # GDELT doesn't provide author
                'language': item.get('language', 'en'),
                'raw_text': None  # Will be fetched separately
            }
        except Exception as e:
            logger.warning(f"Failed to parse GDELT article: {str(e)}")
            return None


class RSSFeedClient:
    """Client for RSS feeds."""
    
    def __init__(self):
        self.feeds = RSS_FEEDS
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(
        self,
        query: str,
        max_records: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search RSS feeds for articles matching query.
        
        Args:
            query: Search query (keywords to filter)
            max_records: Maximum number of records to return
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        query_lower = query.lower()
        
        # Parse date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Fetch from all feeds
        for source_name, feed_urls in self.feeds.items():
            for feed_url in feed_urls:
                try:
                    feed_articles = self._fetch_feed(
                        feed_url, source_name, query_lower, start_dt, end_dt
                    )
                    articles.extend(feed_articles)
                    
                    # Stop if we have enough
                    if len(articles) >= max_records:
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch RSS feed {feed_url}: {str(e)}")
                    continue
            
            if len(articles) >= max_records:
                break
        
        logger.info(f"RSS: Fetched {len(articles)} articles for query '{query}'")
        return articles[:max_records]
    
    def _fetch_feed(
        self,
        feed_url: str,
        source_name: str,
        query: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Fetch and parse single RSS feed."""
        articles = []
        
        try:
            # Parse feed
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Check if matches query
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                
                if query not in title and query not in summary:
                    continue
                
                # Parse date
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_dt = datetime(*entry.published_parsed[:6])
                    
                    # Check date range
                    if start_date and pub_dt < start_date:
                        continue
                    if end_date and pub_dt > end_date:
                        continue
                    
                    published_at = pub_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Extract article data
                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', '').strip(),
                    'source_name': source_name,
                    'published_at': published_at,
                    'author': entry.get('author', None),
                    'language': 'en',  # Most feeds are English
                    'raw_text': entry.get('summary', None)
                }
                
                if article['url']:
                    articles.append(article)
        
        except Exception as e:
            logger.warning(f"Error parsing feed {feed_url}: {str(e)}")
        
        return articles
