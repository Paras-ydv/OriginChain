"""
Configuration constants for News Ingestion Service.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Web Search Configuration
WEB_SEARCH_ENGINES = {
    "duckduckgo": "https://duckduckgo.com/html/",
    "bing": "https://www.bing.com/search"
}
WEB_SEARCH_MAX_RESULTS = 20  # Top 20 relevant sites
WEB_SEARCH_TIMEOUT = 10  # seconds

# NewsAPI Configuration (https://newsapi.org)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_BASE_URL = "https://newsapi.org/v2"
NEWSAPI_MAX_ARTICLES = 20  # Free tier limit per request

# GNews API Configuration (https://gnews.io)
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
GNEWS_BASE_URL = "https://gnews.io/api/v4"
GNEWS_MAX_ARTICLES = 10  # Free tier limit per request

# Translation Configuration
TRANSLATION_ENABLED = True
TARGET_LANGUAGE = "en"

# RSS Feed URLs for major publishers
RSS_FEEDS = {
    # International News
    "BBC": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
    ],
    "Reuters": [
        "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    ],
    "CNN": [
        "http://rss.cnn.com/rss/edition.rss",
        "http://rss.cnn.com/rss/edition_world.rss",
    ],
    "The Guardian": [
        "https://www.theguardian.com/world/rss",
        "https://www.theguardian.com/uk/technology/rss",
    ],
    "Al Jazeera": [
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
    "NPR": [
        "https://feeds.npr.org/1001/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",
    ],
    # Indian News Sources
    "Economic Times": [
        "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/1124.cms",
    ],
    "LiveMint": [
        "https://www.livemint.com/rss/news",
        "https://www.livemint.com/rss/politics",
    ],
    "Times of India": [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    ],
    "The Hindu": [
        "https://www.thehindu.com/news/national/?service=rss",
    ],
}

# GDELT API Configuration
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_MODE = "artlist"  # Article list mode
GDELT_FORMAT = "json"
GDELT_MAX_RECORDS = 250  # GDELT max per request

# Deduplication thresholds
COSINE_SIMILARITY_THRESHOLD = 0.85  # TF-IDF similarity threshold for near-duplicates
FUZZY_MATCH_THRESHOLD = 90  # Fuzzy string match threshold (0-100)

# HTTP Request Configuration
REQUEST_TIMEOUT = 15  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
USER_AGENT = "OriginChain News Ingestion Service/1.0 (Educational Project)"

# Content Extraction
MIN_ARTICLE_LENGTH = 100  # Minimum characters for clean_text to be considered valid
MAX_ARTICLE_LENGTH = 50000  # Maximum characters to extract

# Default Parameters
DEFAULT_MAX_ARTICLES = 100
DEFAULT_LANGUAGE = "en"

# Date Format
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
