"""
Example usage of News Ingestion Service.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion_service import ingest_news, NewsIngestor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic():
    """Basic usage example."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60 + "\n")
    
    result = ingest_news(
        topic_query="artificial intelligence",
        max_articles=20,
        output_path="output/ai_articles.json"
    )
    
    print(f"\nResults:")
    print(f"  Case ID: {result.case_id}")
    print(f"  Query: {result.query}")
    print(f"  Total Articles: {len(result.articles)}")
    print(f"  Generated At: {result.generated_at}")
    
    if result.articles:
        print(f"\nSample Article:")
        article = result.articles[0]
        print(f"  Title: {article.title}")
        print(f"  Source: {article.source_name}")
        print(f"  URL: {article.url}")
        print(f"  Published: {article.published_at}")
        print(f"  Author: {article.author or 'N/A'}")
        print(f"  Clean Text Length: {len(article.clean_text)} chars")


def example_with_date_range():
    """Usage with date range filtering."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Date Range Filtering")
    print("="*60 + "\n")
    
    result = ingest_news(
        topic_query="climate change",
        max_articles=30,
        start_date="2026-01-01",
        end_date="2026-02-03",
        output_path="output/climate_articles.json"
    )
    
    print(f"\nResults:")
    print(f"  Total Articles: {len(result.articles)}")
    print(f"  Date Range: 2026-01-01 to 2026-02-03")
    
    # Show date distribution
    if result.articles:
        dates = [a.published_at[:10] for a in result.articles if a.published_at]
        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        print(f"\nArticles by Date:")
        for date in sorted(date_counts.keys()):
            print(f"  {date}: {date_counts[date]} articles")


def example_advanced():
    """Advanced usage with custom processing."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Advanced Usage")
    print("="*60 + "\n")
    
    # Create ingestor instance for more control
    ingestor = NewsIngestor()
    
    # Fetch articles
    raw_articles = ingestor.fetch_articles(
        topic_query="renewable energy",
        max_articles=25,
        use_gdelt=True,
        use_rss=True,
        use_web_search=True
    )
    
    print(f"Fetched {len(raw_articles)} raw articles")
    
    # Process articles
    processed = ingestor.process_articles(raw_articles)
    print(f"Processed {len(processed)} articles")
    
    # Deduplicate
    unique = ingestor.deduplicate_articles(processed)
    print(f"After deduplication: {len(unique)} unique articles")
    
    # Save
    ingestor.save_to_json(unique, "renewable energy", "output/energy_articles.json")
    
    # Analyze sources
    if unique:
        sources = {}
        for article in unique:
            sources[article.source_name] = sources.get(article.source_name, 0) + 1
        
        print(f"\nArticles by Source:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")


def example_batch_processing():
    """Batch processing multiple topics."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing")
    print("="*60 + "\n")
    
    topics = [
        "quantum computing",
        "space exploration",
        "biotechnology"
    ]
    
    results = {}
    
    for topic in topics:
        print(f"\nProcessing topic: {topic}")
        result = ingest_news(
            topic_query=topic,
            max_articles=15,
            output_path=f"output/{topic.replace(' ', '_')}_articles.json"
        )
        results[topic] = len(result.articles)
    
    print("\n" + "-"*60)
    print("Batch Processing Summary:")
    print("-"*60)
    for topic, count in results.items():
        print(f"  {topic}: {count} articles")
    print(f"\nTotal: {sum(results.values())} articles across {len(topics)} topics")


def test_gdelt():
    """Test GDELT integration only."""
    print("\n" + "="*60)
    print("TEST: GDELT Integration")
    print("="*60 + "\n")
    
    ingestor = NewsIngestor()
    articles = ingestor.fetch_articles(
        topic_query="technology",
        max_articles=10,
        use_gdelt=True,
        use_rss=False,
        use_web_search=False
    )
    
    print(f"GDELT returned {len(articles)} articles")
    if articles:
        print(f"\nSample GDELT article:")
        print(f"  Title: {articles[0].get('title', 'N/A')}")
        print(f"  URL: {articles[0].get('url', 'N/A')}")


def test_rss():
    """Test RSS integration only."""
    print("\n" + "="*60)
    print("TEST: RSS Integration")
    print("="*60 + "\n")
    
    ingestor = NewsIngestor()
    articles = ingestor.fetch_articles(
        topic_query="technology",
        max_articles=10,
        use_gdelt=False,
        use_rss=True,
        use_web_search=False
    )
    
    print(f"RSS returned {len(articles)} articles")
    if articles:
        print(f"\nSample RSS article:")
        print(f"  Title: {articles[0].get('title', 'N/A')}")
        print(f"  Source: {articles[0].get('source_name', 'N/A')}")
        print(f"  URL: {articles[0].get('url', 'N/A')}")


def test_deduplication():
    """Test deduplication logic."""
    print("\n" + "="*60)
    print("TEST: Deduplication")
    print("="*60 + "\n")
    
    from ingestion_service.deduplicator import DuplicateResolver
    from ingestion_service.schema import Article
    from ingestion_service.utils import get_current_iso_time
    
    # Create test articles with duplicates
    test_articles = [
        Article(
            article_id="1",
            title="Climate Change Impact on Agriculture",
            source_name="Source A",
            url="https://example.com/article1",
            published_at=get_current_iso_time(),
            clean_text="Climate change is affecting agriculture worldwide.",
            language="en"
        ),
        Article(
            article_id="2",
            title="Climate Change Impact on Agriculture",  # Exact duplicate title
            source_name="Source B",
            url="https://example.com/article2",
            published_at=get_current_iso_time(),
            clean_text="Climate change is affecting agriculture worldwide. More details here.",
            language="en"
        ),
        Article(
            article_id="3",
            title="Climate Change Impacts Agricultural Production",  # Near duplicate
            source_name="Source C",
            url="https://example.com/article3",
            published_at=get_current_iso_time(),
            clean_text="Similar content about climate and agriculture.",
            language="en"
        ),
        Article(
            article_id="4",
            title="Renewable Energy Sources Growing Rapidly",  # Different topic
            source_name="Source D",
            url="https://example.com/article4",
            published_at=get_current_iso_time(),
            clean_text="Renewable energy is expanding.",
            language="en"
        ),
    ]
    
    print(f"Original articles: {len(test_articles)}")
    
    deduplicator = DuplicateResolver()
    unique = deduplicator.deduplicate([a.model_dump() for a in test_articles])
    
    print(f"After deduplication: {len(unique)}")
    print(f"\nUnique articles:")
    for article in unique:
        print(f"  - {article['title'][:50]}...")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="News Ingestion Service Examples")
    parser.add_argument("--test-gdelt", action="store_true", help="Test GDELT integration")
    parser.add_argument("--test-rss", action="store_true", help="Test RSS integration")
    parser.add_argument("--test-dedup", action="store_true", help="Test deduplication")
    parser.add_argument("--topic", type=str, help="Run with specific topic")
    parser.add_argument("--max-articles", type=int, default=20, help="Max articles to fetch")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD format)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD format)")
    parser.add_argument("--use-mock", action="store_true", help="Use mock data instead of real APIs (for testing)")
    
    args = parser.parse_args()
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    if args.test_gdelt:
        test_gdelt()
    elif args.test_rss:
        test_rss()
    elif args.test_dedup:
        test_deduplication()
    elif args.topic:
        # Run with custom topic
        print(f"\nFetching articles for: {args.topic}")
        if args.use_mock:
            print("  [Using MOCK data for testing]")
        if args.start_date or args.end_date:
            print(f"Date range: {args.start_date or 'any'} to {args.end_date or 'any'}")
        result = ingest_news(
            args.topic, 
            args.max_articles, 
            start_date=args.start_date,
            end_date=args.end_date,
            output_path=f"output/{args.topic.replace(' ', '_')}.json",
            use_mock=args.use_mock
        )
        print(f"Fetched {len(result.articles)} articles")
    else:
        # Run all examples
        example_basic()
        example_with_date_range()
        example_advanced()
        example_batch_processing()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60 + "\n")
