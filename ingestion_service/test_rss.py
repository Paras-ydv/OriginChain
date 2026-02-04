"""Quick test to diagnose RSS fetching issues."""
import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test a few RSS feeds
test_feeds = [
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("CNN", "http://rss.cnn.com/rss/edition.rss"),
]

print("Testing RSS feeds...\n")

for name, url in test_feeds:
    print(f"Testing {name}: {url}")
    try:
        feed = feedparser.parse(url)
        
        if hasattr(feed, 'bozo_exception'):
            print(f"  ⚠ Feed parsing error: {feed.bozo_exception}")
        
        num_entries = len(feed.entries) if hasattr(feed, 'entries') else 0
        print(f"  ✓ Found {num_entries} entries")
        
        if num_entries > 0:
            entry = feed.entries[0]
            print(f"  Sample title: {entry.get('title', 'N/A')[:80]}")
            print(f"  Sample link: {entry.get('link', 'N/A')[:80]}")
        
        print()
    except Exception as e:
        print(f"  ✗ Error: {e}\n")

print("Testing 'technology' keyword search in BBC Tech feed...")
feed = feedparser.parse("http://feeds.bbci.co.uk/news/technology/rss.xml")
query = "technology"

matches = 0
for entry in feed.entries[:10]:
    title = entry.get('title', '').lower()
    summary = entry.get('summary', '').lower()
    
    if query in title or query in summary:
        matches += 1
        print(f"  ✓ Match: {entry.get('title', 'N/A')[:80]}")

print(f"\nTotal matches for '{query}': {matches}/{len(feed.entries[:10])}")
