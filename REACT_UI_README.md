# OriginChain React UI

Modern, AI-powered news intelligence interface with stunning timeline visualizations.

## 🎨 Features

- **Modern Glass-morphism Design** - Beautiful gradient backgrounds with frosted glass effects
- **Animated Timeline** - Interactive timeline with event type indicators and confidence scores
- **Real-time Analysis** - Live news ingestion and AI-powered analysis
- **Impact Visualization** - Comprehensive impact analysis with polarity indicators
- **Responsive Layout** - Works seamlessly on all devices

## 🚀 Quick Start

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start Both Services

From the root directory:

```bash
./start.sh
```

Or manually:

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

### 4. Access the App

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
OriginChain/
├── backend/
│   ├── api.py              # FastAPI backend
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Timeline.jsx        # Animated timeline
│   │   │   └── ImpactAnalysis.jsx  # Impact visualization
│   │   ├── styles/
│   │   │   └── index.css           # Tailwind styles
│   │   ├── App.jsx                 # Main app
│   │   └── main.jsx                # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── start.sh                # Startup script
```

## 🎯 Usage

1. Enter a news query (e.g., "Tesla stock price")
2. Specify target entity for impact analysis
3. Set max articles to fetch
4. Click "Run Analysis"
5. View the animated timeline and impact analysis

## 🎨 UI Components

### Timeline Component
- Alternating left/right layout
- Event type badges with color coding
- Confidence score progress bars
- Hover animations and interactions
- Root origin highlight

### Impact Analysis Component
- Polarity indicators (positive/negative/mixed)
- Confidence score display
- Direct impact description
- Second-order effects list
- Animated entry effects

## 🛠️ Tech Stack

**Frontend:**
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Framer Motion (animations)
- Lucide React (icons)
- Axios (API calls)

**Backend:**
- FastAPI
- Uvicorn
- Pydantic

## 🎨 Design System

**Colors:**
- Primary: Indigo (#6366f1)
- Secondary: Purple (#8b5cf6)
- Background: Dark gradient (slate-900 → purple-900)

**Event Types:**
- Initial Claim: Red/Orange
- Amplification: Blue/Cyan
- Official Response: Green/Emerald
- Correction: Yellow/Amber
- Counter Claim: Purple/Pink
- Consequence: Indigo/Violet

## 📝 API Endpoints

### POST /api/analyze
Analyze news for a given query.

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
  "articles": {...},
  "timeline": {...},
  "impact": {...}
}
```

### GET /api/health
Health check endpoint.

## 🔧 Development

**Frontend Development:**
```bash
cd frontend
npm run dev
```

**Backend Development:**
```bash
cd backend
uvicorn api:app --reload
```

**Build for Production:**
```bash
cd frontend
npm run build
```

## 🎯 Future Enhancements

- [ ] Network graph visualization
- [ ] Article cards with source links
- [ ] Export reports as PDF
- [ ] Dark/light theme toggle
- [ ] Real-time updates with WebSockets
- [ ] Advanced filtering and search
- [ ] Contradiction highlighting
- [ ] Sentiment trend charts

---

**Built with ❤️ by the OriginChain Team**
