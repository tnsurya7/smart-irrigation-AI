#!/bin/bash
# ESP32 USB Bridge Setup Script

echo "🌱 ESP32 USB Bridge Setup (DEMO MODE)"
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install dependencies
echo "📦 Installing USB bridge dependencies..."
npm install --package-lock-only --package-lock-file=package-lock-bridge.json --prefix . serialport @serialport/parser-readline axios

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make bridge script executable
chmod +x usb_esp32_bridge.js

echo ""
echo "🎉 ESP32 USB Bridge setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Connect ESP32 via USB cable"
echo "   2. Make sure ESP32 is sending JSON data to Serial"
echo "   3. Run: node usb_esp32_bridge.js"
echo ""
echo "🔧 Configuration:"
echo "   • Backend: https://smart-agriculture-backend-my7c.onrender.com"
echo "   • Baud Rate: 115200"
echo "   • Auto-detect ESP32 port: YES"
echo ""
echo "⚠️ DEMO MODE ONLY - This is temporary for demonstrations"