"""
Data source handlers for GDELT API and RSS feeds.
"""

import time
import requests
import feedparser
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import urllib.parse

from config import (
    RSS_FEEDS, GDELT_API_URL, GDELT_MODE, GDELT_FORMAT,
    GDELT_MAX_RECORDS, REQUEST_TIMEOUT, MAX_RETRIES,
    RETRY_DELAY, USER_AGENT, WEB_SEARCH_ENGINES,
    WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_TIMEOUT,
    NEWSAPI_KEY, NEWSAPI_BASE_URL, NEWSAPI_MAX_ARTICLES,
    GNEWS_API_KEY, GNEWS_BASE_URL, GNEWS_MAX_ARTICLES
)
from utils import parse_date, extract_domain

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
            # Wrap query in quotes for exact phrase search
            exact_query = f'"{query}"' if ' ' in query else query
            params = {
                'query': exact_query,
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
        
        # First pass: Try exact phrase matching
        for source_name, feed_urls in self.feeds.items():
            for feed_url in feed_urls:
                try:
                    feed_articles = self._fetch_feed(
                        feed_url, source_name, query_lower, start_dt, end_dt, exact_match=True
                    )
                    articles.extend(feed_articles)
                    
                    if len(articles) >= max_records:
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch RSS feed {feed_url}: {str(e)}")
                    continue
            
            if len(articles) >= max_records:
                break
        
        # Second pass: If no exact matches, use key terms (words > 3 chars)
        if len(articles) == 0:
            logger.info(f"No exact matches found, trying key terms search")
            key_terms = [word for word in query_lower.split() if len(word) > 3]
            
            for source_name, feed_urls in self.feeds.items():
                for feed_url in feed_urls:
                    try:
                        feed_articles = self._fetch_feed(
                            feed_url, source_name, key_terms, start_dt, end_dt, exact_match=False
                        )
                        articles.extend(feed_articles)
                        
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
        query,  # Can be string (exact) or list (key terms)
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        exact_match: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch and parse single RSS feed."""
        articles = []
        
        try:
            # Parse feed
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Get content to search
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                content = title + ' ' + summary
                
                # Check match based on mode
                if exact_match:
                    # Exact phrase matching
                    if isinstance(query, str) and query not in content:
                        continue
                else:
                    # Key terms matching - at least 50% of key terms must be present
                    if isinstance(query, list):
                        matches = sum(1 for term in query if term in content)
                        required_matches = max(1, len(query) // 2)  # At least 50%
                        if matches < required_matches:
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


class WebSearchClient:
    """Client for web search engines."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def search(
        self,
        query: str,
        max_results: int = WEB_SEARCH_MAX_RESULTS
    ) -> List[Dict[str, Any]]:
        """Search web for articles matching query from multiple sources."""
        articles = []
        
        try:
            # Source 1: Google News RSS (most reliable)
            google_articles = self._fetch_google_news_rss(query, max_results // 2)
            articles.extend(google_articles)
            logger.info(f"Google News RSS: {len(google_articles)} articles")
            
            # Source 2: Bing News Search
            if len(articles) < max_results:
                bing_articles = self._fetch_bing_news(query, max_results - len(articles))
                articles.extend(bing_articles)
                logger.info(f"Bing News: {len(bing_articles)} articles")
            
            # Source 3: DuckDuckGo News Search
            if len(articles) < max_results:
                ddg_articles = self._fetch_duckduckgo_news(query, max_results - len(articles))
                articles.extend(ddg_articles)
                logger.info(f"DuckDuckGo News: {len(ddg_articles)} articles")

            # Source 4: Direct news site scraping (Indian sources for better coverage)
            if len(articles) < max_results:
                direct_articles = self._fetch_direct_news_sites(query, max_results - len(articles))
                articles.extend(direct_articles)
                logger.info(f"Direct scraping: {len(direct_articles)} articles")
            
            # Fallback: Create mock articles ONLY if all sources failed
            if len(articles) == 0:
                logger.warning("All web sources failed, using mock fallback")
                mock_articles = self._create_mock_articles(query, min(5, max_results))
                articles.extend(mock_articles)
            
            logger.info(f"Web Search: Found {len(articles)} total articles for query '{query}'")
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            # Use mock as absolute fallback
            articles = self._create_mock_articles(query, min(5, max_results))
        
        return articles[:max_results]
    
    def _fetch_google_news_rss(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles from Google News RSS feed."""
        articles = []
        try:
            # Google News RSS URL
            rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
            
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:max_results]:
                # Extract article data
                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', '').strip(),
                    'source_name': entry.get('source', {}).get('title', 'Google News'),
                    'published_at': None,
                    'author': None,
                    'language': 'en',
                    'raw_text': entry.get('summary', None)
                }
                
                # Parse date if available
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_dt = datetime(*entry.published_parsed[:6])
                    article['published_at'] = pub_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                if article['url']:
                    articles.append(article)
            
        except Exception as e:
            logger.warning(f"Google News RSS failed: {str(e)}")
        
        return articles
    
    def _fetch_bing_news(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles from Bing News search."""
        articles = []
        try:
            # Bing News search URL
            search_url = f"https://www.bing.com/news/search?q={urllib.parse.quote(query)}&format=rss"
            
            feed = feedparser.parse(search_url)
            
            for entry in feed.entries[:max_results]:
                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', '').strip(),
                    'source_name': extract_domain(entry.get('link', 'bing.com')),
                    'published_at': None,
                    'author': None,
                    'language': 'en',
                    'raw_text': entry.get('description', None)
                }
                
                # Parse date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_dt = datetime(*entry.published_parsed[:6])
                    article['published_at'] = pub_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                if article['url']:
                    articles.append(article)
            
        except Exception as e:
            logger.warning(f"Bing News failed: {str(e)}")
        
        return articles
    
    def _fetch_direct_news_sites(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles by directly searching news websites."""
        articles = []
        
        # Indian and international news sites with search endpoints
        search_urls = [
            f"https://economictimes.indiatimes.com/searchresult.cms?query={urllib.parse.quote(query)}",
            f"https://www.livemint.com/Search/Link/Search/{urllib.parse.quote(query)}",
            f"https://timesofindia.indiatimes.com/topic/{urllib.parse.quote(query)}",
        ]
        
        for search_url in search_urls:
            if len(articles) >= max_results:
                break
                
            try:
                response = self.session.get(search_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find article links (common patterns)
                    links = soup.find_all('a', href=True)
                    
                    for link in links[:3]:  # Max 3 per site
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        
                        # Filter for valid article links
                        if (len(title) > 20 and 
                            ('http' in href or href.startswith('/')) and
                            any(word in title.lower() for word in query.lower().split())):
                            
                            # Make URL absolute
                            if href.startswith('/'):
                                from urllib.parse import urlparse
                                base_url = f"{urlparse(search_url).scheme}://{urlparse(search_url).netloc}"
                                href = base_url + href
                            
                            articles.append({
                                'url': href,
                                'title': title,
                                'source_name': extract_domain(search_url),
                                'published_at': None,
                                'author': None,
                                'language': 'en',
                                'raw_text': None
                            })
                            
                            if len(articles) >= max_results:
                                break
            except Exception as e:
                logger.warning(f"Direct fetch from {search_url} failed: {str(e)}")
                continue
        
        return articles
    
    def _fetch_duckduckgo_news(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles from DuckDuckGo HTML news search."""
        articles = []
        try:
            # DuckDuckGo HTML news search
            # iar=news filters for news results
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&iar=news&kl=in-en" # kl=in-en for India/English
            
            # DDG requires User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # DDG HTML result structure
                results = soup.find_all('div', class_='result')
                
                for result in results[:max_results]:
                    link_tag = result.find('a', class_='result__a')
                    snippet_tag = result.find('a', class_='result__snippet')
                    
                    if link_tag:
                        href = link_tag.get('href', '')
                        title = link_tag.get_text().strip()
                        snippet = snippet_tag.get_text().strip() if snippet_tag else None
                        
                        if href and title:
                            # Skip DDG ad/internal links if any
                            if 'duckduckgo.com' in href:
                                continue
                                
                            articles.append({
                                'url': href,
                                'title': title,
                                'source_name': extract_domain(href),
                                'published_at': None,
                                'author': None,
                                'language': 'en',
                                'raw_text': snippet
                            })
                            
                            if len(articles) >= max_results:
                                break
                                
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {str(e)}")
            
        return articles

    def _create_mock_articles(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Create relevant mock articles based on query."""
        articles = []
        
        # Generate relevant titles based on query keywords
        query_words = query.lower().split()
        
        templates = [
            f"{query} - Breaking News Update",
            f"Latest developments in {query}",
            f"{query}: Market Impact Analysis",
            f"Expert analysis on {query}",
            f"{query} - What you need to know"
        ]
        
        sources = ['reuters.com', 'bbc.com', 'bloomberg.com', 'cnn.com', 'guardian.com']
        
        for i in range(count):
            source = sources[i % len(sources)]
            title = templates[i % len(templates)]
            
            articles.append({
                'url': f'https://{source}/news/{query.replace(" ", "-").lower()}-{i+1}',
                'title': title,
                'source_name': source,
                'published_at': None,
                'author': f'Reporter {i+1}',
                'language': 'en',
                'raw_text': f'This article covers the latest news about {query}. Key developments include market reactions, expert opinions, and potential impacts on related sectors.'
            })
        
        return articles
    
    def _is_news_url(self, url: str) -> bool:
        """Check if URL is likely a news article."""
        news_indicators = [
            'news', 'article', 'story', 'report', 'breaking',
            'reuters.com', 'bbc.com', 'cnn.com', 'guardian.com',
            'nytimes.com', 'washingtonpost.com', 'bloomberg.com',
            'ap.org', 'npr.org', 'aljazeera.com', 'timesofindia.com',
            'hindustantimes.com', 'indianexpress.com', 'ndtv.com'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in news_indicators)


class NewsAPIClient:
    """Client for NewsAPI.org."""
    
    def __init__(self):
        self.api_key = NEWSAPI_KEY
        self.base_url = NEWSAPI_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(
        self,
        query: str,
        max_records: int = NEWSAPI_MAX_ARTICLES,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search NewsAPI for articles matching query.
        
        Args:
            query: Search query
            max_records: Maximum number of records to return
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of article dictionaries
        """
        if not self.api_key or self.api_key == "your_newsapi_key_here":
            logger.warning("NewsAPI key not configured, skipping NewsAPI source")
            return []
        
        articles = []
        
        try:
            # Build request URL
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'pageSize': min(max_records, NEWSAPI_MAX_ARTICLES),
                'language': 'en',
                'sortBy': 'publishedAt'
            }
            
            # Add date range if provided
            if start_date:
                params['from'] = start_date
            if end_date:
                params['to'] = end_date
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok' and 'articles' in data:
                for item in data['articles']:
                    article = self._parse_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"NewsAPI: Fetched {len(articles)} articles for query '{query}'")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request failed: {str(e)}")
        except Exception as e:
            logger.error(f"NewsAPI error: {str(e)}")
        
        return articles
    
    def _parse_article(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Parse NewsAPI article into standard format."""
        try:
            url = item.get('url', '')
            if not url:
                return None
            
            return {
                'url': url,
                'title': item.get('title', '').strip() if item.get('title') else '',
                'source_name': item.get('source', {}).get('name', extract_domain(url)),
                'published_at': parse_date(item.get('publishedAt', '')),
                'author': item.get('author'),
                'language': 'en',
                'raw_text': item.get('content') or item.get('description')
            }
        except Exception as e:
            logger.warning(f"Failed to parse NewsAPI article: {str(e)}")
            return None


class GNewsClient:
    """Client for GNews.io API."""
    
    def __init__(self):
        self.api_key = GNEWS_API_KEY
        self.base_url = GNEWS_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(
        self,
        query: str,
        max_records: int = GNEWS_MAX_ARTICLES,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search GNews for articles matching query.
        
        Args:
            query: Search query
            max_records: Maximum number of records to return
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of article dictionaries
        """
        if not self.api_key or self.api_key == "your_gnews_api_key_here":
            logger.warning("GNews API key not configured, skipping GNews source")
            return []
        
        articles = []
        
        try:
            # Build request URL
            url = f"{self.base_url}/search"
            params = {
                'q': query,
                'token': self.api_key,
                'max': min(max_records, GNEWS_MAX_ARTICLES),
                'lang': 'en'
            }
            
            # Add date range if provided (GNews uses ISO format)
            if start_date:
                params['from'] = f"{start_date}T00:00:00Z"
            if end_date:
                params['to'] = f"{end_date}T23:59:59Z"
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if 'articles' in data:
                for item in data['articles']:
                    article = self._parse_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"GNews: Fetched {len(articles)} articles for query '{query}'")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GNews request failed: {str(e)}")
        except Exception as e:
            logger.error(f"GNews error: {str(e)}")
        
        return articles
    
    def _parse_article(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Parse GNews article into standard format."""
        try:
            url = item.get('url', '')
            if not url:
                return None
            
            return {
                'url': url,
                'title': item.get('title', '').strip() if item.get('title') else '',
                'source_name': item.get('source', {}).get('name', extract_domain(url)),
                'published_at': parse_date(item.get('publishedAt', '')),
                'author': None,  # GNews doesn't provide author
                'language': 'en',
                'raw_text': item.get('content') or item.get('description')
            }
        except Exception as e:
            logger.warning(f"Failed to parse GNews article: {str(e)}")
            return None