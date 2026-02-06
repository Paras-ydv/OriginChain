# OriginChain (NewsTrace AI)

> **OriginChain** is a GenAI-powered multi-source news intelligence system that finds the **root origin of any news**, reconstructs a **timeline of events**, detects **contradictions**, and generates an evidence-grounded **impact analysis** on a chosen entity (company/person/sector/country).

---

## 🚀 What Problem Are We Solving?

News today spreads fast, mutates quickly, and often gets misreported or reshaped by narratives.

Most tools only **summarize** news.

✅ OriginChain instead:
- traces the **first credible trigger**
- reconstructs the **event chain**
- highlights contradictions across sources
- explains **impact causality** with confidence

---

## ✨ Key Features

### ✅ 1. Root Source Detection
- Identifies the earliest credible trigger (press release / govt order / first report / tweet)
- Gives **source link + why it's root + confidence score**

### ✅ 2. Timeline Reconstruction
Produces a structured timeline:
- timestamp → event summary → sources → confidence
Event tags:
- `initial_claim`
- `amplification`
- `official_response`
- `correction`
- `counter_claim`
- `consequence`

### ✅ 3. Contradiction Detection
Highlights conflicting reporting:
- “Source A says X, Source B says Y”

### ✅ 4. Impact Analysis Engine
For a chosen instance (e.g. Tesla, Bitcoin, India, IT sector), generates:
- direct impact
- second-order effects
- polarity (positive/negative/mixed)
- uncertainty notes

### ✅ 5. Interactive Visualizations
- Timeline graph with event distribution
- Network graph showing article relationships
- Interactive hover details
- Color-coded event types

---

## 🧠 Why this is a GenAI Project?

OriginChain uses LLMs for:
- clustering articles into events (not just sorting by time)
- identifying the true root trigger (not just earliest article)
- extracting claims and detecting contradictions
- reasoning about causal impacts on a target entity

This is **retrieval + reasoning + generation** → proper GenAI pipeline.

---

## 🏗️ Architecture (Microservices)

The system is split into 4 independent microservices:

### 1️⃣ News Ingestion Service (Collector)
- Fetches articles using free sources (RSS/GDELT)
- Cleans and normalizes text
- Deduplicates sources
- Output: `articles.json`

### 2️⃣ Origin + Timeline Builder
- Clusters sources into timeline events
- Detects root origin
- Detects contradictions
- Output: `timeline.json`

### 3️⃣ Impact Analysis Engine
- Takes timeline + target instance
- Produces direct + indirect impact reasoning with confidence
- Output: `impact.json`

### 4️⃣ Case Manager + UI
- Streamlit/React based demo UI
- Integrates all modules
- Exports report

---

## 👥 Team Work Distribution

| Member | Role | Main Deliverable |
|--------|------|------------------|
| Sriyansh | Ingestion Service | `ingestor.py` → `articles.json` |
| Shivansh | Timeline Builder | `timeline_builder.py` → `timeline.json` |
| Anurag | Impact Engine | `impact_engine.py` → `impact.json` |
| Paras | UI + Integration | `app.py` (Streamlit) + report export |

---

## ✅ Build Order (Recommended)

1. **Ingestion (Sriyansh)** → produce `articles.json`
2. **Timeline Builder (Shivansh)** → `timeline.json`
3. **Impact Engine (Anurag)** → `impact.json`
4. **UI + Integration (Paras)** → final demo product

---

## 📁 Project Structure

```
OriginChain/
├── services/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── ingestor.py          # News ingestion service
│   │   ├── sources.py           # RSS/GDELT/Web sources
│   │   ├── deduplicator.py      # Duplicate detection
│   │   └── utils.py             # Helper functions
│   ├── timeline/
│   │   ├── __init__.py
│   │   └── timeline_builder.py  # Timeline construction
│   ├── impact/
│   │   ├── __init__.py
│   │   └── impact_engine.py     # Impact analysis
│   └── ui/
│       ├── __init__.py
│       └── app.py               # Streamlit UI
├── graphs/
│   ├── __init__.py
│   ├── plot_graph.py            # Timeline & network visualization
│   ├── buildingrelations.py     # LLM-based relationship generation
│   └── relationships.json       # Generated relationships
├── outputs/                     # Generated JSON reports
│   ├── articles.json
│   ├── timeline.json
│   └── impact.json
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md
```

## 🚀 Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd OriginChain
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Add your Gemini API key to .env
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Run the application**:
   ```bash
   streamlit run services/ui/app.py
   ```

4. **Using the app**:
   - Enter a news query (e.g., "Tesla stock price", "Union Budget 2026")
   - Specify target entity for impact analysis
   - Set max articles to fetch
   - Click "🚀 Run Analysis"
   - View timeline visualization and network graph
   - Review articles and impact analysis

## 📋 Development Workflow

Each team member works on their assigned service:
- **Sriyansh**: Implement `services/ingestion/ingestor.py`
- **Shivansh**: Implement `services/timeline/timeline_builder.py`
- **Anurag**: Implement `services/impact/impact_engine.py`
- **Paras**: Enhance `services/ui/app.py` and add export functionality

---

## 📊 Features Implemented

- ✅ Multi-source news ingestion (RSS, GDELT, Web Search)
- ✅ Duplicate article detection and deduplication
- ✅ LLM-powered timeline reconstruction
- ✅ Root origin detection with confidence scoring
- ✅ Event classification (initial_claim, amplification, etc.)
- ✅ Impact analysis on target entities
- ✅ Interactive timeline visualization with Plotly
- ✅ Network graph showing article relationships
- ✅ Streamlit-based user interface

## 🔧 Tech Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly, NetworkX
- **LLM**: Google Gemini 2.5 Flash
- **Data Processing**: Pandas, BeautifulSoup, NLTK
- **News Sources**: RSS feeds, GDELT, Web scraping

---

*Ready to trace the origin of any news story! 🔍*