# OriginChain - NewsTrace AI 🔗

> **AI-powered multi-source news intelligence system** that finds the root origin of any news, reconstructs timelines, detects contradictions, and generates evidence-grounded impact analysis.

[![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0-orange)](https://ai.google.dev/)

---

## 🚀 What Makes OriginChain Unique?

Most tools only **summarize** news. OriginChain:
- ✅ Traces the **first credible trigger** (root origin detection)
- ✅ Reconstructs the **event chain** with AI-powered timeline
- ✅ Highlights **contradictions** across sources
- ✅ Explains **impact causality** with confidence scores
- ✅ Visualizes **article relationships** in interactive network graph
- ✅ Provides **credibility scoring** for each source
- ✅ Generates **sentiment analysis** over time

---

## ✨ Key Features

### 1. **Root Source Detection**
- Identifies earliest credible trigger with confidence score
- Credibility scoring (60-95%) based on source reputation

### 2. **Timeline Reconstruction**
- AI-powered event clustering and classification
- Event types: `initial_claim`, `amplification`, `official_response`, `correction`, `counter_claim`, `consequence`
- Color-coded by sentiment (positive/negative/neutral)

### 3. **AI Impact Analysis**
- Gemini 2.0 powered sentiment analysis
- Batch processing for large datasets
- Direct and second-order effects prediction
- Confidence scoring based on data quality

### 4. **Interactive Visualizations**
- **Timeline Graph**: Animated alternating timeline with hover details
- **Network Graph**: Force-directed graph showing article relationships
- **Sentiment Chart**: Line graph showing sentiment trends over time
- **Source Diversity**: Pie chart with credibility indicators

### 5. **Export & Share**
- Share analysis via unique URL
- Export reports as text files
- Case-based storage for retrieval

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React UI      │  Modern glass-morphism design
│  (Port 3000)    │  Framer Motion animations
└────────┬────────┘
         │
    ┌────▼────┐
    │ FastAPI │  RESTful API
    │ Backend │  (Port 8000)
    └────┬────┘
         │
    ┌────▼──────────────────────────┐
    │  Microservices Architecture   │
    ├───────────────────────────────┤
    │ 1. News Ingestion Service     │
    │    - RSS/GDELT/Web Search     │
    │    - Deduplication            │
    │                               │
    │ 2. Timeline Builder           │
    │    - Event clustering         │
    │    - Root origin detection    │
    │    - Credibility scoring      │
    │                               │
    │ 3. Impact Analysis Engine     │
    │    - Gemini AI integration    │
    │    - Sentiment analysis       │
    │    - Impact prediction        │
    │                               │
    │ 4. Relationship Generator     │
    │    - Network graph data       │
    │    - Connection types         │
    └───────────────────────────────┘
```

---

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Gemini API Key** ([Get it here](https://ai.google.dev/))

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repo-url>
cd OriginChain
```

### 2. Setup Environment
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 3. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
python3 api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
OriginChain/
├── backend/
│   ├── api.py                    # FastAPI server
│   ├── requirements.txt          # Backend dependencies
│   └── test_relationships.py     # Testing utilities
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Timeline.jsx           # Animated timeline
│   │   │   ├── NetworkGraph.jsx       # Force-directed graph
│   │   │   ├── ImpactAnalysis.jsx     # Impact dashboard
│   │   │   ├── SentimentChart.jsx     # Sentiment visualization
│   │   │   └── SourceDiversity.jsx    # Source pie chart
│   │   ├── styles/
│   │   │   └── index.css              # Tailwind styles
│   │   ├── App.jsx                    # Main app
│   │   └── main.jsx                   # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── services/
│   ├── ingestion/
│   │   ├── ingestor.py           # News fetching
│   │   ├── sources.py            # RSS/GDELT/Web
│   │   ├── deduplicator.py       # Duplicate removal
│   │   └── utils.py              # Helper functions
│   ├── timeline/
│   │   └── timeline_builder.py   # Timeline construction
│   └── impact/
│       └── impact_engine.py      # AI impact analysis
│
├── graphs/
│   ├── buildingrelations.py      # Relationship generation
│   └── plot_graph.py             # Visualization logic
│
├── outputs/                       # Generated reports
│   ├── articles.json
│   ├── timeline.json
│   ├── impact.json
│   ├── relationships.json
│   └── case_*.json               # Shared analyses
│
├── .env                          # API keys
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🎯 Usage

1. **Enter Query**: e.g., "Tesla stock price", "Union Budget 2026"
2. **Specify Target Entity**: e.g., "Tesla", "India"
3. **Set Max Articles**: 10-100 articles
4. **Click "Run Analysis"**
5. **View Results**:
   - Sentiment chart and source diversity
   - Animated timeline with color-coded events
   - Interactive network graph
   - Comprehensive impact analysis
6. **Share or Export**: Use buttons to share link or download report

---

## 🔧 Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Lucide React** - Icons
- **Axios** - API calls

### Backend
- **FastAPI** - REST API
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### AI/ML
- **Google Gemini 2.0** - Impact analysis
- **NLTK** - Text processing
- **Sentence Transformers** - Embeddings
- **Scikit-learn** - ML utilities

### Data Sources
- **RSS Feeds** - News aggregation
- **GDELT** - Global news database
- **Web Search** - Google News, Bing News

---

## 📊 API Endpoints

### `POST /api/analyze`
Run complete analysis pipeline.

**Request:**
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
  "case_id": "abc123def456",
  "articles": {...},
  "timeline": {...},
  "impact": {...},
  "relationships": {...}
}
```

### `GET /api/case/{case_id}`
Retrieve shared analysis.

### `GET /api/export/{case_id}`
Download report as text file.

### `GET /api/health`
Health check endpoint.

---

## 🎨 Features Showcase

### Credibility Scoring
- **Trusted Sources** (95%): Reuters, AP, Bloomberg, WSJ, BBC
- **Government** (90%): .gov domains, official statements
- **News Sites** (70%): General news websites
- **Others** (60%): Blogs, social media

### Event Classification
- **Initial Claim** (Red): First report of an event
- **Amplification** (Blue): Story spreading/reinforcement
- **Official Response** (Green): Government/company statements
- **Correction** (Yellow): Fact-checks/corrections
- **Counter Claim** (Purple): Contradicting reports
- **Consequence** (Indigo): Follow-up impacts

### Relationship Types
- **AMPLIFIES**: Later article reinforces earlier claim
- **CORRECTS**: Later article corrects misinformation
- **COUNTERS**: Contradicting information
- **OFFICIAL_RESPONSE**: Official statement
- **CONSEQUENCE_OF**: Resulting events

---

## 🏆 Hackathon Ready

### Unique Selling Points
1. **Only tool that finds ROOT origin** - Not just earliest article
2. **AI-powered impact analysis** - Gemini 2.0 integration
3. **Network visualization** - See information flow
4. **Credibility scoring** - Trust indicators
5. **Share & Export** - Collaboration features

### Demo Flow
1. Show breaking news query
2. Run real-time analysis
3. Highlight contradictions found
4. Show network graph connections
5. Export professional report
6. Share analysis link

### Use Cases
- **Journalists**: Verify story origins and track misinformation
- **Investors**: Monitor market-moving news and sentiment
- **Researchers**: Study information spread patterns
- **PR Teams**: Track brand mentions and sentiment

---

## 🐛 Troubleshooting

**Backend won't start:**
```bash
pip install --upgrade google-genai fastapi uvicorn
```

**Frontend build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**No relationships in graph:**
- Check backend logs for "Generated X relationships"
- Ensure at least 2 articles were fetched
- Relationships auto-generate based on timeline

**Gemini API errors:**
- Verify API key in `.env`
- Check API quota limits
- System falls back to keyword analysis

---

## 👥 Team

| Member | Role | Contribution |
|--------|------|--------------|
| Sriyansh | Ingestion Service | Multi-source news fetching |
| Shivansh | Timeline Builder | Event clustering & root detection |
| Anurag | Impact Engine | AI-powered sentiment analysis |
| Paras | UI & Integration | React frontend & API integration |

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- GDELT Project for global news data
- Open-source community for amazing tools

---

**Built with ❤️ for accurate news intelligence**

*Ready to trace the origin of any news story! 🔍*
