#!/bin/bash

echo "=========================================="
echo "🚀 Starting Healthnexus AI"
echo "=========================================="
echo ""

export PATH="/usr/local/bin:/opt/homebrew/bin:/opt/anaconda3/bin:$PATH"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✅ Virtual environment created and dependencies installed"
else
    echo "✅ Virtual environment found"
fi

# Start backend in background
echo ""
echo "🔧 Starting Flask backend on port 5001..."
cd backend
./venv/bin/python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo ""
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
fi

# Start frontend
echo ""
echo "🎨 Starting React frontend on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "✅ Healthnexus AI is running!"
echo "=========================================="
echo ""
echo "📍 Backend API:  http://localhost:5001"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=========================================="

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID
