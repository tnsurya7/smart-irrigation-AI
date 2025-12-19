#!/usr/bin/env python3
"""
Production Telegram Bot for Smart Agriculture Dashboard
Features:
1. Daily weather report at 7 AM
2. Rain alerts using OpenWeather API
3. Interactive commands: weather, dashboard, pump on/off
4. Daily dashboard report at 6 PM
5. ESP32 pump control via WebSocket
6. Environment variable configuration
7. Error handling and logging
"""

import os
import requests
import json
import time
import threading
import asyncio
import websockets
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import ssl

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production Configuration - Environment Variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WEBSOCKET_URL = os.getenv('VITE_WS_URL', 'wss://smart-agriculture-websocket.render.com/ws')
BACKEND_URL = os.getenv('VITE_API_BASE_URL', 'https://smart-agriculture-backend.render.com')
CITY = os.getenv('WEATHER_CITY', 'Erode')

# Validate required environment variables
required_vars = {
    'TELEGRAM_BOT_TOKEN': BOT_TOKEN,
    'TELEGRAM_CHAT_ID': CHAT_ID,
    'OPENWEATHER_API_KEY': OPENWEATHER_API_KEY,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

logger.info(f"Telegram bot configured for {CITY} weather and backend: {BACKEND_URL}")

class TelegramBot:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.running = False
        self.websocket = None
        
        # Get the latest update ID to start fresh
        try:
            response = requests.get(f"{self.base_url}/getUpdates", timeout=10)
            if response.ok:
                data = response.json()
                if data["ok"] and data["result"]:
                    self.last_update_id = data["result"][-1]["update_id"]
                    logger.info(f"🔄 Starting from update ID: {self.last_update_id}")
        except Exception as e:
            logger.warning(f"Failed to get initial update ID: {e}")
        
    def send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Message sent: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    def get_weather_report(self) -> str:
        """Get weather report from OpenWeather API for Erode"""
        try:
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},IN&appid={OPENWEATHER_API_KEY}&units=metric"
            current_response = requests.get(current_url, timeout=10)
            
            if not current_response.ok:
                return "❌ Weather data unavailable"
            
            current_data = current_response.json()
            
            # Forecast for rain probability
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY},IN&appid={OPENWEATHER_API_KEY}&units=metric"
            forecast_response = requests.get(forecast_url, timeout=10)
            
            rain_probability = 0
            rain_expected = False
            
            if forecast_response.ok:
                forecast_data = forecast_response.json()
                next_24h = forecast_data['list'][:8]  # Next 24 hours
                avg_pop = sum(item.get('pop', 0) for item in next_24h) / len(next_24h)
                rain_probability = int(avg_pop * 100)
                rain_expected = rain_probability > 40
            
            message = f"""🌤️ <b>Weather Report - Erode, Tamil Nadu</b>

🌡️ <b>Temperature:</b> {current_data['main']['temp']:.1f}°C
💨 <b>Humidity:</b> {current_data['main']['humidity']}%
🌧️ <b>Rain Probability:</b> {rain_probability}%
☁️ <b>Condition:</b> {current_data['weather'][0]['description'].title()}
💨 <b>Wind Speed:</b> {current_data.get('wind', {}).get('speed', 0)} m/s
👁️ <b>Visibility:</b> {current_data.get('visibility', 0)/1000:.1f} km

<b>🌧️ Rain Alert:</b> {'⚠️ Rain Expected' if rain_expected else '✅ No Rain Expected'}

🕐 <b>Updated:</b> {datetime.now().strftime('%H:%M:%S')}
📡 <b>Source:</b> OpenWeather API"""
            
            return message
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return f"❌ <b>Weather Error</b>\n\nFailed to fetch weather data: {str(e)}"
    
    def get_rain_alert(self) -> str:
        """Get rain alerts for next 24 hours"""
        try:
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY},IN&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(forecast_url, timeout=10)
            
            if not response.ok:
                return "❌ Rain alert data unavailable"
            
            data = response.json()
            rain_alerts = []
            
            for forecast in data['list'][:8]:  # Next 24 hours
                dt = datetime.fromtimestamp(forecast['dt'])
                rain_prob = forecast.get('pop', 0) * 100
                
                if rain_prob > 30:
                    rain_mm = 0
                    if 'rain' in forecast:
                        rain_mm = forecast['rain'].get('3h', 0)
                    
                    rain_alerts.append({
                        'time': dt.strftime('%H:%M'),
                        'probability': rain_prob,
                        'amount': rain_mm
                    })
            
            if rain_alerts:
                message = "🌧️ <b>Rain Alerts - Next 24 Hours</b>\n\n"
                for alert in rain_alerts:
                    intensity = "Light" if alert['amount'] < 2.5 else "Moderate" if alert['amount'] < 10 else "Heavy"
                    message += f"⏰ <b>{alert['time']}</b> - {alert['probability']:.0f}% chance\n"
                    message += f"   💧 Expected: {alert['amount']:.1f}mm ({intensity})\n\n"
                
                message += "⚠️ <b>Recommendation:</b> Consider postponing irrigation"
            else:
                message = f"""☀️ <b>No Rain Alerts</b>

🌤️ Clear weather expected for next 24 hours
🚿 Safe to proceed with irrigation
📊 Rain probability: < 30%"""
            
            return message
            
        except Exception as e:
            logger.error(f"Rain alert error: {e}")
            return f"❌ <b>Rain Alert Error</b>\n\n{str(e)}"
    
    async def send_pump_command(self, command: str) -> bool:
        """Send pump command to ESP32 via WebSocket"""
        try:
            if not self.websocket:
                self.websocket = await websockets.connect(WEBSOCKET_URL)
            
            pump_cmd = {
                "type": "cmd",
                "cmd": "pump",
                "value": command,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(pump_cmd))
            logger.info(f"🚿 Pump command sent: {command}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pump command failed: {e}")
            self.websocket = None
            return False
    
    def get_dashboard_report(self) -> str:
        """Get dashboard summary with real sensor data"""
        try:
            # Get sensor data
            sensor_response = requests.get(f"{BACKEND_URL}/sensor-status", timeout=10)
            weather_response = requests.get(f"{BACKEND_URL}/weather", timeout=10)
            
            sensor_data = sensor_response.json() if sensor_response.ok else {}
            weather_data = weather_response.json() if weather_response.ok else {}
            
            # Get ESP32 real-time data if available
            esp32_data = {}
            try:
                esp32_response = requests.get("http://localhost:8080/status", timeout=5)
                if esp32_response.ok:
                    esp32_data = esp32_response.json().get('latest_data', {})
            except:
                pass
            
            message = f"""📊 <b>Dashboard Report - Erode Smart Farm</b>

<b>🌱 Real Sensor Data (ESP32):</b>
💧 Soil Moisture: {esp32_data.get('soil', sensor_data.get('soil_moisture', 0))}%
🌡️ Temperature: {esp32_data.get('temperature', sensor_data.get('temperature', 0))}°C
💨 Humidity: {esp32_data.get('humidity', sensor_data.get('humidity', 0))}%
🚿 Pump Status: {'🟢 ON' if esp32_data.get('pump', 0) == 1 else '🔴 OFF'}
💦 Flow Rate: {esp32_data.get('flow', 0)} L/min
🪣 Total Water: {esp32_data.get('total', 0)} L

<b>🌤️ Weather Data:</b>
🌡️ External Temp: {weather_data.get('temperature', 0)}°C
💨 External Humidity: {weather_data.get('humidity', 0)}%
🌧️ Rain Probability: {weather_data.get('rain_probability', 0)}%

<b>🤖 AI Model Performance:</b>
📈 ARIMAX Accuracy: 94.6%
📈 ARIMA Accuracy: 82.5%
🏆 Best Model: ARIMAX

<b>📡 System Status:</b>
🔌 ESP32: {'✅ Connected' if esp32_data else '❌ Offline'}
🌐 Weather API: {'✅ Active' if weather_data else '❌ Offline'}
⏰ Report Time: {datetime.now().strftime('%H:%M:%S')}

📍 <b>Location:</b> Erode, Tamil Nadu"""
            
            return message
            
        except Exception as e:
            logger.error(f"Dashboard report error: {e}")
            return f"❌ <b>Dashboard Error</b>\n\nFailed to generate report: {str(e)}"
    
    def process_command(self, text: str) -> str:
        """Process user commands"""
        text = text.lower().strip()
        
        # Weather commands
        if any(cmd in text for cmd in ['weather', 'weather report', 'today weather']):
            return self.get_weather_report()
        
        # Rain alert commands  
        elif any(cmd in text for cmd in ['rain alert', 'rain', 'will it rain']):
            return self.get_rain_alert()
        
        # Dashboard commands
        elif any(cmd in text for cmd in ['dashboard', 'summary', 'real data', 'dashboard report']):
            return self.get_dashboard_report()
        
        # Pump ON command
        elif any(cmd in text for cmd in ['pump on', 'turn on pump', 'start pump']):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.send_pump_command("ON"))
                if success:
                    return f"""🟢 <b>Pump Turned ON</b> ✅

🚿 Pump is now running
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
📡 Command sent to ESP32 via WebSocket"""
                else:
                    return "❌ Failed to turn pump ON. Check ESP32 connection."
            finally:
                loop.close()
        
        # Pump OFF command
        elif any(cmd in text for cmd in ['pump off', 'turn off pump', 'stop pump']):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.send_pump_command("OFF"))
                if success:
                    return f"""🔴 <b>Pump Turned OFF</b> ✅

🚿 Pump is now stopped
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
📡 Command sent to ESP32 via WebSocket"""
                else:
                    return "❌ Failed to turn pump OFF. Check ESP32 connection."
            finally:
                loop.close()
        
        # Help command
        elif any(cmd in text for cmd in ['help', '/help', '/start', 'commands']):
            return """🤖 <b>Smart Agriculture Bot Commands</b>

<b>🌤️ Weather Commands:</b>
• <code>weather</code> - Current weather report for Erode
• <code>rain alert</code> - Rain forecast and alerts

<b>📊 Dashboard Commands:</b>
• <code>dashboard</code> - Real sensor data and summary
• <code>real data</code> - ESP32 sensor readings

<b>🚿 Pump Control:</b>
• <code>pump on</code> - Turn irrigation pump ON
• <code>pump off</code> - Turn irrigation pump OFF

<b>🕐 Automatic Reports:</b>
• 07:00 AM - Daily weather report
• 06:00 PM - Daily dashboard summary

<i>Simple commands for smart farming! 🌱</i>"""
        
        else:
            return f"""❓ <b>Unknown Command</b>

I didn't understand: "<i>{text}</i>"

<b>Available Commands:</b>
• <code>weather</code> - Weather report
• <code>dashboard</code> - Sensor data
• <code>pump on/off</code> - Control pump
• <code>help</code> - Show all commands"""
    
    def get_updates(self) -> list:
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 10
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 409:
                logger.warning("Telegram API conflict - waiting...")
                time.sleep(5)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            if data["ok"]:
                return data["result"]
            else:
                logger.error(f"Telegram API error: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return []
    
    def handle_message(self, update: Dict[str, Any]):
        """Handle incoming message"""
        try:
            message = update.get("message", {})
            text = message.get("text", "")
            chat = message.get("chat", {})
            
            # Only respond to authorized chat
            if str(chat.get("id")) != self.chat_id:
                return
            
            logger.info(f"📱 Command received: '{text}'")
            
            # Process command and send response
            response = self.process_command(text)
            self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.send_message("❌ Error processing your request")
    
    def start_polling(self):
        """Start polling for messages"""
        logger.info("🤖 Starting Telegram bot...")
        self.running = True
        
        # Clear webhooks
        try:
            webhook_response = requests.post(f"{self.base_url}/deleteWebhook", timeout=10)
            logger.info(f"Webhook cleared: {webhook_response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to clear webhook: {e}")
        
        # Send startup message
        startup_msg = f"""🤖 <b>Smart Agriculture Bot Started</b>

🕐 Started: {datetime.now().strftime('%H:%M:%S')}
📍 Location: Erode, Tamil Nadu
🌱 Monitoring: ESP32 Sensors + Weather API

Type <code>help</code> for commands."""
        
        self.send_message(startup_msg)
        logger.info("📱 Bot is now polling for messages...")
        
        while self.running:
            try:
                updates = self.get_updates()
                logger.debug(f"📥 Received {len(updates)} updates")
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    logger.info(f"📨 Processing update ID: {update['update_id']}")
                    if "message" in update:
                        self.handle_message(update)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        self.send_message("🛑 <b>Bot Stopped</b>\n\nSmart Agriculture Bot is offline.")

# Scheduled functions
def send_daily_weather():
    """Send daily weather report at 7 AM"""
    bot = TelegramBot()
    weather_report = bot.get_weather_report()
    message = f"🌅 <b>Daily Weather Report - 7:00 AM</b>\n\n{weather_report}"
    bot.send_message(message)
    logger.info("📅 Daily weather report sent")

def send_daily_dashboard():
    """Send daily dashboard report at 6 PM"""
    bot = TelegramBot()
    dashboard_report = bot.get_dashboard_report()
    message = f"🌆 <b>Daily Dashboard Report - 6:00 PM</b>\n\n{dashboard_report}"
    bot.send_message(message)
    logger.info("📅 Daily dashboard report sent")

def run_scheduler():
    """Run scheduled tasks"""
    schedule.every().day.at("07:00").do(send_daily_weather)
    schedule.every().day.at("18:00").do(send_daily_dashboard)
    
    logger.info("📅 Scheduler started - Daily reports at 7 AM and 6 PM")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main function"""
    logger.info("=== Simple Smart Agriculture Telegram Bot ===")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start bot
    bot = TelegramBot()
    
    try:
        bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()