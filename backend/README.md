# OriginChain Backend API

FastAPI-based REST API for news analysis and intelligence.

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Server
```bash
python3 api.py
```

Server runs on **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

---

## 📋 Requirements

```txt
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
```

---

## 🔌 API Endpoints

### `POST /api/analyze`
Run complete news analysis pipeline.

**Request Body:**
```json
{
  "query": "Tesla stock price",
  "target_entity": "Tesla",
  "max_articles": 20
}
```

**Response:**
```json
{
  "success": true,
  "case_id": "abc123",
  "articles": {...},
  "timeline": {...},
  "impact": {...},
  "relationships": {...}
}
```

**Process:**
1. Fetch articles from RSS/GDELT/Web
2. Deduplicate and clean
3. Build timeline with credibility scores
4. Analyze impact with Gemini AI
5. Generate relationship graph
6. Save case for sharing

---

### `GET /api/case/{case_id}`
Retrieve shared analysis by case ID.

**Response:** Complete analysis JSON

---

### `GET /api/export/{case_id}`
Download analysis report as text file.

**Response:** Text file download

---

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{"status": "healthy"}
```

---

## 🏗️ Architecture

```
api.py
├── generate_relationships()  # Network graph generation
├── POST /api/analyze         # Main analysis endpoint
├── GET /api/case/{id}        # Retrieve shared case
├── GET /api/export/{id}      # Export report
└── GET /api/health           # Health check
```

### Dependencies
- **services/ingestion**: News fetching and deduplication
- **services/timeline**: Timeline construction and credibility scoring
- **services/impact**: AI-powered impact analysis
- **graphs/buildingrelations**: Relationship generation

---

## 🔧 Configuration

### Environment Variables
Create `.env` in project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

### CORS
Configured to allow all origins for development:
```python
allow_origins=["*"]
```

For production, restrict to specific domains.

---

## 📊 Data Flow

```
1. Client Request
   ↓
2. Ingest News (RSS/GDELT/Web)
   ↓
3. Deduplicate Articles
   ↓
4. Build Timeline
   - Calculate confidence scores
   - Assign credibility ratings
   - Detect root origin
   ↓
5. Analyze Impact (Gemini AI)
   - Batch process events
   - Sentiment analysis
   - Generate predictions
   ↓
6. Generate Relationships
   - Sequential connections
   - Event type clustering
   - Root connections
   ↓
7. Save Case & Return Response
```

---

## 🧪 Testing

### Test Relationship Generation
```bash
python3 test_relationships.py
```

### Manual API Testing
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"Tesla","target_entity":"Tesla","max_articles":10}'
```

---

## 📁 Output Files

All outputs saved to `../outputs/`:
- `articles.json` - Fetched and deduplicated articles
- `timeline.json` - Timeline with events and root origin
- `impact.json` - Impact analysis results
- `relationships.json` - Network graph data
- `case_{id}.json` - Complete analysis for sharing

---

## 🐛 Troubleshooting

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

**Gemini API errors:**
- Check API key in `.env`
- Verify API quota
- System falls back to keyword analysis

**Port already in use:**
```bash
# Kill existing process
pkill -f "python3 api.py"
# Or use different port
uvicorn api:app --port 8001
```

---

## 🔒 Security Notes

- Never commit `.env` file
- Use environment variables for production
- Implement rate limiting for production
- Add authentication for sensitive endpoints
- Validate all input data

---

## 📈 Performance

- **Batch Processing**: Gemini API calls batched (10 events/batch)
- **Async Operations**: FastAPI async endpoints
- **Caching**: Case-based storage for quick retrieval
- **Fallback Logic**: Keyword analysis if AI fails

---

## 🚀 Deployment

### Production Setup
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "api.py"]
```

---

## 📝 API Response Examples

### Success Response
```json
{
  "success": true,
  "case_id": "a1b2c3d4e5f6",
  "articles": {
    "case_id": "...",
    "query": "Tesla stock price",
    "articles": [...]
  },
  "timeline": {
    "root_origin": {...},
    "events": [...],
    "contradictions": []
  },
  "impact": {
    "target_entity": "Tesla",
    "overall_polarity": "negative",
    "confidence_score": 0.9,
    "relevant_events": [...]
  },
  "relationships": {
    "relationships": [...]
  }
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

Built with FastAPI ⚡
