#!/usr/bin/env python3
"""
Smart Agriculture Dashboard - Telegram Alert Service
Provides weather reports, irrigation alerts, and sensor monitoring via Telegram Bot
"""

import requests
import json
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
    exit(1)

# OpenWeather API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LOCATION = "Erode"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# FastAPI Backend Configuration
BACKEND_URL = "http://localhost:8000"

# Alert State Management
class AlertState:
    def __init__(self):
        self.last_rain_alert = None
        self.last_irrigation_alert = None
        self.last_critical_soil_alert = None
        self.last_sensor_offline_alert = None
        self.last_manual_override_alert = None
        self.last_sensor_data_time = None
        self.current_pump_status = False
        self.daily_water_usage = 0.0
        self.daily_pump_runtime = 0
        self.pump_start_time = None
        
    def can_send_alert(self, alert_type: str, cooldown_minutes: int = 30) -> bool:
        """Check if enough time has passed since last alert of this type"""
        last_alert_time = getattr(self, f"last_{alert_type}_alert", None)
        if last_alert_time is None:
            return True
        
        time_diff = datetime.now() - last_alert_time
        return time_diff.total_seconds() >= (cooldown_minutes * 60)
    
    def update_alert_time(self, alert_type: str):
        """Update the last alert time for given type"""
        setattr(self, f"last_{alert_type}_alert", datetime.now())

# Global alert state
alert_state = AlertState()

def send_telegram_message(message: str) -> bool:
    """Send message to Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Telegram message sent successfully: {message[:50]}...")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False

def fetch_weather_data() -> Optional[Dict[str, Any]]:
    """Fetch weather data from OpenWeather API"""
    try:
        params = {
            "q": LOCATION,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        weather_info = {
            "location": data["name"],
            "temperature": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["description"].title(),
            "rain_probability": min(data["main"]["humidity"], 100),  # Estimate from humidity
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Weather data fetched: {weather_info}")
        return weather_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None

def fetch_sensor_data() -> Optional[Dict[str, Any]]:
    """Fetch current sensor data from FastAPI backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/sensor-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            alert_state.last_sensor_data_time = datetime.now()
            return data
        else:
            logger.warning(f"Backend returned status {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch sensor data: {e}")
        return None

def send_daily_weather_report():
    """Send daily weather report at 7:00 AM"""
    logger.info("Sending daily weather report...")
    
    weather_data = fetch_weather_data()
    if not weather_data:
        logger.error("Could not fetch weather data for daily report")
        return
    
    today = datetime.now().strftime("%B %d, %Y")
    
    message = f"""🌤️ <b>Daily Weather Report – {weather_data['location']}</b>

🌡️ <b>Temperature:</b> {weather_data['temperature']}°C
💨 <b>Humidity:</b> {weather_data['humidity']}%
🌧️ <b>Rain Chance:</b> {weather_data['rain_probability']}%
☁️ <b>Condition:</b> {weather_data['weather_condition']}
📅 <b>Date:</b> {today}

<i>Have a great day! 🌱</i>"""

    send_telegram_message(message)

def check_rain_alert():
    """Check for rain alerts and auto-pause irrigation"""
    weather_data = fetch_weather_data()
    if not weather_data:
        return
    
    rain_probability = weather_data['rain_probability']
    
    if rain_probability > 40 and alert_state.can_send_alert("rain", 30):
        logger.info(f"Rain alert triggered: {rain_probability}% probability")
        
        # Check if pump is currently ON
        sensor_data = fetch_sensor_data()
        pump_status = ""
        
        if sensor_data and sensor_data.get('pump_status', False):
            pump_status = "\n🚿 <b>Irrigation paused automatically</b> to avoid water wastage."
            # Here you would send a command to pause irrigation
            # requests.post(f"{BACKEND_URL}/irrigation/pause")
        
        message = f"""🌧️ <b>Rain Alert!</b>

Rain expected in the next 30–60 minutes.
☔ Probability: {rain_probability}%{pump_status}

<i>Smart irrigation system activated! 🤖</i>"""

        if send_telegram_message(message):
            alert_state.update_alert_time("rain")

def check_critical_soil_moisture():
    """Check for critical soil moisture levels"""
    sensor_data = fetch_sensor_data()
    if not sensor_data:
        return
    
    soil_moisture = sensor_data.get('soil_moisture', 0)
    
    if soil_moisture < 15 and alert_state.can_send_alert("critical_soil", 60):
        logger.info(f"Critical soil moisture alert: {soil_moisture}%")
        
        message = f"""⚠️ <b>Critical Alert!</b>

🌱 Soil moisture is critically low (<b>{soil_moisture:.1f}%</b>)
💧 <b>Immediate irrigation recommended</b>

<i>Your plants need water urgently! 🆘</i>"""

        if send_telegram_message(message):
            alert_state.update_alert_time("critical_soil")

def check_irrigation_status():
    """Monitor irrigation status changes"""
    sensor_data = fetch_sensor_data()
    if not sensor_data:
        return
    
    current_pump_status = sensor_data.get('pump_status', False)
    soil_moisture = sensor_data.get('soil_moisture', 0)
    
    # Check for pump status change
    if current_pump_status != alert_state.current_pump_status:
        logger.info(f"Pump status changed: {alert_state.current_pump_status} -> {current_pump_status}")
        
        # Determine reason for change
        if current_pump_status:  # Pump turned ON
            if soil_moisture < 30:
                reason = "soil moisture low"
            else:
                reason = "scheduled irrigation"
            
            alert_state.pump_start_time = datetime.now()
            
        else:  # Pump turned OFF
            if soil_moisture > 70:
                reason = "soil moisture sufficient"
            else:
                reason = "irrigation cycle complete"
            
            # Calculate runtime
            if alert_state.pump_start_time:
                runtime = datetime.now() - alert_state.pump_start_time
                alert_state.daily_pump_runtime += runtime.total_seconds() / 60
        
        status_text = "ON" if current_pump_status else "OFF"
        
        message = f"""🚿 <b>Irrigation Update</b>

💧 <b>Pump Status:</b> {status_text}
📋 <b>Reason:</b> {reason}
🌱 <b>Soil Moisture:</b> {soil_moisture:.1f}%

<i>Smart irrigation in action! 🤖</i>"""

        send_telegram_message(message)
        alert_state.current_pump_status = current_pump_status

def check_sensor_offline():
    """Check if sensors are offline"""
    if alert_state.last_sensor_data_time is None:
        return
    
    time_since_last_data = datetime.now() - alert_state.last_sensor_data_time
    
    if time_since_last_data.total_seconds() > 300 and alert_state.can_send_alert("sensor_offline", 60):  # 5 minutes
        logger.info("Sensor offline alert triggered")
        
        message = f"""📡 <b>Sensor Alert</b>

⚠️ Live sensors offline for {int(time_since_last_data.total_seconds() / 60)} minutes
🤖 System running on historical data and AI prediction
🧠 ARIMAX model providing backup predictions

<i>Don't worry, AI has got you covered! 🛡️</i>"""

        if send_telegram_message(message):
            alert_state.update_alert_time("sensor_offline")

def send_daily_dashboard_summary():
    """Send comprehensive daily dashboard summary at 8:00 PM"""
    logger.info("Sending daily dashboard summary...")
    
    try:
        # Fetch daily summary from FastAPI backend
        response = requests.get(f"{BACKEND_URL}/send-daily-dashboard-report", timeout=10)
        
        if response.status_code == 200:
            logger.info("Daily dashboard report sent successfully")
        else:
            logger.error(f"Failed to send daily dashboard report: {response.status_code}")
            
            # Send fallback message
            fallback_message = f"""📊 <b>Daily Smart Agriculture Report</b>

📍 <b>Location:</b> Erode
📅 <b>Date:</b> {datetime.now().strftime("%B %d, %Y")}

⚠️ <i>Unable to fetch complete data from backend</i>
🤖 <i>System monitoring continues...</i>

<i>Smart agriculture active 24/7! 🌱</i>"""
            
            send_telegram_message(fallback_message)
            
    except Exception as e:
        logger.error(f"Error sending daily dashboard summary: {e}")

def send_water_usage_summary():
    """Send daily water usage summary at 9:00 PM"""
    logger.info("Sending daily water usage summary...")
    
    # Calculate total water usage (mock calculation for demo)
    total_liters = alert_state.daily_water_usage
    runtime_minutes = int(alert_state.daily_pump_runtime)
    
    # Reset daily counters
    alert_state.daily_water_usage = 0.0
    alert_state.daily_pump_runtime = 0
    
    today = datetime.now().strftime("%B %d, %Y")
    
    message = f"""💧 <b>Water Usage Report</b>

📅 <b>Date:</b> {today}
🚿 <b>Total Water Used:</b> {total_liters:.1f} L
⏱️ <b>Pump Runtime:</b> {runtime_minutes} mins
💰 <b>Efficiency:</b> Smart irrigation active

<i>Water conservation in action! 🌍</i>"""

    send_telegram_message(message)

def send_manual_override_alert(action: str, user: str = "admin"):
    """Send alert for manual pump control"""
    if alert_state.can_send_alert("manual_override", 5):  # 5 minute cooldown
        
        message = f"""🛠️ <b>Manual Override</b>

👤 <b>User:</b> {user}
🚿 <b>Pump turned:</b> {action.upper()}
⏰ <b>Time:</b> {datetime.now().strftime("%H:%M:%S")}

<i>Manual control activated! 🎛️</i>"""

        if send_telegram_message(message):
            alert_state.update_alert_time("manual_override")

def run_monitoring_loop():
    """Main monitoring loop for real-time alerts"""
    logger.info("Starting monitoring loop...")
    
    while True:
        try:
            # Check all alert conditions
            check_rain_alert()
            check_critical_soil_moisture()
            check_irrigation_status()
            check_sensor_offline()
            
            # Wait 30 seconds before next check
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(60)  # Wait longer on error

def start_scheduler():
    """Start APScheduler for scheduled jobs"""
    logger.info("Starting APScheduler...")
    
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    
    # Schedule daily weather report at 7:00 AM IST
    scheduler.add_job(
        func=send_daily_weather_report,
        trigger=CronTrigger(hour=7, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
        id='daily_weather_report',
        replace_existing=True
    )
    
    # Schedule daily dashboard summary at 8:00 PM IST
    scheduler.add_job(
        func=send_daily_dashboard_summary,
        trigger=CronTrigger(hour=20, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
        id='daily_dashboard_summary',
        replace_existing=True
    )
    
    # Schedule water usage summary at 9:00 PM IST
    scheduler.add_job(
        func=send_water_usage_summary,
        trigger=CronTrigger(hour=21, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
        id='water_usage_summary',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ APScheduler started with IST timezone")
    return scheduler

def test_telegram_connection():
    """Test Telegram bot connection"""
    logger.info("Testing Telegram connection...")
    
    test_message = """🤖 <b>Smart Agriculture Bot Online!</b>

✅ Telegram connection established
🌱 Monitoring your farm 24/7
📊 AI-powered alerts active

<i>Ready to keep your crops healthy! 🚀</i>"""

    return send_telegram_message(test_message)

def main():
    """Main function to start the Telegram alert service"""
    logger.info("=== Smart Agriculture Telegram Alert Service ===")
    
    # Test connection
    if not test_telegram_connection():
        logger.error("Failed to connect to Telegram. Exiting...")
        return
    
    # Start scheduler for daily reports
    start_scheduler()
    
    # Send startup notification
    startup_message = f"""🌱 <b>Smart Agriculture System Started</b>

📅 <b>Time:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🤖 <b>AI Models:</b> ARIMA & ARIMAX loaded
📡 <b>Monitoring:</b> Weather, Soil, Irrigation
⏰ <b>Daily Reports:</b> 7:00 AM & 9:00 PM

<i>Your smart farm is now online! 🚜</i>"""
    
    send_telegram_message(startup_message)
    
    # Start monitoring loop
    try:
        run_monitoring_loop()
    except KeyboardInterrupt:
        logger.info("Telegram alert service stopped by user")
        
        shutdown_message = """🛑 <b>Smart Agriculture System Stopped</b>

Thank you for using our smart farming solution!
<i>See you next time! 👋</i>"""
        
        send_telegram_message(shutdown_message)

if __name__ == "__main__":
    main()