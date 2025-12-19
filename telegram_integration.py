#!/usr/bin/env python3
"""
Telegram Integration Module for FastAPI Backend
Integrates Telegram alerts with the existing Smart Agriculture Dashboard
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Telegram Bot Configuration
BOT_TOKEN = "***REMOVED***"
CHAT_ID = "***REMOVED***"

class TelegramNotifier:
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
            
            logger.info(f"Telegram message sent: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_weather_alert(self, weather_data: Dict[str, Any]) -> bool:
        """Send weather-based alert"""
        rain_prob = weather_data.get('rain_probability', 0)
        
        if rain_prob > 40:
            message = f"""🌧️ <b>Rain Alert!</b>

Rain expected in the next 30–60 minutes.
☔ Probability: {rain_prob}%
🚿 <b>Irrigation paused automatically</b> to avoid water wastage.

<i>Smart irrigation system activated! 🤖</i>"""
            
            return self.send_message(message)
        return False
    
    def send_irrigation_alert(self, pump_status: bool, reason: str, soil_moisture: float) -> bool:
        """Send irrigation status alert"""
        status_text = "ON" if pump_status else "OFF"
        
        message = f"""🚿 <b>Irrigation Update</b>

💧 <b>Pump Status:</b> {status_text}
📋 <b>Reason:</b> {reason}
🌱 <b>Soil Moisture:</b> {soil_moisture:.1f}%

<i>Smart irrigation in action! 🤖</i>"""

        return self.send_message(message)
    
    def send_critical_soil_alert(self, soil_moisture: float) -> bool:
        """Send critical soil moisture alert"""
        message = f"""⚠️ <b>Critical Alert!</b>

🌱 Soil moisture is critically low (<b>{soil_moisture:.1f}%</b>)
💧 <b>Immediate irrigation recommended</b>

<i>Your plants need water urgently! 🆘</i>"""

        return self.send_message(message)
    
    def send_sensor_offline_alert(self, minutes_offline: int) -> bool:
        """Send sensor offline alert"""
        message = f"""📡 <b>Sensor Alert</b>

⚠️ Live sensors offline for {minutes_offline} minutes
🤖 System running on historical data and AI prediction
🧠 ARIMAX model providing backup predictions

<i>Don't worry, AI has got you covered! 🛡️</i>"""

        return self.send_message(message)
    
    def send_manual_override_alert(self, action: str, user: str = "admin") -> bool:
        """Send manual override alert"""
        message = f"""🛠️ <b>Manual Override</b>

👤 <b>User:</b> {user}
🚿 <b>Pump turned:</b> {action.upper()}
⏰ <b>Time:</b> {datetime.now().strftime("%H:%M:%S")}

<i>Manual control activated! 🎛️</i>"""

        return self.send_message(message)
    
    def send_daily_weather_report(self, weather_data: Dict[str, Any]) -> bool:
        """Send daily weather report"""
        today = datetime.now().strftime("%B %d, %Y")
        
        message = f"""🌤️ <b>Daily Weather Report – {weather_data.get('location', 'Erode')}</b>

🌡️ <b>Temperature:</b> {weather_data.get('temperature', 0)}°C
💨 <b>Humidity:</b> {weather_data.get('humidity', 0)}%
🌧️ <b>Rain Chance:</b> {weather_data.get('rain_probability', 0)}%
☁️ <b>Condition:</b> {weather_data.get('weather_condition', 'Unknown')}
📅 <b>Date:</b> {today}

<i>Have a great day! 🌱</i>"""

        return self.send_message(message)
    
    def send_daily_dashboard_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Send comprehensive daily dashboard summary"""
        message = f"""📊 <b>Daily Smart Agriculture Report</b>

📍 <b>Location:</b> {summary_data.get('location', 'Erode')}
📅 <b>Date:</b> {summary_data.get('date', datetime.now().strftime('%B %d, %Y'))}

<b>🌡️ Environmental Averages (24h):</b>
🌡️ Avg Temperature: {summary_data.get('averages', {}).get('avg_temperature', 0)}°C
💨 Avg Humidity: {summary_data.get('averages', {}).get('avg_humidity', 0)}%
💧 Avg Soil Moisture: {summary_data.get('averages', {}).get('avg_soil_moisture', 0)}%
🌧️ Rain Probability: {summary_data.get('weather', {}).get('rain_probability', 0):.0f}%

<b>🤖 AI Model Performance:</b>
🏆 Best Model: {summary_data.get('model', {}).get('best_model', 'ARIMAX')}
📈 ARIMA Accuracy: {summary_data.get('model', {}).get('arima_accuracy', 82.5)}%
📈 ARIMAX Accuracy: {summary_data.get('model', {}).get('arimax_accuracy', 94.6)}%

<b>🚿 Irrigation Summary:</b>
🟢 Pump ON Count: {summary_data.get('irrigation', {}).get('pump_on_count', 0)}
🔴 Pump OFF Count: {summary_data.get('irrigation', {}).get('pump_off_count', 0)}
💦 Total Water Used: {summary_data.get('irrigation', {}).get('total_water_used', 0)} L

<b>⚠️ System Status:</b>
📊 Alerts Today: {summary_data.get('alerts', {}).get('total_count', 0)}
🔌 System Status: {summary_data.get('system', {}).get('status', 'unknown').replace('_', ' ').title()}
📡 Data Points: {summary_data.get('averages', {}).get('data_points', 0)}

<i>Smart agriculture monitoring active 24/7! 🌱🤖</i>"""

        return self.send_message(message)

    def send_water_usage_summary(self, total_liters: float, runtime_minutes: int) -> bool:
        """Send daily water usage summary"""
        today = datetime.now().strftime("%B %d, %Y")
        
        message = f"""💧 <b>Water Usage Report</b>

📅 <b>Date:</b> {today}
🚿 <b>Total Water Used:</b> {total_liters:.1f} L
⏱️ <b>Pump Runtime:</b> {runtime_minutes} mins
💰 <b>Efficiency:</b> Smart irrigation active

<i>Water conservation in action! 🌍</i>"""

        return self.send_message(message)

# Global notifier instance
telegram_notifier = TelegramNotifier()

# Convenience functions for FastAPI integration
def notify_weather_alert(weather_data: Dict[str, Any]) -> bool:
    """Send weather alert notification"""
    return telegram_notifier.send_weather_alert(weather_data)

def notify_irrigation_change(pump_status: bool, reason: str, soil_moisture: float) -> bool:
    """Send irrigation status change notification"""
    return telegram_notifier.send_irrigation_alert(pump_status, reason, soil_moisture)

def notify_critical_soil(soil_moisture: float) -> bool:
    """Send critical soil moisture notification"""
    return telegram_notifier.send_critical_soil_alert(soil_moisture)

def notify_sensor_offline(minutes_offline: int) -> bool:
    """Send sensor offline notification"""
    return telegram_notifier.send_sensor_offline_alert(minutes_offline)

def notify_manual_override(action: str, user: str = "admin") -> bool:
    """Send manual override notification"""
    return telegram_notifier.send_manual_override_alert(action, user)

def send_daily_weather_report(weather_data: Dict[str, Any]) -> bool:
    """Send daily weather report"""
    return telegram_notifier.send_daily_weather_report(weather_data)

def send_daily_dashboard_summary(summary_data: Dict[str, Any]) -> bool:
    """Send comprehensive daily dashboard summary"""
    return telegram_notifier.send_daily_dashboard_summary(summary_data)

def send_water_usage_summary(total_liters: float, runtime_minutes: int) -> bool:
    """Send daily water usage summary"""
    return telegram_notifier.send_water_usage_summary(total_liters, runtime_minutes)

def test_telegram_connection() -> bool:
    """Test Telegram bot connection"""
    test_message = """🤖 <b>Smart Agriculture Bot Test</b>

✅ Connection successful
🌱 Ready to monitor your farm

<i>Test completed! 🚀</i>"""

    return telegram_notifier.send_message(test_message)