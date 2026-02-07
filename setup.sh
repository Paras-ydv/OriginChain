#!/bin/bash

echo "🔧 Setting up OriginChain React UI..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q google-genai python-Levenshtein fastapi uvicorn pydantic

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --silent

echo "✅ Setup complete!"
echo ""
echo "To start the app:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  Terminal 1: cd backend && python3 api.py"
echo "  Terminal 2: cd frontend && npm run dev"
