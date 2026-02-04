"""
News Ingestion Service package.
"""

from .ingestor import NewsIngestor, ingest_news
from .schema import Article, ArticlesOutput

__version__ = "1.0.0"
__all__ = ['NewsIngestor', 'ingest_news', 'Article', 'ArticlesOutput']
