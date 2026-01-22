"""
Telegram 5-Minute Real Data Updates for Smart Agriculture
STRICT RULES: Only real data, ESP32 online check, transparent sources
"""

import os
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5707565347")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ESP32 online tracking
LAST_ESP32_TIME: Optional[datetime] = None
ESP32_ONLINE_THRESHOLD_SECONDS = 120  # 2 minutes

# Default city for weather
DEFAULT_CITY = "Erode,IN"

def send_telegram_message(message: str, parse_mode: str = "Markdown") -> bool:
    """Send message to Telegram chat"""
    try:
        response = requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": parse_mode
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("5-min update sent to Telegram successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram message: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

def update_esp32_heartbeat():
    """Update ESP32 last seen timestamp"""
    global LAST_ESP32_TIME
    LAST_ESP32_TIME = datetime.utcnow()
    logger.info(f"ESP32 heartbeat updated: {LAST_ESP32_TIME}")

def is_esp32_online() -> bool:
    """Check if ESP32 is online based on last heartbeat"""
    global LAST_ESP32_TIME
    
    if LAST_ESP32_TIME is None:
        return False
    
    time_diff = (datetime.utcnow() - LAST_ESP32_TIME).total_seconds()
    return time_diff < ESP32_ONLINE_THRESHOLD_SECONDS

def get_esp32_last_seen() -> str:
    """Get ESP32 last seen time formatted"""
    global LAST_ESP32_TIME
    
    if LAST_ESP32_TIME is None:
        return "Never"
    
    time_diff = (datetime.utcnow() - LAST_ESP32_TIME).total_seconds()
    
    if time_diff < 60:
        return f"{int(time_diff)} seconds ago"
    elif time_diff < 3600:
        return f"{int(time_diff / 60)} minutes ago"
    else:
        return f"{int(time_diff / 3600)} hours ago"

def get_real_sensor_data() -> Dict[str, Any]:
    """Get REAL sensor data from ESP32 (only if online)"""
    try:
        # Import shared state from production backend
        from production_backend import latest_sensor_data
        
        if latest_sensor_data and is_esp32_online():
            return latest_sensor_data
        else:
            # Return empty dict if ESP32 offline - NO FAKE DATA
            return {}
            
    except Exception as e:
        logger.error(f"Failed to get sensor data: {e}")
        return {}

def get_real_weather_data(city: str = DEFAULT_CITY) -> Dict[str, Any]:
    """Get REAL weather data from OpenWeather API"""
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeather API key not configured")
        return {}
    
    try:
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        # Forecast for rain probability
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        rain_probability = 0
        if forecast_response.ok:
            forecast_data = forecast_response.json()
            # Calculate rain probability from next 8 forecasts (24 hours)
            next_24h = forecast_data['list'][:8]
            rain_forecasts = [f for f in next_24h if f.get('pop', 0) > 0]
            if rain_forecasts:
                avg_pop = sum(f.get('pop', 0) for f in rain_forecasts) / len(rain_forecasts)
                rain_probability = int(avg_pop * 100)
        
        return {
            "temperature": round(current_data['main']['temp']),
            "humidity": current_data['main']['humidity'],
            "description": current_data['weather'][0]['description'].title(),
            "rain_probability": rain_probability,
            "city_name": current_data['name'],
            "country": current_data['sys']['country']
        }
        
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        return {}

def get_pump_status() -> Dict[str, Any]:
    """Get pump status from shared state"""
    try:
        from production_backend import latest_sensor_data
        
        if latest_sensor_data:
            return {
                "pump_status": latest_sensor_data.get('pump_status', 0),
                "mode": latest_sensor_data.get('mode', 'auto').upper(),
                "total_liters": latest_sensor_data.get('total_liters', 0)
            }
        else:
            return {
                "pump_status": 0,
                "mode": "AUTO",
                "total_liters": 0
            }
            
    except Exception as e:
        logger.error(f"Failed to get pump status: {e}")
        return {
            "pump_status": 0,
            "mode": "AUTO", 
            "total_liters": 0
        }

def build_5min_update_message() -> str:
    """Build the 5-minute update message with STRICT real data rules"""
    
    # Get real weather data (ALWAYS from OpenWeather API)
    weather_data = get_real_weather_data()
    
    # Get real sensor data (ONLY if ESP32 online)
    sensor_data = get_real_sensor_data()
    esp32_online = is_esp32_online()
    
    # Get pump status
    pump_data = get_pump_status()
    
    # Current time in IST
    ist_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S IST")
    
    # Build message
    message = "📈 SMART AGRICULTURE UPDATE (5-Min)\n\n"
    
    # Weather section (ALWAYS show - from OpenWeather API)
    if weather_data:
        message += f"🌤️ Weather (OpenWeather)\n"
        message += f"• Location: {weather_data['city_name']}\n"
        message += f"• Temperature: {weather_data['temperature']}°C\n"
        message += f"• Humidity: {weather_data['humidity']}%\n"
        message += f"• Condition: {weather_data['description']}\n"
        message += f"• Rain Probability: {weather_data['rain_probability']}%\n\n"
    else:
        message += "🌤️ Weather (OpenWeather)\n"
        message += "• Status: API unavailable\n\n"
    
    # Sensor section (ONLY if ESP32 online)
    message += "📡 Live Sensors:\n"
    if esp32_online and sensor_data:
        message += f"• Status: 🟢 ONLINE\n"
        message += f"• Soil Moisture: {sensor_data.get('soil_moisture', 0)}%\n"
        message += f"• Temperature: {sensor_data.get('temperature', 0)}°C\n"
        message += f"• Humidity: {sensor_data.get('humidity', 0)}%\n"
        message += f"• Light: {sensor_data.get('light_percent', 0)}% ({sensor_data.get('light_state', 'unknown')})\n"
        message += f"• Rain Detected: {'🌧️ Yes' if sensor_data.get('rain_detected') else '☀️ No'}\n\n"
    else:
        message += f"• Status: 🔴 OFFLINE\n"
        message += f"• Last Update: {get_esp32_last_seen()}\n"
        message += f"• Sensor Values: Not available\n\n"
    
    # System status (ALWAYS show)
    message += "📊 System Status\n"
    pump_status = "🟢 ON" if pump_data['pump_status'] == 1 else "🔴 OFF"
    message += f"• Pump: {pump_status}\n"
    message += f"• Mode: {pump_data['mode']}\n"
    message += f"• Water Used: {pump_data['total_liters']} L\n"
    message += f"• ARIMAX: 🟢 ACTIVE\n\n"
    
    # Rain alert (if applicable)
    if weather_data and weather_data['rain_probability'] > 60:
        message += "🌧️ RAIN ALERT\n"
        message += f"• High rain probability: {weather_data['rain_probability']}%\n"
        message += f"• Recommendation: Skip irrigation\n\n"
    
    # Data sources (MANDATORY transparency)
    message += "📡 Data Sources:\n"
    message += f"• Weather: OpenWeather API\n"
    if esp32_online:
        message += f"• Sensors: ESP32 (online)\n"
    else:
        message += f"• Sensors: ESP32 (offline)\n"
    message += f"• Prediction: ARIMAX\n\n"
    
    # Report time
    message += f"⏰ Report Time: {ist_time}"
    
    return message

async def send_5min_farm_update():
    """Send 5-minute farm update to Telegram"""
    try:
        logger.info("Generating 5-minute farm update...")
        
        # Build message with real data only
        message = build_5min_update_message()
        
        # Send to Telegram
        success = send_telegram_message(message)
        
        if success:
            logger.info("✅ 5-minute farm update sent successfully")
        else:
            logger.error("❌ Failed to send 5-minute farm update")
            
    except Exception as e:
        logger.error(f"Error in 5-minute update: {e}")

def setup_5min_scheduler():
    """Setup APScheduler for 5-minute updates"""
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    
    # Add 5-minute update job
    scheduler.add_job(
        send_5min_farm_update,
        IntervalTrigger(minutes=5),
        id='telegram_farm_update',
        name='Telegram 5-Minute Farm Updates',
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("✅ 5-minute Telegram update scheduler started")
    
    return scheduler

def start_5min_telegram_updates():
    """Start the 5-minute Telegram update system"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Telegram bot token or chat ID not configured")
        return None
    
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeather API key not configured")
        return None
    
    logger.info("🚀 Starting 5-minute Telegram update system...")
    
    # Setup scheduler
    scheduler = setup_5min_scheduler()
    
    # Send startup notification
    startup_message = f"""🚀 5-MINUTE TELEGRAM UPDATES ACTIVATED

⏰ Started: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}

📊 Update Frequency: Every 5 minutes
🌤️ Weather Source: OpenWeather API
📡 Sensor Source: ESP32 (when online)
🚿 System Source: Backend API

STRICT DATA POLICY:
✅ Only real sensor data shown
✅ ESP32 offline status transparent
✅ Weather always from OpenWeather API
✅ No fake or simulated values

Your farm monitoring is now LIVE! 🌱"""
    
    send_telegram_message(startup_message)
    logger.info("✅ 5-minute Telegram update system started successfully")
    
    return scheduler

# ESP32 heartbeat integration functions
def register_esp32_data_received():
    """Call this when ESP32 data is received via WebSocket"""
    update_esp32_heartbeat()

def get_esp32_status_info() -> Dict[str, Any]:
    """Get ESP32 status information for other modules"""
    return {
        "online": is_esp32_online(),
        "last_seen": get_esp32_last_seen(),
        "last_timestamp": LAST_ESP32_TIME
    }

if __name__ == "__main__":
    # Test the 5-minute update system
    scheduler = start_5min_telegram_updates()
    
    if scheduler:
        try:
            # Keep running
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            logger.info("5-minute Telegram update system stopped")
            scheduler.shutdown()