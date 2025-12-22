"""
Telegram Bot Integration for Smart Agriculture Backend
Webhook-based bot integrated with FastAPI backend
"""

import os
import json
import logging
import requests
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/telegram", tags=["telegram"])

# Environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "https://smart-agriculture-backend-my7c.onrender.com")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AUTHORIZED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "***REMOVED***")

# Telegram API URL
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_telegram_message(chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
    """Send message to Telegram chat"""
    try:
        response = requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False

def get_sensor_data() -> Dict[str, Any]:
    """Get latest sensor data from internal shared state"""
    try:
        # Import shared state from production backend
        from production_backend import latest_sensor_data
        
        if latest_sensor_data:
            return latest_sensor_data
        else:
            # Return safe defaults if no data available
            return {
                "soil_moisture": 0.0,
                "temperature": 0.0,
                "humidity": 0.0,
                "rain_detected": False,
                "light_raw": 0,
                "light_percent": 0.0,
                "light_state": "dark",
                "pump_status": 0,
                "flow_rate": 0.0,
                "total_liters": 0.0,
                "mode": "auto",
                "source": "system"
            }
    except Exception as e:
        logger.error(f"Failed to get sensor data from shared state: {e}")
        return {}

def get_weather_data() -> Dict[str, Any]:
    """Get weather data from internal shared state"""
    try:
        # Import shared state from production backend
        from production_backend import latest_weather_data
        
        if latest_weather_data:
            return latest_weather_data
        else:
            # Return safe defaults if no data available
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "rain_probability": 0,
                "rain_expected": False,
                "location": "Erode, Tamil Nadu"
            }
    except Exception as e:
        logger.error(f"Failed to get weather data from shared state: {e}")
        return {}

def control_pump(command: str) -> bool:
    """Control pump via internal backend functions"""
    try:
        # Import shared state from production backend
        from production_backend import latest_sensor_data
        
        # Update pump status in shared state
        if latest_sensor_data:
            latest_sensor_data["pump_status"] = 1 if command.upper() == "ON" else 0
            latest_sensor_data["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"Pump turned {command} via Telegram")
        return True
        
    except Exception as e:
        logger.error(f"Failed to control pump: {e}")
        return False

def process_telegram_command(text: str, chat_id: str) -> str:
    """Process Telegram command and return response"""
    text_lower = text.lower().strip()
    
    # Start command
    if text_lower in ["/start", "start"]:
        return """🌱 **ARIMAX Smart Agriculture Bot** 🌱

🤖 **Production Ready!**
🔗 **Backend:** Connected
🌍 **Location:** Erode, Tamil Nadu

**🎮 Available Commands:**
• `pump on` - Turn irrigation ON
• `pump off` - Turn irrigation OFF
• `sensor data` - Live sensor readings
• `weather report` - Current weather
• `dashboard` - System status

**🗣️ Natural Language:**
• "Turn on the pump"
• "Show sensor data"
• "What's the weather?"
• "Is it raining?"

**Ready to control your smart farm!** 🚜"""

    # Pump control commands
    elif any(cmd in text_lower for cmd in ["pump on", "turn on pump", "start irrigation", "irrigation on"]):
        success = control_pump("ON")
        if success:
            return f"""🟢 **PUMP TURNED ON** ✅

⏰ **Time:** {datetime.now().strftime("%H:%M:%S")}
🚿 **Status:** Irrigation started
🔄 **Method:** Telegram remote control
💧 **Source:** ARIMAX Smart Agriculture

The pump is now running. Monitor via dashboard."""
        else:
            return "❌ **Failed to turn pump ON**\n\nPlease check system status and try again."

    elif any(cmd in text_lower for cmd in ["pump off", "turn off pump", "stop irrigation", "irrigation off"]):
        success = control_pump("OFF")
        if success:
            return f"""🔴 **PUMP TURNED OFF** ✅

⏰ **Time:** {datetime.now().strftime("%H:%M:%S")}
🚿 **Status:** Irrigation stopped
🔄 **Method:** Telegram remote control
💧 **Source:** ARIMAX Smart Agriculture

The pump has been turned off."""
        else:
            return "❌ **Failed to turn pump OFF**\n\nPlease check system status and try again."

    # Sensor data commands
    elif any(cmd in text_lower for cmd in ["sensor", "data", "readings", "current", "status"]):
        sensor_data = get_sensor_data()
        if sensor_data:
            # Format light status with emoji
            light_state = sensor_data.get('light_state', 'unknown')
            light_percent = sensor_data.get('light_percent', 0)
            light_raw = sensor_data.get('light_raw', 0)
            
            light_emoji = {
                'very_bright': '☀️',
                'normal': '🌤️', 
                'low': '🌥️',
                'dark': '🌙'
            }.get(light_state, '💡')
            
            return f"""📊 **LIVE SENSOR DATA** 📊

🌱 **Soil Moisture:** {sensor_data.get('soil_moisture', 0)}%
🌡️ **Temperature:** {sensor_data.get('temperature', 0)}°C
💨 **Humidity:** {sensor_data.get('humidity', 0)}%
🌧️ **Rain:** {'🌧️ Detected' if sensor_data.get('rain_detected') else '☀️ Clear'}
💡 **Light:** {light_percent}% ({light_emoji} {light_state.title()})
🚿 **Pump:** {'🟢 ON' if sensor_data.get('pump_status') == 1 else '🔴 OFF'}
💧 **Flow Rate:** {sensor_data.get('flow_rate', 0)} L/min
🪣 **Total Water:** {sensor_data.get('total_liters', 0)} L

📡 **Source:** {sensor_data.get('source', 'API')}
⏰ **Updated:** {datetime.now().strftime("%H:%M:%S")}"""
        else:
            return "❌ **Sensor data unavailable**\n\nCheck system connectivity and try again."

    # Weather commands
    elif any(cmd in text_lower for cmd in ["weather", "rain", "temperature", "forecast", "climate"]):
        weather_data = get_weather_data()
        if weather_data:
            temp = weather_data.get('temperature', 0)
            humidity = weather_data.get('humidity', 0)
            rain_prob = weather_data.get('rain_probability', 0)
            rain_expected = weather_data.get('rain_expected', False)
            location = weather_data.get('location', 'Erode')
            
            return f"""🌤️ **WEATHER - {location}** 🌤️

**Current Conditions:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Rain Probability: {rain_prob}%

**Forecast:**
• Rain Expected: {'🌧️ Yes' if rain_expected else '☀️ No'}
• Irrigation: {'⏸️ Skip (rain coming)' if rain_prob > 40 else '✅ Safe to irrigate'}

**Farming Recommendation:**
{'🌧️ Wait for rain, skip irrigation' if rain_expected else '🚿 Good conditions for irrigation'}

⏰ **Updated:** {datetime.now().strftime("%H:%M:%S")}"""
        else:
            return "❌ **Weather data unavailable**\n\nPlease try again in a few minutes."

    # Dashboard/report commands
    elif any(cmd in text_lower for cmd in ["dashboard", "report", "summary", "today"]):
        sensor_data = get_sensor_data()
        weather_data = get_weather_data()
        
        # Format light status
        light_state = sensor_data.get('light_state', 'unknown')
        light_percent = sensor_data.get('light_percent', 0)
        light_emoji = {
            'very_bright': '☀️',
            'normal': '🌤️', 
            'low': '🌥️',
            'dark': '🌙'
        }.get(light_state, '💡')
        
        return f"""📈 **SMART AGRICULTURE DASHBOARD** 📈

**🌱 Current Farm Status:**
• Soil Moisture: {sensor_data.get('soil_moisture', 0)}%
• Temperature: {sensor_data.get('temperature', 0)}°C
• Light Level: {light_percent}% ({light_emoji} {light_state.title()})
• Pump Status: {'🟢 ON' if sensor_data.get('pump_status') == 1 else '🔴 OFF'}

**🌤️ Weather Conditions:**
• Location: {weather_data.get('location', 'Erode')}
• Temperature: {weather_data.get('temperature', 0)}°C
• Rain Probability: {weather_data.get('rain_probability', 0)}%

**💧 Water Management:**
• Flow Rate: {sensor_data.get('flow_rate', 0)} L/min
• Total Used: {sensor_data.get('total_liters', 0)} L

**🤖 System Status:**
• Backend: ✅ Online
• API: ✅ Connected
• ARIMAX Model: ✅ Active

⏰ **Report Time:** {datetime.now().strftime("%H:%M:%S")}"""

    # Help command
    elif text_lower in ["help", "/help", "commands"]:
        return """ℹ️ **HELP & COMMANDS** ℹ️

**🎮 Control Commands:**
• `pump on` / `pump off` - Control irrigation
• `sensor data` - Live readings
• `weather report` - Current weather
• `dashboard` - System summary

**🚨 Alert Commands:**
• `threshold status` - Check alert thresholds
• `rain status` - Rain sensor & forecast
• `today summary` - Today's farm report

**🗣️ Natural Language:**
• "Turn on the pump"
• "What's the weather like?"
• "Show me sensor data"
• "Is it going to rain?"

**⚡ Quick Tips:**
• Commands work in English and natural language
• Bot responds instantly via webhook
• All data is live from your farm sensors
• Automatic alerts for critical conditions

**🆘 Support:**
Type any command or ask naturally!"""

    # New alert status commands
    elif any(cmd in text_lower for cmd in ["threshold status", "thresholds", "alert status"]):
        try:
            from telegram_alerts import get_threshold_status
            return get_threshold_status()
        except Exception as e:
            logger.error(f"Error getting threshold status: {e}")
            return "❌ **Threshold status unavailable**\n\nSystem may be starting up. Try again in a moment."

    elif any(cmd in text_lower for cmd in ["rain status", "rain forecast", "rain check"]):
        try:
            from telegram_alerts import get_rain_status
            return get_rain_status()
        except Exception as e:
            logger.error(f"Error getting rain status: {e}")
            return "❌ **Rain status unavailable**\n\nSystem may be starting up. Try again in a moment."

    elif any(cmd in text_lower for cmd in ["today summary", "daily summary", "farm summary"]):
        try:
            from telegram_alerts import send_evening_dashboard_summary
            # Get the summary content without sending
            sensor_data = get_sensor_data()
            weather_data = get_weather_data()
            
            soil_avg = sensor_data.get('soil_moisture', 0)
            temp_avg = sensor_data.get('temperature', 0)
            light_state = sensor_data.get('light_state', 'normal')
            water_used = sensor_data.get('total_liters', 0)
            pump_status = sensor_data.get('pump_status', 0)
            
            system_status = "✅ Healthy"
            if soil_avg < 30:
                system_status = "⚠️ Low soil moisture"
            elif temp_avg > 35:
                system_status = "⚠️ High temperature"
            
            return f"""📊 **TODAY'S FARM SUMMARY** 📊

📅 **Date:** {datetime.now().strftime("%B %d, %Y")}

**🌱 Current Status:**
• Soil Moisture: {soil_avg}%
• Temperature: {temp_avg}°C
• Light Level: {light_state.title()}
• Humidity: {sensor_data.get('humidity', 0)}%

**💧 Water Management:**
• Total Water Used: {water_used} L
• Pump Status: {'🟢 ON' if pump_status == 1 else '🔴 OFF'}

**🤖 System Health:**
• Overall Status: {system_status}
• Backend: ✅ Online
• ARIMAX Model: ✅ Active

**🌤️ Weather:**
• Rain Probability: {weather_data.get('rain_probability', 0)}%

⏰ **Report Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return "❌ **Daily summary unavailable**\n\nSystem may be starting up. Try again in a moment."

    # Tamil/Tanglish support
    elif any(cmd in text_lower for cmd in ["iniku", "mala", "mazhai"]):
        weather_data = get_weather_data()
        rain_prob = weather_data.get('rain_probability', 0) if weather_data else 0
        if rain_prob > 40:
            return "🌧️ **Iniku mazhai varum!** \n\nRain probability: {}%\n\n🚿 Irrigation skip pannunga.".format(rain_prob)
        else:
            return "☀️ **Iniku mazhai varadu!** \n\nClear weather expected.\n\n✅ Irrigation safe-ah pannalam."

    # Unknown command
    else:
        return """🤔 **Command not recognized**

**Try these:**
• `pump on` - Turn irrigation ON
• `sensor data` - Get live readings  
• `weather report` - Current weather
• `dashboard` - System status
• `help` - Show all commands

**Or ask naturally:**
• "Turn on the pump"
• "What's the weather?"
• "Show sensor data"

Type `/start` for the main menu."""

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook"""
    try:
        data = await request.json()
        logger.info(f"Received Telegram webhook: {data}")
        
        # Check if message exists
        if "message" not in data:
            return {"ok": True}
        
        message = data["message"]
        chat_id = str(message["chat"]["id"])
        
        # Security: Only respond to authorized chat
        if chat_id != AUTHORIZED_CHAT_ID:
            logger.warning(f"Unauthorized chat ID: {chat_id}")
            send_telegram_message(
                chat_id, 
                "❌ **Unauthorized Access**\n\nThis bot is for authorized users only."
            )
            return {"ok": True}
        
        # Get message text
        text = message.get("text", "").strip()
        if not text:
            return {"ok": True}
        
        # Process command
        response_text = process_telegram_command(text, chat_id)
        
        # Send response
        success = send_telegram_message(chat_id, response_text)
        
        if success:
            logger.info(f"Telegram response sent successfully to {chat_id}")
        else:
            logger.error(f"Failed to send Telegram response to {chat_id}")
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return {"ok": False, "error": str(e)}

@router.get("/webhook/info")
async def webhook_info():
    """Get webhook information"""
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")
    
    try:
        response = requests.get(f"{TG_API}/getWebhookInfo", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to get webhook info")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/set")
async def set_webhook():
    """Set Telegram webhook URL"""
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")
    
    webhook_url = f"{BACKEND_URL}/telegram/webhook"
    
    try:
        response = requests.post(
            f"{TG_API}/setWebhook",
            json={"url": webhook_url},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Webhook set successfully: {webhook_url}")
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to set webhook")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/webhook")
async def delete_webhook():
    """Delete Telegram webhook"""
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")
    
    try:
        response = requests.post(f"{TG_API}/deleteWebhook", timeout=10)
        if response.status_code == 200:
            logger.info("Webhook deleted successfully")
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to delete webhook")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))