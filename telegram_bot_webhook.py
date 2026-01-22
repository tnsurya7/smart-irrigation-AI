#!/usr/bin/env python3
"""
Alternative Telegram Bot using Webhook instead of polling
This avoids the 409 conflicts that occur with polling
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
    exit(1)

app = FastAPI(title="Telegram Bot Webhook")

class TelegramWebhookBot:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Message sent: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def fetch_weather_report(self) -> str:
        """Fetch weather report from backend"""
        try:
            logger.info("Fetching weather data from backend...")
            response = requests.get(f"{BACKEND_URL}/weather", timeout=15)
            
            if response.status_code == 200:
                weather_data = response.json()
                logger.info(f"Weather data received: {weather_data.get('temperature')}°C")
                
                # Format temperature properly
                temp = weather_data.get('temperature', 0)
                if isinstance(temp, (int, float)):
                    temp_str = f"{temp:.1f}"
                else:
                    temp_str = str(temp)
                
                message = f"""🌤️ <b>Weather Report - {weather_data.get('location', 'Erode')}</b>

🌡️ <b>Temperature:</b> {temp_str}°C
💨 <b>Humidity:</b> {weather_data.get('humidity', 0)}%
🌧️ <b>Rain Probability:</b> {weather_data.get('rain_probability', 0):.0f}%
☁️ <b>Condition:</b> {weather_data.get('weather_condition', 'Clear Sky')}
🕐 <b>Updated:</b> {datetime.now().strftime('%H:%M:%S')}

<i>Live weather data from OpenWeather API 🌍</i>"""
                
                return message
            else:
                logger.error(f"Weather API returned status {response.status_code}")
                return f"❌ <b>Weather Error</b>\n\nBackend returned status {response.status_code}. Please try again."
                
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return "❌ <b>Weather Error</b>\n\nUnexpected error occurred. Please try again."
    
    def process_command(self, message_text: str) -> str:
        """Process user command and return appropriate response"""
        text = message_text.lower().strip()
        
        # Weather commands
        if any(keyword in text for keyword in ['weather', 'weather report', 'weather today']):
            logger.info("Processing weather command")
            return self.fetch_weather_report()
        
        # Help commands
        elif any(keyword in text for keyword in ['help', 'commands', '/help', '/start']):
            return """🤖 <b>Smart Agriculture Bot Commands</b>

<b>📋 Available Commands:</b>
• <code>weather</code> or <code>weather report</code> - Current weather for Erode
• <code>dashboard</code> or <code>dashboard summary</code> - Today's farm summary
• <code>irrigation</code> or <code>irrigation update</code> - Pump status and activity
• <code>help</code> or <code>commands</code> - Show this help message

<i>Smart agriculture at your fingertips! 🌱🤖</i>"""
        
        # Unknown command
        else:
            return f"""❓ <b>Unknown Command</b>

I didn't understand: "<i>{message_text}</i>"

Type <code>help</code> to see available commands.

<b>Quick Commands:</b>
• <code>weather</code> - Weather report
• <code>help</code> - Show commands"""

# Global bot instance
webhook_bot = TelegramWebhookBot()

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhook from Telegram"""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")
        
        if "message" in data:
            message = data["message"]
            text = message.get("text", "")
            user = message.get("from", {})
            chat = message.get("chat", {})
            
            # Only respond to messages from our chat
            if str(chat.get("id")) != CHAT_ID:
                logger.warning(f"Ignoring message from unauthorized chat: {chat.get('id')}")
                return JSONResponse({"status": "ignored"})
            
            logger.info(f"Processing command: '{text}' from user: {user.get('username', 'unknown')}")
            
            # Process the command
            response = webhook_bot.process_command(text)
            
            # Send response
            webhook_bot.send_message(response)
            
            return JSONResponse({"status": "processed"})
        
        return JSONResponse({"status": "no_message"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/")
def root():
    """Root endpoint"""
    return {"status": "Telegram Bot Webhook Active", "timestamp": datetime.now().isoformat()}

@app.post("/test-weather")
def test_weather():
    """Test weather command directly"""
    try:
        response = webhook_bot.fetch_weather_report()
        webhook_bot.send_message(response)
        return {"status": "success", "message": "Weather report sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Telegram Bot Webhook Server...")
    print("📱 Bot will respond to messages via webhook")
    print("🧪 Test endpoint: POST /test-weather")
    uvicorn.run("telegram_bot_webhook:app", host="0.0.0.0", port=8001, reload=False)