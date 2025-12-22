#!/bin/bash
# 🤖 Smart Agriculture Telegram Bot - Production Deployment Script

echo "🌱 Smart Agriculture Telegram Bot Deployment"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Install required packages
echo "📦 Installing required packages..."
pip3 install python-telegram-bot requests --break-system-packages --quiet

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Set environment variables
echo "🔧 Setting up environment variables..."
export TELEGRAM_BOT_TOKEN="8063174729:AAGJYD_IMImdzkTRYbCiokomWsZlHcIW8jg"
export TELEGRAM_CHAT_ID="5707565347"
export OPENWEATHER_API_KEY="59ade005948b4c8f58a100afc603f047"
export BACKEND_URL="https://smart-agriculture-backend-my7c.onrender.com"
export WEATHER_CITY="Erode"

echo "✅ Environment variables set"

# Test bot connection
echo "🧪 Testing bot connection..."
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Bot token is valid"
else
    echo "❌ Bot token test failed"
    exit 1
fi

# Test backend connection
echo "🧪 Testing backend connection..."
curl -s "$BACKEND_URL/api/health" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Backend is online"
else
    echo "⚠️  Backend might be offline, but continuing..."
fi

echo ""
echo "🎉 Setup complete! Your bot is ready to run."
echo ""
echo "📱 Bot Details:"
echo "   Bot Name: Smart Agriculture Alert Bot"
echo "   Username: @Arimax_Alert_Bot"
echo "   Chat ID: 5707565347"
echo "   Backend: $BACKEND_URL"
echo ""
echo "🚀 To start the bot, run:"
echo "   python3 telegram_production.py"
echo ""
echo "📋 To test the bot:"
echo "   1. Open Telegram"
echo "   2. Search for @Arimax_Alert_Bot"
echo "   3. Click START"
echo "   4. Send: /start"
echo ""
echo "🔄 To run in background:"
echo "   nohup python3 telegram_production.py > telegram.log 2>&1 &"
echo ""

# Ask if user wants to start the bot now
read -p "🤖 Do you want to start the bot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting Telegram bot..."
    python3 telegram_production.py
else
    echo "👍 Bot is ready. Run 'python3 telegram_production.py' when you're ready."
fi