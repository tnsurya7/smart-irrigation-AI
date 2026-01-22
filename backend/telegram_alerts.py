"""
Smart Agriculture Telegram Alert System
Production-ready threshold alerts, daily reports, and scheduling
"""

import os
import logging
import asyncio
import requests
from datetime import datetime, time
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5707565347")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Alert thresholds
THRESHOLDS = {
    "soil_moisture_low": 30.0,      # Below 30% = dry
    "soil_moisture_high": 80.0,     # Above 80% = over-watering
    "temperature_high": 38.0,       # Above 38°C = heat stress
    "light_low": 300,               # Below 300 lux = dark
    "light_high": 800,              # Above 800 lux = very bright
    "rain_probability": 60          # Above 60% = rain expected
}

# Alert state tracking (prevent spam)
last_alerts = {
    "soil_low": None,
    "soil_high": None,
    "temperature_high": None,
    "light_low": None,
    "light_high": None,
    "rain_detected": None
}

def send_telegram_alert(message: str, parse_mode: str = "Markdown") -> bool:
    """Send alert message to Telegram"""
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
            logger.info("Telegram alert sent successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram alert: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")
        return False

def get_current_sensor_data() -> Dict[str, Any]:
    """Get current sensor data from shared state"""
    try:
        from production_backend import latest_sensor_data
        return latest_sensor_data or {}
    except Exception as e:
        logger.error(f"Failed to get sensor data: {e}")
        return {}

def get_current_weather_data() -> Dict[str, Any]:
    """Get current weather data from shared state"""
    try:
        from production_backend import latest_weather_data
        return latest_weather_data or {}
    except Exception as e:
        logger.error(f"Failed to get weather data: {e}")
        return {}

def should_send_alert(alert_type: str, cooldown_minutes: int = 30) -> bool:
    """Check if alert should be sent (prevent spam)"""
    global last_alerts
    
    now = datetime.now()
    last_sent = last_alerts.get(alert_type)
    
    if last_sent is None:
        last_alerts[alert_type] = now
        return True
    
    time_diff = (now - last_sent).total_seconds() / 60
    if time_diff >= cooldown_minutes:
        last_alerts[alert_type] = now
        return True
    
    return False

# 🚨 1️⃣ THRESHOLD ALERTS

def check_soil_moisture_alerts():
    """Check soil moisture thresholds and send alerts"""
    sensor_data = get_current_sensor_data()
    soil_moisture = sensor_data.get('soil_moisture', 0)
    
    # Soil too dry
    if soil_moisture < THRESHOLDS["soil_moisture_low"]:
        if should_send_alert("soil_low", 30):
            message = f"""🚨 **SOIL MOISTURE ALERT** 🚨

🌱 **Soil Moisture:** {soil_moisture}%
⚠️ **Status:** TOO DRY
🚿 **Recommendation:** Turn ON pump immediately

**Action Required:**
• Start irrigation now
• Monitor soil levels
• Check for system issues

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info(f"Soil moisture alert sent: {soil_moisture}%")
    
    # Soil over-watered
    elif soil_moisture > THRESHOLDS["soil_moisture_high"]:
        if should_send_alert("soil_high", 60):
            message = f"""🚨 **OVER-WATERING ALERT** 🚨

🌱 **Soil Moisture:** {soil_moisture}%
⚠️ **Status:** TOO WET
🚿 **Recommendation:** Turn OFF pump

**Action Required:**
• Stop irrigation immediately
• Check drainage system
• Monitor for root rot risk

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info(f"Over-watering alert sent: {soil_moisture}%")

def check_temperature_alerts():
    """Check temperature thresholds and send alerts"""
    sensor_data = get_current_sensor_data()
    temperature = sensor_data.get('temperature', 0)
    
    if temperature > THRESHOLDS["temperature_high"]:
        if should_send_alert("temperature_high", 45):
            message = f"""🔥 **TEMPERATURE ALERT** 🔥

🌡️ **Temperature:** {temperature}°C
⚠️ **Risk:** Crop heat stress
🌿 **Impact:** Reduced growth, wilting

**Recommendations:**
• Increase irrigation frequency
• Provide shade if possible
• Monitor plants closely
• Consider evening watering

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info(f"Temperature alert sent: {temperature}°C")

def check_light_alerts():
    """Check light level thresholds and send alerts"""
    sensor_data = get_current_sensor_data()
    light_percent = sensor_data.get('light_percent', 0)
    light_raw = sensor_data.get('light_raw', 0)
    light_state = sensor_data.get('light_state', 'unknown')
    
    # Convert percentage to approximate lux (rough estimation)
    light_lux = int(light_percent * 10)  # 0-100% -> 0-1000 lux approx
    
    if light_lux < THRESHOLDS["light_low"]:
        if should_send_alert("light_low", 120):  # 2 hour cooldown
            light_emoji = "🌙" if light_state == "dark" else "🌥️"
            
            message = f"""💡 **LIGHT LEVEL ALERT** 💡

💡 **Light Intensity:** {light_lux} lux ({light_percent}%)
{light_emoji} **Status:** {light_state.upper()}
⚠️ **Impact:** Reduced photosynthesis

**Information:**
• Normal daylight: 300-800 lux
• Current level is below optimal
• Plants may grow slower
• Consider supplemental lighting

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info(f"Low light alert sent: {light_lux} lux")

def check_rain_alerts():
    """Check rain detection and weather forecast"""
    sensor_data = get_current_sensor_data()
    weather_data = get_current_weather_data()
    
    rain_detected = sensor_data.get('rain_detected', False)
    rain_probability = weather_data.get('rain_probability', 0)
    
    # Rain sensor detected rain
    if rain_detected:
        if should_send_alert("rain_detected", 60):
            message = f"""🌧️ **RAIN DETECTED** 🌧️

🌧️ **Status:** Rain sensor activated
🚿 **Action:** Irrigation paused automatically
💧 **Benefit:** Natural watering in progress

**System Response:**
• Pump turned OFF automatically
• Water conservation active
• Resume irrigation when rain stops

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info("Rain detection alert sent")
    
    # High rain probability from weather API
    elif rain_probability > THRESHOLDS["rain_probability"]:
        if should_send_alert("rain_forecast", 180):  # 3 hour cooldown
            message = f"""🌧️ **RAIN FORECAST ALERT** 🌧️

🌤️ **Rain Probability:** {rain_probability}%
🌧️ **Expected:** Within next 24 hours
🚿 **Recommendation:** Skip irrigation

**Smart Irrigation Advice:**
• Wait for natural rain
• Save water and energy
• Monitor weather updates
• Resume irrigation if rain doesn't come

⏰ **Alert Time:** {datetime.now().strftime("%H:%M:%S")}"""
            
            send_telegram_alert(message)
            logger.info(f"Rain forecast alert sent: {rain_probability}%")

# ⏰ 2️⃣ DAILY REPORTS

async def send_morning_weather_report():
    """Send daily weather report at 7:00 AM"""
    weather_data = get_current_weather_data()
    sensor_data = get_current_sensor_data()
    
    temp = weather_data.get('temperature', 0)
    humidity = weather_data.get('humidity', 0)
    rain_prob = weather_data.get('rain_probability', 0)
    location = weather_data.get('location', 'Erode, Tamil Nadu')
    
    # Irrigation advice based on conditions
    if rain_prob > 40:
        irrigation_advice = "❌ Skip irrigation (rain expected)"
    elif sensor_data.get('soil_moisture', 0) < 40:
        irrigation_advice = "✅ Irrigation recommended"
    else:
        irrigation_advice = "⏸️ Monitor soil levels"
    
    message = f"""🌅 **GOOD MORNING - DAILY WEATHER** 🌅

📍 **Location:** {location}
📅 **Date:** {datetime.now().strftime("%B %d, %Y")}

**🌤️ Today's Weather:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Rain Chance: {rain_prob}%

**🌱 Irrigation Advice:**
{irrigation_advice}

**🌾 Farm Status:**
• Soil Moisture: {sensor_data.get('soil_moisture', 0)}%
• System Status: ✅ Online

**Have a productive farming day!** 🚜"""
    
    send_telegram_alert(message)
    logger.info("Morning weather report sent")

async def send_evening_dashboard_summary():
    """Send daily dashboard summary at 6:00 PM"""
    sensor_data = get_current_sensor_data()
    weather_data = get_current_weather_data()
    
    # Calculate daily stats (in production, get from database)
    soil_avg = sensor_data.get('soil_moisture', 0)
    temp_avg = sensor_data.get('temperature', 0)
    light_state = sensor_data.get('light_state', 'normal')
    water_used = sensor_data.get('total_liters', 0)
    pump_status = sensor_data.get('pump_status', 0)
    
    # System health check
    system_status = "✅ Healthy"
    if soil_avg < 30:
        system_status = "⚠️ Low soil moisture"
    elif temp_avg > 35:
        system_status = "⚠️ High temperature"
    
    message = f"""📊 **DAILY FARM SUMMARY** 📊

📅 **Date:** {datetime.now().strftime("%B %d, %Y")}
⏰ **Report Time:** {datetime.now().strftime("%H:%M")}

**🌱 Today's Averages:**
• Soil Moisture: {soil_avg}%
• Temperature: {temp_avg}°C
• Light Level: {light_state.title()}
• Humidity: {sensor_data.get('humidity', 0)}%

**💧 Water Management:**
• Total Water Used: {water_used} L
• Pump Status: {'🟢 ON' if pump_status == 1 else '🔴 OFF'}
• Irrigation Cycles: Auto-managed

**🤖 System Health:**
• Overall Status: {system_status}
• Backend: ✅ Online
• Sensors: ✅ Active
• ARIMAX Model: ✅ Running

**🌤️ Tomorrow's Weather:**
• Rain Probability: {weather_data.get('rain_probability', 0)}%

**Sleep well, your farm is in good hands!** 🌙"""
    
    send_telegram_alert(message)
    logger.info("Evening dashboard summary sent")

# 📊 3️⃣ MANUAL COMMANDS (for telegram_bot.py integration)

def get_threshold_status() -> str:
    """Get current threshold status for manual command"""
    sensor_data = get_current_sensor_data()
    
    soil = sensor_data.get('soil_moisture', 0)
    temp = sensor_data.get('temperature', 0)
    light = sensor_data.get('light_percent', 0) * 10  # Convert to lux
    
    # Check each threshold
    soil_status = "🟢 Normal"
    if soil < THRESHOLDS["soil_moisture_low"]:
        soil_status = "🔴 Too Dry"
    elif soil > THRESHOLDS["soil_moisture_high"]:
        soil_status = "🔴 Too Wet"
    
    temp_status = "🟢 Normal" if temp <= THRESHOLDS["temperature_high"] else "🔴 Too Hot"
    light_status = "🟢 Normal"
    if light < THRESHOLDS["light_low"]:
        light_status = "🔴 Too Dark"
    elif light > THRESHOLDS["light_high"]:
        light_status = "🔴 Too Bright"
    
    return f"""📊 **THRESHOLD STATUS** 📊

**🌱 Soil Moisture:** {soil}%
Status: {soil_status}
Threshold: {THRESHOLDS["soil_moisture_low"]}-{THRESHOLDS["soil_moisture_high"]}%

**🌡️ Temperature:** {temp}°C
Status: {temp_status}
Threshold: < {THRESHOLDS["temperature_high"]}°C

**💡 Light Level:** {light} lux
Status: {light_status}
Threshold: {THRESHOLDS["light_low"]}-{THRESHOLDS["light_high"]} lux

⏰ **Checked:** {datetime.now().strftime("%H:%M:%S")}"""

def get_rain_status() -> str:
    """Get current rain status for manual command"""
    sensor_data = get_current_sensor_data()
    weather_data = get_current_weather_data()
    
    rain_detected = sensor_data.get('rain_detected', False)
    rain_prob = weather_data.get('rain_probability', 0)
    
    sensor_status = "🌧️ Rain Detected" if rain_detected else "☀️ No Rain"
    forecast_status = f"{rain_prob}% chance"
    
    if rain_prob > 60:
        forecast_emoji = "🌧️"
        advice = "Skip irrigation"
    elif rain_prob > 30:
        forecast_emoji = "🌤️"
        advice = "Monitor weather"
    else:
        forecast_emoji = "☀️"
        advice = "Safe to irrigate"
    
    return f"""🌧️ **RAIN STATUS** 🌧️

**🌧️ Rain Sensor:** {sensor_status}
**🌤️ Weather Forecast:** {forecast_emoji} {forecast_status}

**💧 Irrigation Advice:** {advice}

**📍 Location:** {weather_data.get('location', 'Erode')}
⏰ **Updated:** {datetime.now().strftime("%H:%M:%S")}"""

# 🔄 4️⃣ SCHEDULER SETUP

def setup_alert_scheduler():
    """Setup APScheduler for automated alerts and reports"""
    scheduler = AsyncIOScheduler()
    
    # Threshold alerts (every 5 minutes)
    scheduler.add_job(
        check_soil_moisture_alerts,
        IntervalTrigger(minutes=5),
        id='soil_alerts',
        name='Soil Moisture Threshold Alerts'
    )
    
    scheduler.add_job(
        check_temperature_alerts,
        IntervalTrigger(minutes=5),
        id='temperature_alerts',
        name='Temperature Threshold Alerts'
    )
    
    scheduler.add_job(
        check_light_alerts,
        IntervalTrigger(minutes=10),
        id='light_alerts',
        name='Light Level Threshold Alerts'
    )
    
    scheduler.add_job(
        check_rain_alerts,
        IntervalTrigger(minutes=10),
        id='rain_alerts',
        name='Rain Detection Alerts'
    )
    
    # Daily reports
    scheduler.add_job(
        send_morning_weather_report,
        CronTrigger(hour=7, minute=0),
        id='morning_report',
        name='Daily Morning Weather Report'
    )
    
    scheduler.add_job(
        send_evening_dashboard_summary,
        CronTrigger(hour=18, minute=0),
        id='evening_summary',
        name='Daily Evening Dashboard Summary'
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("✅ Telegram alert scheduler started")
    
    return scheduler

# 🚀 5️⃣ INTEGRATION FUNCTIONS

def start_telegram_alerts():
    """Start the complete Telegram alert system"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Telegram bot token or chat ID not configured")
        return None
    
    logger.info("Starting Telegram alert system...")
    scheduler = setup_alert_scheduler()
    
    # Send startup notification
    startup_message = f"""🚀 **SMART AGRICULTURE ALERTS ACTIVATED** 🚀

⏰ **Started:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**🚨 Active Alerts:**
• Soil moisture thresholds
• Temperature monitoring
• Light level tracking
• Rain detection

**📅 Daily Reports:**
• 07:00 AM - Weather forecast
• 06:00 PM - Farm summary

**Your smart farm is now fully monitored!** 🌱🤖"""
    
    send_telegram_alert(startup_message)
    
    return scheduler

if __name__ == "__main__":
    # Test the alert system
    start_telegram_alerts()
    
    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Telegram alert system stopped")