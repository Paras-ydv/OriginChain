"""
Main News Ingestion Module for OriginChain.
Fetches, normalizes, and deduplicates news articles from multiple sources.
"""

import json
import logging
from typing import List, Dict, Optional, Any
import requests
from bs4 import BeautifulSoup

from schema import Article, ArticlesOutput
from sources import GDELTClient, RSSFeedClient, WebSearchClient
from deduplicator import DuplicateResolver
from mock_source import MockNewsSource
from utils import (
    clean_html, normalize_url, parse_date, get_current_iso_time,
    generate_article_id, generate_case_id, is_valid_article_text
)
from config import REQUEST_TIMEOUT, USER_AGENT, DEFAULT_MAX_ARTICLES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsIngestor:
    """Main news ingestion class."""
    
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.gdelt_client = GDELTClient()
        self.rss_client = RSSFeedClient()
        self.web_search_client = WebSearchClient()
        self.mock_client = MockNewsSource()
        self.deduplicator = DuplicateResolver()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def fetch_articles(
        self,
        topic_query: str,
        max_articles: int = DEFAULT_MAX_ARTICLES,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_gdelt: bool = False,  # Disabled by default (rate limited)
        use_rss: bool = False,    # Disabled by default (not finding articles)
        use_web_search: bool = True  # Only web search enabled
    ) -> List[Dict[str, Any]]:
        """
        Fetch articles from all sources.
        
        Args:
            topic_query: Search query/topic
            max_articles: Maximum number of articles to fetch
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            use_gdelt: Whether to use GDELT API
            use_rss: Whether to use RSS feeds
            use_web_search: Whether to use web search
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        
        # Use mock data if enabled
        if self.use_mock:
            logger.info(f"Using MOCK data source for query='{topic_query}'")
            return self.mock_client.search(topic_query, max_articles, start_date, end_date)
        
        # Calculate how many to fetch from each source
        active_sources = int(use_gdelt) + int(use_rss) + int(use_web_search)
        per_source = max_articles // active_sources if active_sources > 0 else 0
        
        # Fetch from RSS first (most reliable)
        if use_rss:
            try:
                logger.info(f"Fetching from RSS: query='{topic_query}'")
                rss_articles = self.rss_client.search(
                    topic_query, per_source, start_date, end_date
                )
                all_articles.extend(rss_articles)
            except Exception as e:
                logger.error(f"RSS fetch failed: {str(e)}")
        
        # Fetch from GDELT
        if use_gdelt:
            try:
                logger.info(f"Fetching from GDELT: query='{topic_query}'")
                gdelt_articles = self.gdelt_client.search(
                    topic_query, per_source, start_date, end_date
                )
                all_articles.extend(gdelt_articles)
            except Exception as e:
                logger.error(f"GDELT fetch failed: {str(e)}")
        
        # Fetch from web search
        if use_web_search:
            try:
                logger.info(f"Fetching from web search: query='{topic_query}'")
                web_articles = self.web_search_client.search(
                    topic_query, per_source  # Use per_source instead of hardcoded 20
                )
                all_articles.extend(web_articles)
            except Exception as e:
                logger.error(f"Web search failed: {str(e)}")
        
        # Fallback to mock data if no articles fetched
        if len(all_articles) == 0:
            logger.warning("No articles fetched from external sources, falling back to mock data")
            all_articles = self.mock_client.search(topic_query, max_articles, start_date, end_date)
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch full article content from URL.
        
        Args:
            url: Article URL
            
        Returns:
            HTML content or None if failed
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.debug(f"Failed to fetch content from {url}: {str(e)}")
            return None
    
    def extract_metadata(self, html_content: str, url: str) -> Dict[str, Optional[str]]:
        """
        Extract metadata from HTML content.
        
        Args:
            html_content: Raw HTML
            url: Article URL for fallback
            
        Returns:
            Dictionary with metadata fields
        """
        metadata = {
            'author': None,
            'published_at': None,
        }
        
        if not html_content:
            return metadata
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to extract author
            author_meta = soup.find('meta', attrs={'name': 'author'}) or \
                         soup.find('meta', attrs={'property': 'article:author'})
            if author_meta and author_meta.get('content'):
                metadata['author'] = author_meta['content']
            
            # Try article tag
            if not metadata['author']:
                author_tag = soup.find('span', class_='author') or \
                            soup.find('a', rel='author') or \
                            soup.find(class_='author-name')
                if author_tag:
                    metadata['author'] = author_tag.get_text().strip()
            
            # Try to extract publication date
            date_meta = soup.find('meta', attrs={'property': 'article:published_time'}) or \
                       soup.find('meta', attrs={'name': 'publishdate'}) or \
                       soup.find('meta', attrs={'name': 'date'})
            if date_meta and date_meta.get('content'):
                metadata['published_at'] = parse_date(date_meta['content'])
            
            # Try time tag
            if not metadata['published_at']:
                time_tag = soup.find('time', attrs={'datetime': True})
                if time_tag:
                    metadata['published_at'] = parse_date(time_tag['datetime'])
        
        except Exception as e:
            logger.debug(f"Metadata extraction failed for {url}: {str(e)}")
        
        return metadata
    
    def process_articles(self, raw_articles: List[Dict]) -> List[Article]:
        """
        Process raw articles: fetch content, clean, extract metadata.
        
        Args:
            raw_articles: List of raw article dictionaries
            
        Returns:
            List of processed Article objects
        """
        processed = []
        
        for idx, raw_article in enumerate(raw_articles):
            try:
                url = raw_article.get('url', '')
                if not url:
                    continue
                
                logger.debug(f"Processing article {idx + 1}/{len(raw_articles)}: {url}")
                
                # Fetch article content if not already available
                raw_text = raw_article.get('raw_text')
                if not raw_text:
                    raw_text = self.fetch_article_content(url)
                
                # Extract clean text
                clean_text = clean_html(raw_text) if raw_text else ""
                
                # Skip if no valid content
                if not is_valid_article_text(clean_text):
                    logger.debug(f"Skipping article with insufficient content: {url}")
                    continue
                
                # Extract additional metadata from HTML
                metadata = self.extract_metadata(raw_text, url)
                
                # Merge with existing metadata (prefer existing)
                author = raw_article.get('author') or metadata.get('author')
                published_at = raw_article.get('published_at') or metadata.get('published_at')
                
                # Generate article ID
                article_id = generate_article_id(url, raw_article.get('title', ''))
                
                # Create Article object
                article = Article(
                    article_id=article_id,
                    title=raw_article.get('title', 'Untitled'),
                    source_name=raw_article.get('source_name', 'Unknown'),
                    url=normalize_url(url),
                    published_at=published_at or get_current_iso_time(),
                    author=author,
                    language=raw_article.get('language', 'en'),
                    clean_text=clean_text,
                    raw_text=raw_text[:10000] if raw_text else None  # Truncate raw text
                )
                
                processed.append(article)
            
            except Exception as e:
                logger.warning(f"Failed to process article: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(processed)}/{len(raw_articles)} articles")
        return processed
    
    def deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """
        Deduplicate articles.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Deduplicated list
        """
        # Convert to dicts for deduplicator
        article_dicts = [article.model_dump() for article in articles]
        
        # Run deduplication
        unique_dicts = self.deduplicator.deduplicate(article_dicts)
        
        # Convert back to Article objects
        unique_articles = [Article(**d) for d in unique_dicts]
        
        return unique_articles
    
    def save_to_json(
        self,
        articles: List[Article],
        query: str,
        output_path: str
    ) -> None:
        """
        Save articles to JSON file following schema.
        
        Args:
            articles: List of Article objects
            query: Original search query
            output_path: Path to save JSON file
        """
        # Generate metadata
        generated_at = get_current_iso_time()
        case_id = generate_case_id(query, generated_at)
        
        # Create output object
        output = ArticlesOutput(
            case_id=case_id,
            query=query,
            generated_at=generated_at,
            articles=articles
        )
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(articles)} articles to {output_path}")
    
    def ingest(
        self,
        topic_query: str,
        max_articles: int = DEFAULT_MAX_ARTICLES,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_path: str = "articles.json"
    ) -> ArticlesOutput:
        """
        Complete ingestion pipeline.
        
        Args:
            topic_query: Search query/topic
            max_articles: Maximum number of articles
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_path: Path to save output JSON
            
        Returns:
            ArticlesOutput object
        """
        logger.info(f"Starting ingestion for query: '{topic_query}'")
        
        # Step 1: Fetch raw articles
        raw_articles = self.fetch_articles(
            topic_query, max_articles, start_date, end_date
        )
        
        if not raw_articles:
            logger.warning("No articles fetched")
            return ArticlesOutput(
                case_id=generate_case_id(topic_query, get_current_iso_time()),
                query=topic_query,
                generated_at=get_current_iso_time(),
                articles=[]
            )
        
        # Step 2: Process articles (fetch content, clean, extract metadata)
        processed_articles = self.process_articles(raw_articles)
        
        if not processed_articles:
            logger.warning("No articles processed successfully")
            return ArticlesOutput(
                case_id=generate_case_id(topic_query, get_current_iso_time()),
                query=topic_query,
                generated_at=get_current_iso_time(),
                articles=[]
            )
        
        # Step 3: Deduplicate
        unique_articles = self.deduplicate_articles(processed_articles)
        
        # Step 4: Save to JSON
        self.save_to_json(unique_articles, topic_query, output_path)
        
        logger.info(f"Ingestion complete: {len(unique_articles)} unique articles")
        
        # Return output object
        return ArticlesOutput(
            case_id=generate_case_id(topic_query, get_current_iso_time()),
            query=topic_query,
            generated_at=get_current_iso_time(),
            articles=unique_articles
        )


def ingest_news(
    topic_query: str,
    max_articles: int = DEFAULT_MAX_ARTICLES,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_path: str = "articles.json",
    use_mock: bool = False
) -> ArticlesOutput:
    """
    Convenience function to run news ingestion.
    
    Args:
        topic_query: Search query/topic
        max_articles: Maximum number of articles to fetch
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        output_path: Path to save output JSON
        use_mock: Use mock data source instead of real APIs (for testing)
        
    Returns:
        ArticlesOutput object with fetched articles
    
    Example:
        >>> result = ingest_news("climate change", max_articles=50)
        >>> print(f"Fetched {len(result.articles)} articles")
    """
    ingestor = NewsIngestor(use_mock=use_mock)
    return ingestor.ingest(topic_query, max_articles, start_date, end_date, output_path)
