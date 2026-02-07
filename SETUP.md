# OriginChain - Complete Setup Guide

Step-by-step guide to set up and run OriginChain locally.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.8+** ([Download](https://www.python.org/downloads/))
- ✅ **Node.js 16+** ([Download](https://nodejs.org/))
- ✅ **Git** ([Download](https://git-scm.com/))
- ✅ **Gemini API Key** ([Get it here](https://ai.google.dev/))

### Verify Installation
```bash
python3 --version  # Should show 3.8 or higher
node --version     # Should show 16 or higher
npm --version      # Should show 8 or higher
```

---

## 🚀 Installation Steps

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd OriginChain
```

### Step 2: Setup Environment Variables
```bash
# Create .env file in project root
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Get Gemini API Key:**
1. Go to https://ai.google.dev/
2. Sign in with Google account
3. Create new API key
4. Copy and paste into `.env` file

### Step 3: Install Python Dependencies
```bash
# Install main dependencies
pip install -r requirements.txt

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

**If you encounter errors:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -v -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
```

**If you encounter errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

## ▶️ Running the Application

### Option 1: Using Startup Script (Recommended)
```bash
# Make script executable
chmod +x start.sh

# Run both services
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python3 api.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
```

---

## 🌐 Access Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## ✅ Verify Installation

### Test Backend
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"healthy"}
```

### Test Frontend
Open http://localhost:3000 in browser. You should see the OriginChain UI.

### Run Test Analysis
1. Enter query: "Tesla stock price"
2. Target entity: "Tesla"
3. Max articles: 10
4. Click "Run Analysis"
5. Wait for results (30-60 seconds)

---

## 📁 Project Structure Overview

```
OriginChain/
├── .env                          # API keys (DO NOT COMMIT)
├── requirements.txt              # Python dependencies
├── start.sh                      # Startup script
│
├── backend/                      # FastAPI server
│   ├── api.py                   # Main API file
│   └── requirements.txt         # Backend dependencies
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── styles/              # CSS files
│   │   ├── App.jsx              # Main app
│   │   └── main.jsx             # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── services/                     # Core services
│   ├── ingestion/               # News fetching
│   ├── timeline/                # Timeline building
│   └── impact/                  # Impact analysis
│
├── graphs/                       # Visualization logic
│   └── buildingrelations.py    # Relationship generation
│
└── outputs/                      # Generated files
    ├── articles.json
    ├── timeline.json
    ├── impact.json
    └── relationships.json
```

---

## 🔧 Configuration

### Backend Configuration

**Port Change:**
Edit `backend/api.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change port
```

**CORS Settings:**
Edit `backend/api.py`:
```python
allow_origins=["http://localhost:3000"]  # Restrict origins
```

### Frontend Configuration

**API URL:**
Edit `frontend/vite.config.js`:
```js
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // Change backend port
    changeOrigin: true
  }
}
```

**Port Change:**
Edit `frontend/vite.config.js`:
```js
server: {
  port: 3001  // Change frontend port
}
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Module not found" errors

**Solution:**
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

### Issue 2: Port already in use

**Solution:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Or use different ports (see Configuration)
```

### Issue 3: Gemini API errors

**Solution:**
- Verify API key in `.env` file
- Check API quota at https://ai.google.dev/
- System will fallback to keyword analysis if API fails

### Issue 4: No relationships in network graph

**Solution:**
- Check backend terminal for "Generated X relationships"
- Ensure at least 2 articles were fetched
- Relationships auto-generate based on timeline

### Issue 5: CORS errors

**Solution:**
- Ensure backend is running before frontend
- Check CORS settings in `backend/api.py`
- Clear browser cache

---

## 🧪 Testing

### Test Backend Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Run analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"Tesla","target_entity":"Tesla","max_articles":5}'
```

### Test Relationship Generation
```bash
cd backend
python3 test_relationships.py
```

Expected output:
```
✅ Generated X relationships
```

---

## 📦 Dependencies Explained

### Python Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-genai` - Gemini AI integration
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `pandas` - Data processing
- `nltk` - Text processing

### Node Dependencies
- `react` - UI framework
- `vite` - Build tool
- `tailwindcss` - Styling
- `framer-motion` - Animations
- `axios` - HTTP client
- `lucide-react` - Icons

---

## 🚀 Next Steps

After successful setup:

1. **Explore Features**
   - Try different queries
   - Test share and export
   - Explore visualizations

2. **Customize**
   - Change theme colors
   - Modify animations
   - Add new features

3. **Deploy**
   - See deployment guides in respective READMEs
   - Configure production settings
   - Set up monitoring

---

## 📚 Additional Resources

- **Main README**: Project overview and features
- **Backend README**: API documentation
- **Frontend README**: Component documentation
- **API Docs**: http://localhost:8000/docs (when running)

---

## 💡 Tips

- **Development**: Use `npm run dev` for hot reload
- **Production**: Build with `npm run build`
- **Debugging**: Check browser console and terminal logs
- **Performance**: Reduce max_articles for faster results
- **API Limits**: Gemini has rate limits, system auto-falls back

---

## 🆘 Getting Help

If you encounter issues:

1. Check this setup guide
2. Review error messages in terminal
3. Check browser console (F12)
4. Verify all prerequisites are installed
5. Ensure `.env` file exists with valid API key

---

## ✅ Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Repository cloned
- [ ] `.env` file created with Gemini API key
- [ ] Python dependencies installed
- [ ] Node dependencies installed
- [ ] Backend starts successfully (port 8000)
- [ ] Frontend starts successfully (port 3000)
- [ ] Health check passes
- [ ] Test analysis completes

---

**Setup complete! Ready to trace news origins! 🔍**
