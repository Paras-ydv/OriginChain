#!/bin/bash

echo "🚀 Starting OriginChain..."

# Start backend
echo "Starting FastAPI backend..."
cd backend
python3 api.py &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start frontend
echo "Starting React frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ OriginChain is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
