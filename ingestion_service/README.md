# News Ingestion Service

A Python-based microservice for the **OriginChain** project that fetches, normalizes, and deduplicates news articles from free sources (GDELT API and RSS feeds).

## Features

✅ **Multi-Source Ingestion**: Fetches articles from GDELT API and RSS feeds (BBC, Reuters, CNN, The Guardian, Al Jazeera, NPR)  
✅ **Smart Deduplication**: Two-tier approach with exact (URL) and near-duplicate (TF-IDF + fuzzy matching) detection  
✅ **Content Extraction**: Automatic HTML cleaning and plain text extraction  
✅ **Metadata Enrichment**: Extracts author, publication date, and source information  
✅ **Schema Validation**: Strict adherence to `articles.json` contract using Pydantic  
✅ **Retry Logic**: Robust error handling with automatic retries  

```

## Quick Start & Testing

### Step 1: Navigate to Project Directory

```bash
cd c:\Users\LENOVO\shivansh\OriginChain\ingestion_service
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Tests

#### Test 1: Deduplication Logic
```bash
python example_usage.py --test-dedup
```
**Expected**: Should show deduplication working on test articles.

#### Test 2: RSS Feed Integration
```bash
python example_usage.py --test-rss
```
**Expected**: Should fetch articles from BBC, Reuters, CNN, etc.

#### Test 3: GDELT Integration
```bash
python example_usage.py --test-gdelt
```
**Expected**: Should fetch articles from GDELT API.

### Step 4: Fetch Real Articles

#### Simple Topic Query
```bash
python example_usage.py --topic "electric vehicles" --max-articles 15
```

#### Complex Multi-word Query
```bash
python example_usage.py --topic "India union budget 2026" --max-articles 20
```

#### Other Example Topics
```bash
# Technology
python example_usage.py --topic "artificial intelligence" --max-articles 20

# Science
python example_usage.py --topic "space exploration" --max-articles 15

# Current Events
python example_usage.py --topic "climate summit 2026" --max-articles 20

# Business
python example_usage.py --topic "cryptocurrency market trends" --max-articles 15
```

### Step 5: Check Output

All results are saved to the `output/` folder:
```bash
# View generated files
dir output\

# Or on Mac/Linux
ls output/
```

**Output files will be named**: `output/<topic_name>.json`

### What to Expect

✅ **Console Output:**
- Real-time progress logs
- Article fetching from GDELT + RSS
- Processing and deduplication statistics
- Final count of unique articles

✅ **JSON Output:**
- Strict schema compliance
- Multi-language support (English, Korean, Turkish, etc.)
- Rich metadata (title, author, date, source)
- Clean text extraction from HTML

### Quick Verification

View a sample output:
```bash
# Open in browser or text editor
start output\electric_vehicles.json
```

The JSON will contain:
- `case_id`: Unique identifier
- `query`: Your search query
- `generated_at`: ISO timestamp
- `articles[]`: Array of fetched articles with full metadata

---

## Usage Examples


### Basic Usage

```python
from ingestion_service import ingest_news

# Fetch articles about a topic
result = ingest_news(
    topic_query="climate change",
    max_articles=50,
    output_path="articles.json"
)

print(f"Fetched {len(result.articles)} articles")
```

### With Date Range

```python
result = ingest_news(
    topic_query="artificial intelligence",
    max_articles=30,
    start_date="2026-01-01",
    end_date="2026-02-03",
    output_path="ai_articles.json"
)
```

### Advanced Usage

```python
from ingestion_service import NewsIngestor

ingestor = NewsIngestor()

# Fetch from specific sources
raw_articles = ingestor.fetch_articles(
    topic_query="renewable energy",
    max_articles=25,
    use_gdelt=True,
    use_rss=True
)

# Process and deduplicate
processed = ingestor.process_articles(raw_articles)
unique = ingestor.deduplicate_articles(processed)

# Save to JSON
ingestor.save_to_json(unique, "renewable energy", "output.json")
```

## API Reference

### `ingest_news()`

Convenience function to run the complete ingestion pipeline.

**Parameters:**
- `topic_query` (str): Search query/topic
- `max_articles` (int): Maximum number of articles to fetch (default: 100)
- `start_date` (str, optional): Start date in `YYYY-MM-DD` format
- `end_date` (str, optional): End date in `YYYY-MM-DD` format
- `output_path` (str): Path to save output JSON (default: "articles.json")

**Returns:**
- `ArticlesOutput`: Object containing case metadata and list of articles

### `NewsIngestor` Class

Main ingestion class with granular control.

**Methods:**

#### `fetch_articles()`
Fetch articles from all configured sources.

#### `process_articles()`
Process raw articles: fetch content, clean HTML, extract metadata.

#### `deduplicate_articles()`
Remove exact and near-duplicate articles.

#### `save_to_json()`
Save articles to JSON file following schema.

#### `ingest()`
Run complete pipeline: fetch → process → deduplicate → save.

## Output Schema

The service outputs JSON conforming to the OriginChain `articles.json` schema:

```json
{
  "case_id": "case_abc123",
  "query": "climate change",
  "generated_at": "2026-02-03T10:04:05Z",
  "articles": [
    {
      "article_id": "art_xyz789",
      "title": "Climate Change Impact on Agriculture",
      "source_name": "BBC News",
      "url": "https://example.com/article",
      "published_at": "2026-02-01T12:00:00Z",
      "author": "John Doe",
      "language": "en",
      "clean_text": "Article content here...",
      "raw_text": "<html>...</html>"
    }
  ]
}
```

## Configuration

Edit `config.py` to customize:

- **RSS Feeds**: Add/remove RSS feed URLs
- **Deduplication Thresholds**: 
  - `COSINE_SIMILARITY_THRESHOLD` (default: 0.85)
  - `FUZZY_MATCH_THRESHOLD` (default: 90)
- **Request Settings**: Timeout, retries, user agent
- **Content Limits**: Min/max article length

## Examples

Run the example file to see various usage patterns:

```bash
# Run all examples
python example_usage.py

# Test GDELT integration
python example_usage.py --test-gdelt

# Test RSS integration
python example_usage.py --test-rss

# Test deduplication
python example_usage.py --test-dedup

# Fetch specific topic
python example_usage.py --topic "quantum computing" --max-articles 30
```

## Architecture

```
ingestion_service/
├── __init__.py          # Package initialization
├── ingestor.py          # Main ingestion pipeline
├── sources.py           # GDELT & RSS clients
├── deduplicator.py      # Deduplication logic
├── schema.py            # Pydantic models
├── utils.py             # Utility functions
├── config.py            # Configuration constants
├── requirements.txt     # Dependencies
├── example_usage.py     # Usage examples
└── README.md           # This file
```

## Deduplication Strategy

### Exact Duplicates
- **Method**: URL normalization and matching
- **Removes**: Same article from different sources

### Near Duplicates
- **Method 1**: TF-IDF cosine similarity on article titles
- **Method 2**: Fuzzy string matching (Levenshtein distance)
- **Threshold**: Articles with >85% similarity or >90% fuzzy match score
- **Resolution**: Keeps article with longest `clean_text` and most metadata

## Logging

The service uses Python's built-in logging. Configure verbosity:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Show all logs
```

## Error Handling

The service handles common errors gracefully:

- **Network failures**: Automatic retries with exponential backoff
- **Paywalled content**: Skips articles that can't be accessed
- **Malformed HTML**: Falls back to basic text extraction
- **Rate limiting**: Respects source rate limits and retries

## Limitations

⚠️ **GDELT API**: Rate limits apply; max 250 records per request  
⚠️ **RSS Feeds**: Limited to configured sources; keyword filtering only  
⚠️ **Content Access**: Paywalls and geo-restrictions may block some articles  
⚠️ **Language**: Optimized for English content  

## Troubleshooting

### No articles fetched
- Check internet connection
- Verify query is not too specific
- Try different date range
- Check GDELT API status

### Low-quality content
- Increase `MIN_ARTICLE_LENGTH` in `config.py`
- Use more specific queries
- Filter by specific sources

### Too many duplicates
- Lower `COSINE_SIMILARITY_THRESHOLD` (more aggressive)
- Lower `FUZZY_MATCH_THRESHOLD`

## Contributing

This module is part of the OriginChain project. Follow the project's contribution guidelines.

## License

Part of OriginChain educational project.

## Contact

For issues or questions, refer to the main OriginChain repository.
