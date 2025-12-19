#!/bin/bash

# Smart Agriculture - Unified System Startup Script
# Single command to start the complete system

echo "🌱 Smart Agriculture - Unified System Startup"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if main_unified.py exists
if [ ! -f "main_unified.py" ]; then
    echo "❌ main_unified.py not found!"
    exit 1
fi

# Kill any existing processes on port 8000
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start the unified system
echo "🚀 Starting unified system on port 8000..."
echo ""
echo "🌐 Dashboard: http://localhost:8000"
echo "📡 API: http://localhost:8000/api/*"
echo "🔌 WebSocket: ws://localhost:8000/ws"
echo "🤖 Telegram: @Arimax_Alert_Bot"
echo ""
echo "Press Ctrl+C to stop the system"
echo "=============================================="

# Run the unified system
python main_unified.py