#!/bin/bash

echo "🌱 Smart Agriculture Demo Startup"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Make scripts executable
chmod +x usb_serial_reader.py
chmod +x start_demo.py

echo "✅ Python 3 found"
echo "🚀 Starting ESP32 USB Serial Reader..."
echo ""
echo "📡 Backend will run on http://localhost:5000"
echo "📊 Live data endpoint: http://localhost:5000/api/live-data"
echo ""
echo "🔄 Next steps:"
echo "   1. Connect ESP32 via USB"
echo "   2. Start dashboard: npm run dev (on port 3000)"
echo "   3. Open http://localhost:3000"
echo ""
echo "=================================================="
echo ""

# Start the demo
python3 start_demo.py