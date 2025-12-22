#!/usr/bin/env python3
"""
Production Smart Agriculture Telegram Bot
Uses environment variables for all configuration
"""

import asyncio
import json
import logging
import requests
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production Configuration - All from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
BACKEND_URL = os.getenv('BACKEND_URL', 'https://smart-agriculture-backend-my7c.onrender.com')
CITY = os.getenv('WEATHER_CITY', 'Erode')

# Validate required environment variables
required_vars = {
    'TELEGRAM_BOT_TOKEN': TELEGRAM_BOT_TOKEN,
    'TELEGRAM_CHAT_ID': CHAT_ID,
    'OPENWEATHER_API_KEY': OPENWEATHER_API_KEY,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Global variables for tracking
pump_operations = []
irrigation_cycles = []

class ProductionFarmController:
    def __init__(self):
        self.backend_url = BACKEND_URL
        
    async def send_pump_command(self, command):
        """Send pump command via backend API"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/pump-control",
                json={"command": command, "source": "telegram"},
                timeout=10
            )
            
            if response.status_code == 200:
                pump_operations.append({
                    'timestamp': datetime.now(),
                    'command': command,
                    'status': 'success'
                })
                logger.info(f"🚿 Pump command sent: {command}")
                return True
            else:
                logger.error(f"❌ Pump command failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send pump command: {e}")
            return False
    
    async def get_sensor_data(self):
        """Get latest sensor data from backend API"""
        try:
            response = requests.get(f"{self.backend_url}/api/sensor-data/latest", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [{}])[0] if data.get('data') else {}
        except Exception as e:
            logger.error(f"❌ Failed to get sensor data: {e}")
        return {}

# Initialize production farm controller
farm = ProductionFarmController()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with welcome message"""
    keyboard = [
        [InlineKeyboardButton("🚿 Pump Control", callback_data="pump_menu")],
        [InlineKeyboardButton("📊 Sensor Data", callback_data="sensor_data")],
        [InlineKeyboardButton("🌤️ Weather Report", callback_data="weather_report")],
        [InlineKeyboardButton("📈 Dashboard Report", callback_data="dashboard_report")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = f"""
🌱 **Smart Agriculture Bot - PRODUCTION** 🌱

🤖 **Connected to**: {BACKEND_URL}
🌍 **Weather Location**: {CITY}
📱 **Chat ID**: {CHAT_ID}

**Available Commands:**
• Control pump remotely
• Get real-time sensor data  
• Weather reports & forecasts
• System status & analytics

👆 **Use buttons or type commands**
    """
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "pump_menu":
        await pump_control_menu(query)
    elif query.data == "pump_on":
        await pump_on_command(query)
    elif query.data == "pump_off":
        await pump_off_command(query)
    elif query.data == "sensor_data":
        await sensor_data_command(query)
    elif query.data == "weather_report":
        await weather_report_command(query)
    elif query.data == "dashboard_report":
        await dashboard_report_command(query)

async def pump_control_menu(query):
    """Show pump control options"""
    keyboard = [
        [InlineKeyboardButton("🟢 Turn Pump ON", callback_data="pump_on")],
        [InlineKeyboardButton("🔴 Turn Pump OFF", callback_data="pump_off")],
        [InlineKeyboardButton("📊 Current Status", callback_data="sensor_data")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🚿 **Pump Control Panel**\n\nSelect an action:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def pump_on_command(query):
    """Turn pump ON"""
    success = await farm.send_pump_command("ON")
    
    if success:
        msg = f"""
🟢 **PUMP TURNED ON** ✅

⏰ **Time**: {datetime.now().strftime("%H:%M:%S")}
🚿 **Status**: Irrigation started
🔄 **Method**: Telegram remote control
        """
    else:
        msg = "❌ **Failed to turn pump ON**\n\nPlease check system status."
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def pump_off_command(query):
    """Turn pump OFF"""
    success = await farm.send_pump_command("OFF")
    
    if success:
        msg = f"""
🔴 **PUMP TURNED OFF** ✅

⏰ **Time**: {datetime.now().strftime("%H:%M:%S")}
🚿 **Status**: Irrigation stopped
🔄 **Method**: Telegram remote control
        """
    else:
        msg = "❌ **Failed to turn pump OFF**\n\nPlease check system status."
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def sensor_data_command(query):
    """Get sensor data from production API"""
    sensor_data = await farm.get_sensor_data()
    
    if sensor_data:
        msg = f"""
📊 **LIVE SENSOR DATA** 📊

🌱 **Soil Moisture**: {sensor_data.get('soil_moisture', 0)}%
🌡️ **Temperature**: {sensor_data.get('temperature', 0)}°C
💨 **Humidity**: {sensor_data.get('humidity', 0)}%
🌧️ **Rain**: {'🌧️ Detected' if sensor_data.get('rain_detected') else '☀️ Clear'}
🚿 **Pump**: {'🟢 ON' if sensor_data.get('pump_status') == 1 else '🔴 OFF'}
💧 **Flow Rate**: {sensor_data.get('flow_rate', 0)} L/min
🪣 **Total Water**: {sensor_data.get('total_liters', 0)} L

📡 **Source**: {sensor_data.get('source', 'API')}
⏰ **Updated**: {datetime.now().strftime("%H:%M:%S")}
        """
    else:
        msg = "❌ **Sensor data unavailable**\n\nCheck system connectivity."
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def weather_report_command(query):
    """Get weather from OpenWeather API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description'].title()
            
            # Get forecast for rain probability
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
            forecast_response = requests.get(forecast_url, timeout=10)
            
            rain_prob = 0
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                rain_prob = forecast_data['list'][0].get('pop', 0) * 100
            
            msg = f"""
🌤️ **WEATHER - {CITY}** 🌤️

**Current Conditions:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Conditions: {description}

**Rain Forecast:**
• Probability: {rain_prob:.0f}%
• Recommendation: {'⏸️ Skip irrigation' if rain_prob > 40 else '✅ Safe to irrigate'}

⏰ **Updated**: {datetime.now().strftime("%H:%M:%S")}
            """
        else:
            msg = "❌ **Weather data unavailable**"
            
    except Exception as e:
        msg = f"❌ **Weather Error**: {str(e)}"
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def dashboard_report_command(query):
    """Generate dashboard report"""
    sensor_data = await farm.get_sensor_data()
    today_pumps = len([op for op in pump_operations if op['timestamp'].date() == datetime.now().date()])
    
    msg = f"""
📈 **PRODUCTION DASHBOARD** 📈

**System Status:**
• Backend: {BACKEND_URL}
• API Status: {'✅ Online' if sensor_data else '⚠️ Limited'}
• Pump Operations Today: {today_pumps}

**Current Readings:**
• Soil: {sensor_data.get('soil_moisture', 0)}%
• Temperature: {sensor_data.get('temperature', 0)}°C
• Pump: {'🟢 ON' if sensor_data.get('pump_status') == 1 else '🔴 OFF'}

**Water Management:**
• Total Used: {sensor_data.get('total_liters', 0)} L
• Flow Rate: {sensor_data.get('flow_rate', 0)} L/min

⏰ **Report Time**: {datetime.now().strftime("%H:%M:%S")}
    """
    
    await query.edit_message_text(msg, parse_mode='Markdown')

def main():
    """Start the production Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("🤖 Production Telegram Bot started!")
    logger.info(f"🔗 Backend: {BACKEND_URL}")
    logger.info(f"🌤️ Weather: {CITY}")
    logger.info(f"📱 Chat ID: {CHAT_ID}")
    
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()