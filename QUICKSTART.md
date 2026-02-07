# 🚀 Quick Start Guide

## Start the Application

### Terminal 1 - Backend
```bash
cd backend
python3 api.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Access
Open http://localhost:3000

## What You'll See

1. **Input Form** - Enter query, target entity, max articles
2. **Timeline Analysis** - Animated timeline with color-coded events
3. **Network Graph** - Interactive force-directed graph showing article relationships
4. **Impact Analysis** - Sentiment analysis and impact metrics

## Network Graph Features

- **Nodes** = Articles (color-coded by event type)
- **Edges** = Relationships between articles
  - Blue = Amplifies
  - Yellow = Corrects  
  - Red = Counters
  - Green = Official Response
- **Hover** = See article details
- **Auto-layout** = Physics-based positioning

## Troubleshooting

If network graph is empty:
- Check backend logs for relationship generation
- Verify at least 2 articles were fetched
- Relationships are auto-generated based on timeline order

## Test
```bash
bash test.sh
```
