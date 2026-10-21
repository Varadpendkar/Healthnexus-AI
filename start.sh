#!/bin/bash

echo "=========================================="
echo "🚀 Starting Healthnexus AI"
echo "=========================================="
echo ""

export PATH="/usr/local/bin:/opt/homebrew/bin:/opt/anaconda3/bin:$PATH"
export COPYFILE_DISABLE=1

# Clean up any stale processes on ports 5001 and 3000
echo "🧹 Checking ports 5001 and 3000..."
lsof -ti :5001 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true

# Cleanup trap on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stopping all servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

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

# Clean up any rogue AppleDouble files that cause python site.py crash
find backend/venv -name "._*.pth" -delete 2>/dev/null || true

# Start backend in background
echo ""
echo "🔧 Starting Flask backend on port 5001..."
cd backend
./venv/bin/python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 4

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo ""
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
fi

echo ""
echo "=========================================="
echo "✅ Healthnexus AI servers starting!"
echo "=========================================="
echo ""
echo "📍 Backend API:  http://localhost:5001"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "👉 Note: React initial compilation takes ~15-20 seconds."
echo "👉 Keep this terminal open! Press Ctrl+C to stop all servers."
echo "=========================================="
echo ""

# Start frontend (foreground so compilation logs and ready status are visible)
cd frontend
BROWSER=none npm start
