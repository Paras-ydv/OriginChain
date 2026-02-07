# OriginChain Frontend

Modern React UI with stunning visualizations for news intelligence.

## 🚀 Quick Start

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

App runs on **http://localhost:3000**

### Build for Production
```bash
npm run build
npm run preview
```

---

## 🎨 Features

### 1. **Animated Timeline**
- Alternating left/right layout
- Color-coded by sentiment (green/red/blue)
- Hover tooltips with article details
- Click to open article in new tab
- Confidence score progress bars

### 2. **Network Graph**
- Force-directed physics simulation
- Interactive node hover
- Color-coded relationships
- Real-time stats display
- Glow effects and animations

### 3. **Sentiment Chart**
- Line graph showing sentiment over time
- Positive/negative/neutral breakdown
- Trend indicators
- Date-based grouping

### 4. **Source Diversity**
- Pie chart visualization
- Credibility indicators per source
- Source count and distribution
- Average credibility score

### 5. **Impact Analysis**
- Polarity indicators
- Confidence scoring
- Direct and second-order effects
- Relevant events list with summaries

### 6. **Share & Export**
- Copy shareable link
- Export report as text
- Case-based URL routing

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Timeline.jsx           # Animated timeline
│   │   ├── NetworkGraph.jsx       # Force-directed graph
│   │   ├── ImpactAnalysis.jsx     # Impact dashboard
│   │   ├── SentimentChart.jsx     # Sentiment line chart
│   │   └── SourceDiversity.jsx    # Source pie chart
│   ├── styles/
│   │   └── index.css              # Tailwind + custom styles
│   ├── App.jsx                    # Main application
│   └── main.jsx                   # Entry point
├── public/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

---

## 🔧 Tech Stack

- **React 18.2** - UI framework
- **Vite 5.0** - Build tool & dev server
- **Tailwind CSS 3.4** - Utility-first styling
- **Framer Motion 10.16** - Animation library
- **Lucide React 0.300** - Icon library
- **Axios 1.6** - HTTP client

---

## 🎨 Design System

### Colors
```js
primary: '#6366f1'    // Indigo
secondary: '#8b5cf6'  // Purple
```

### Event Type Colors
- **Root Origin**: Gold (#FFD700)
- **Initial Claim**: Red (#ef4444)
- **Amplification**: Blue (#3b82f6)
- **Official Response**: Green (#10b981)
- **Correction**: Yellow (#f59e0b)
- **Counter Claim**: Purple (#a855f7)
- **Consequence**: Indigo (#6366f1)

### Sentiment Colors
- **Positive**: Green (#10b981)
- **Negative**: Red (#ef4444)
- **Neutral**: Gray (#6b7280)

### Animations
```js
fade-in: 0.5s ease-in
slide-up: 0.5s ease-out
pulse-slow: 3s infinite
```

---

## 🧩 Components

### Timeline.jsx
**Props:**
- `events` - Array of timeline events
- `rootOrigin` - Root origin object
- `impact` - Impact analysis data

**Features:**
- Alternating layout with center line
- Sentiment-based color coding
- Hover tooltips with article preview
- Click to open article URL
- Animated entrance effects

---

### NetworkGraph.jsx
**Props:**
- `timeline` - Timeline data
- `relationships` - Relationship array

**Features:**
- Canvas-based force simulation
- 400 frames of physics animation
- Node repulsion and edge attraction
- Hover to see article details
- Color-coded nodes and edges
- Stats display (nodes/edges count)

---

### SentimentChart.jsx
**Props:**
- `impact` - Impact analysis data

**Features:**
- SVG line chart
- Date-based grouping
- Sentiment score calculation
- Positive/negative/neutral counts
- Trend indicator (improving/declining)

---

### SourceDiversity.jsx
**Props:**
- `timeline` - Timeline data

**Features:**
- SVG pie chart
- Top 8 sources displayed
- Credibility score per source
- Article count per source
- Average credibility calculation

---

### ImpactAnalysis.jsx
**Props:**
- `impact` - Impact analysis data

**Features:**
- Polarity indicator with icon
- Confidence score display
- Impact level metrics
- Second-order effects list
- Relevant events with hover summaries
- Sentiment badges

---

## 🎯 Usage

### Basic Flow
```jsx
import App from './App';

// App handles:
// 1. User input (query, entity, max articles)
// 2. API call to backend
// 3. Display all visualizations
// 4. Share and export functionality
```

### API Integration
```js
const response = await axios.post('/api/analyze', {
  query: 'Tesla stock price',
  target_entity: 'Tesla',
  max_articles: 20
});

setData(response.data);
setCaseId(response.data.case_id);
```

---

## 🎨 Styling

### Glass Morphism
```css
.glass {
  @apply bg-white/10 backdrop-blur-lg border border-white/20;
}
```

### Glow Effect
```css
.glow {
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
}
```

### Gradient Background
```css
body {
  @apply bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900;
}
```

---

## 🔌 API Proxy

Vite proxies `/api` requests to backend:

```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

---

## 🐛 Troubleshooting

**Build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Proxy not working:**
- Ensure backend is running on port 8000
- Check vite.config.js proxy settings

**Animations laggy:**
- Reduce animation frames in NetworkGraph
- Disable motion in Framer Motion settings

**Canvas not rendering:**
- Check browser console for errors
- Ensure relationships data is present

---

## 📦 Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "framer-motion": "^10.16.0",
  "lucide-react": "^0.300.0",
  "tailwindcss": "^3.4.0",
  "vite": "^5.0.0"
}
```

---

## 🚀 Deployment

### Build
```bash
npm run build
```

Output in `dist/` folder.

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

### Environment Variables
Set backend API URL:
```bash
VITE_API_URL=https://your-backend.com
```

---

## 🎨 Customization

### Change Theme Colors
Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: '#your-color',
      secondary: '#your-color'
    }
  }
}
```

### Modify Animations
Edit `tailwind.config.js`:
```js
animation: {
  'custom': 'customAnim 1s ease-in'
}
```

---

## 📱 Responsive Design

All components are responsive:
- Mobile: Single column layout
- Tablet: 2-column grid
- Desktop: Full multi-column layout

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

Built with React ⚛️ + Vite ⚡
