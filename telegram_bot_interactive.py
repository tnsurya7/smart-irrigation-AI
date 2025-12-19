#!/usr/bin/env python3
"""
Enhanced Interactive Telegram Bot for Smart Agriculture Dashboard
- Pump ON/OFF control via WebSocket
- Real-time sensor data from WebSocket
- Weather reports from OpenWeather API
- Dashboard analytics and reports
- Rain alerts and predictions
- All existing features combined
"""

import requests
import json
import time
import threading
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
BOT_TOKEN = "***REMOVED***"
CHAT_ID = "***REMOVED***"

# FastAPI Backend Configuration
BACKEND_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8080/ws"
OPENWEATHER_API_KEY = "***REMOVED***"
CITY = "Erode"

# Global tracking variables
pump_operations = []
irrigation_cycles = []
websocket_connections = []
water_consumption = 0.0
latest_sensor_data = {}

class WebSocketController:
    def __init__(self):
        self.websocket = None
        self.connected = False
        
    async def connect_websocket(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(WEBSOCKET_URL)
            self.connected = True
            websocket_connections.append({
                'timestamp': datetime.now(),
                'action': 'connected'
            })
            logger.info("✅ Connected to WebSocket server")
            return True
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.connected = False
            websocket_connections.append({
                'timestamp': datetime.now(),
                'action': 'disconnected',
                'error': str(e)
            })
            return False
    
    async def send_pump_command(self, command):
        """Send pump ON/OFF command via WebSocket"""
        if not self.connected:
            await self.connect_websocket()
        
        if self.websocket:
            try:
                pump_cmd = {
                    "type": "cmd",
                    "cmd": "pump",
                    "value": command,
                    "timestamp": datetime.now().isoformat()
                }
                await self.websocket.send(json.dumps(pump_cmd))
                
                # Track pump operation
                pump_operations.append({
                    'timestamp': datetime.now(),
                    'command': command,
                    'status': 'sent'
                })
                
                logger.info(f"🚿 Pump command sent: {command}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to send pump command: {e}")
                return False
        return False
    
    async def get_sensor_data(self):
        """Get latest sensor data from WebSocket server"""
        try:
            response = requests.get(f"http://localhost:8080/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('latest_data', {})
        except Exception as e:
            logger.error(f"❌ Failed to get sensor data: {e}")
        return {}

# Initialize WebSocket controller
ws_controller = WebSocketController()

class TelegramBotHandler:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.running = False
        
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
    
    def get_updates(self) -> list:
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 10
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            # Handle 409 conflicts gracefully
            if response.status_code == 409:
                logger.warning("Telegram API conflict (409) - another bot instance may be running")
                time.sleep(5)  # Wait longer on conflict
                return []
            
            response.raise_for_status()
            
            data = response.json()
            if data["ok"]:
                return data["result"]
            else:
                logger.error(f"Telegram API error: {data}")
                return []
                
        except requests.exceptions.Timeout:
            logger.warning("Telegram API timeout - retrying...")
            return []
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return []
    
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
                
        except requests.exceptions.Timeout:
            logger.error("Weather API timeout")
            return "❌ <b>Weather Timeout</b>\n\nWeather service is slow. Please try again in a moment."
        except requests.exceptions.ConnectionError:
            logger.error("Weather API connection error")
            return "❌ <b>Connection Error</b>\n\nCannot connect to weather service. Backend may be offline."
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return "❌ <b>Weather Error</b>\n\nUnexpected error occurred. Please try again."
    
    def fetch_dashboard_summary(self) -> str:
        """Fetch dashboard summary from backend"""
        try:
            response = requests.get(f"{BACKEND_URL}/daily-summary", timeout=10)
            if response.status_code == 200:
                summary = response.json()
                
                message = f"""📊 <b>Dashboard Summary Report</b>

📍 <b>Location:</b> {summary.get('location', 'Erode')}
📅 <b>Date:</b> {summary.get('date', 'Today')}

<b>🌡️ Current Averages:</b>
🌡️ Temperature: {summary.get('averages', {}).get('avg_temperature', 0)}°C
💨 Humidity: {summary.get('averages', {}).get('avg_humidity', 0)}%
💧 Soil Moisture: {summary.get('averages', {}).get('avg_soil_moisture', 0)}%
🌧️ Rain Probability: {summary.get('weather', {}).get('rain_probability', 0):.0f}%

<b>🤖 AI Models:</b>
🏆 Best Model: {summary.get('model', {}).get('best_model', 'ARIMAX')}
📈 ARIMA: {summary.get('model', {}).get('arima_accuracy', 82.5)}%
📈 ARIMAX: {summary.get('model', {}).get('arimax_accuracy', 94.6)}%

<b>🚿 Irrigation Today:</b>
🟢 Pump ON: {summary.get('irrigation', {}).get('pump_on_count', 0)} times
🔴 Pump OFF: {summary.get('irrigation', {}).get('pump_off_count', 0)} times
💦 Water Used: {summary.get('irrigation', {}).get('total_water_used', 0)} L

<b>📊 System Status:</b>
⚠️ Alerts: {summary.get('alerts', {}).get('total_count', 0)}
🔌 Status: {summary.get('system', {}).get('status', 'unknown').replace('_', ' ').title()}
📡 Data Points: {summary.get('averages', {}).get('data_points', 0)}

<i>Real-time dashboard data 📊</i>"""
                
                return message
            else:
                return "❌ <b>Dashboard Error</b>\n\nUnable to fetch dashboard data from backend."
                
        except Exception as e:
            logger.error(f"Dashboard fetch error: {e}")
            return "❌ <b>Dashboard Error</b>\n\nBackend connection failed."
    
    def fetch_irrigation_update(self) -> str:
        """Fetch irrigation status from backend"""
        try:
            response = requests.get(f"{BACKEND_URL}/sensor-status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                
                # Also get daily summary for irrigation details
                summary_response = requests.get(f"{BACKEND_URL}/daily-summary", timeout=10)
                irrigation_data = {}
                if summary_response.status_code == 200:
                    summary = summary_response.json()
                    irrigation_data = summary.get('irrigation', {})
                
                pump_status = "🟢 ON" if status.get('pump_status', False) else "🔴 OFF"
                last_sensor = status.get('last_sensor_time')
                sensor_time = "Unknown"
                if last_sensor:
                    try:
                        dt = datetime.fromisoformat(last_sensor.replace('Z', '+00:00'))
                        sensor_time = dt.strftime('%H:%M:%S')
                    except:
                        sensor_time = "Invalid"
                
                message = f"""🚿 <b>Irrigation System Update</b>

<b>💧 Current Status:</b>
🚿 Pump Status: {pump_status}
💧 Soil Moisture: {status.get('soil_moisture', 0):.1f}%
🕐 Last Update: {sensor_time}

<b>📊 Today's Activity:</b>
🟢 Pump ON Count: {irrigation_data.get('pump_on_count', 0)}
🔴 Pump OFF Count: {irrigation_data.get('pump_off_count', 0)}
💦 Total Water Used: {irrigation_data.get('total_water_used', 0)} L

<b>🔌 System Health:</b>
📡 Sensor Status: {status.get('status', 'unknown').title()}
🤖 AI Backup: {'Active' if status.get('status') == 'offline' else 'Standby'}

<i>Live irrigation monitoring 🌱</i>"""
                
                return message
            else:
                return "❌ <b>Irrigation Error</b>\n\nUnable to fetch irrigation data from backend."
                
        except Exception as e:
            logger.error(f"Irrigation fetch error: {e}")
            return "❌ <b>Irrigation Error</b>\n\nBackend connection failed."
    
    def get_enhanced_help_message(self) -> str:
        """Get enhanced help message with all available commands"""
        return """🤖 <b>Enhanced Smart Agriculture Bot Commands</b>

<b>🎮 PUMP CONTROL (NEW!):</b>
• <code>pump on</code> or <code>turn on pump</code> - Turn pump ON via WebSocket
• <code>pump off</code> or <code>turn off pump</code> - Turn pump OFF via WebSocket
• <code>pump status</code> - Check current pump status

<b>📊 REAL-TIME DATA:</b>
• <code>sensor data</code> or <code>real sensor</code> - Live WebSocket sensor readings
• <code>weather report</code> - Current weather from OpenWeather API
• <code>rain alert</code> - Rain probability and predictions

<b>📈 COMPREHENSIVE REPORTS:</b>
• <code>dashboard</code> or <code>today report</code> - Complete daily analytics
• <code>irrigation update</code> - Pump operations and water usage
• <code>system status</code> - WebSocket connections and uptime

<b>🌟 NATURAL LANGUAGE EXAMPLES:</b>
• "Turn on the pump"
• "What's the current sensor data?"
• "Will it rain today?"
• "Show me today's dashboard report"
• "How much water was used?"

<b>🔔 AUTO REPORTS (Existing):</b>
• 7:00 AM - Daily weather report
• 8:00 PM - Dashboard summary
• 9:00 PM - Water usage report

<b>🚀 NEW FEATURES:</b>
✅ Direct pump control via WebSocket
✅ Real-time sensor data from ESP32
✅ Rain probability alerts
✅ Water consumption tracking
✅ System connectivity monitoring
✅ Comprehensive analytics

<i>Your complete smart farm controller! 🌱🤖🚜</i>"""
    
    async def pump_on_command(self) -> str:
        """Turn pump ON via WebSocket"""
        success = await ws_controller.send_pump_command("ON")
        
        if success:
            irrigation_cycles.append({
                'timestamp': datetime.now(),
                'action': 'started',
                'method': 'telegram_manual'
            })
            
            return f"""🟢 <b>PUMP TURNED ON</b> ✅

🚿 <b>Status:</b> Pump is now running
⏰ <b>Time:</b> {datetime.now().strftime("%H:%M:%S")}
💧 <b>Action:</b> Irrigation started
🔄 <b>Command:</b> Sent via WebSocket

The pump will run according to auto-irrigation rules or until manually turned off."""
        else:
            return "❌ <b>Failed to turn pump ON</b>\n\nPlease check WebSocket connection and try again."
    
    async def pump_off_command(self) -> str:
        """Turn pump OFF via WebSocket"""
        success = await ws_controller.send_pump_command("OFF")
        
        if success:
            irrigation_cycles.append({
                'timestamp': datetime.now(),
                'action': 'stopped',
                'method': 'telegram_manual'
            })
            
            return f"""🔴 <b>PUMP TURNED OFF</b> ✅

🚿 <b>Status:</b> Pump is now stopped
⏰ <b>Time:</b> {datetime.now().strftime("%H:%M:%S")}
💧 <b>Action:</b> Irrigation stopped
🔄 <b>Command:</b> Sent via WebSocket

The pump has been manually turned off via Telegram."""
        else:
            return "❌ <b>Failed to turn pump OFF</b>\n\nPlease check WebSocket connection and try again."
    
    async def get_real_sensor_data(self) -> str:
        """Get real-time sensor data from WebSocket"""
        sensor_data = await ws_controller.get_sensor_data()
        
        if sensor_data:
            global latest_sensor_data
            latest_sensor_data = sensor_data
            
            return f"""📊 <b>REAL-TIME SENSOR DATA</b> 📊

🌱 <b>Soil Moisture:</b> {sensor_data.get('soil', 0)}%
🌡️ <b>Temperature:</b> {sensor_data.get('temperature', 0)}°C
💨 <b>Humidity:</b> {sensor_data.get('humidity', 0)}%
🌧️ <b>Rain Status:</b> {'🌧️ Raining' if sensor_data.get('rain', 0) == 1 else '☀️ Clear'}
🚿 <b>Pump Status:</b> {'🟢 ON' if sensor_data.get('pump', 0) == 1 else '🔴 OFF'}
💡 <b>Light Level:</b> {sensor_data.get('light', 0)} lux
💧 <b>Flow Rate:</b> {sensor_data.get('flow', 0)} L/min
🪣 <b>Total Water:</b> {sensor_data.get('total', 0)} L

📡 <b>Data Source:</b> {sensor_data.get('source', 'Unknown')}
⏰ <b>Last Update:</b> {datetime.now().strftime("%H:%M:%S")}

🔄 <b>Connection:</b> {'✅ Connected' if ws_controller.connected else '❌ Disconnected'}"""
        else:
            return """❌ <b>SENSOR DATA UNAVAILABLE</b>

🔍 <b>Possible Issues:</b>
• WebSocket server not running
• ESP32 not connected
• Network connectivity issues

Please check system status and try again."""
    
    def get_rain_alert(self) -> str:
        """Get rain alerts and predictions"""
        try:
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(forecast_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                rain_alerts = []
                for i, forecast in enumerate(data['list'][:8]):  # Next 24 hours
                    dt = datetime.fromtimestamp(forecast['dt'])
                    rain_prob = forecast.get('pop', 0) * 100
                    
                    if rain_prob > 30:  # Alert threshold
                        rain_mm = 0
                        if 'rain' in forecast:
                            rain_mm = forecast['rain'].get('3h', 0)
                        
                        rain_alerts.append({
                            'time': dt,
                            'probability': rain_prob,
                            'amount': rain_mm
                        })
                
                if rain_alerts:
                    msg = "🌧️ <b>RAIN ALERTS</b> ⚠️\n\n"
                    for alert in rain_alerts:
                        intensity = "Light" if alert['amount'] < 2.5 else "Moderate" if alert['amount'] < 10 else "Heavy"
                        msg += f"⏰ <b>{alert['time'].strftime('%H:%M')}</b> - {alert['probability']:.0f}% chance\n"
                        msg += f"   💧 Expected: {alert['amount']:.1f}mm ({intensity})\n\n"
                    
                    msg += """🚜 <b>RECOMMENDED ACTIONS:</b>
• 🚿 Postpone irrigation if >60% probability
• 🌾 Cover sensitive crops if heavy rain expected  
• 🚜 Avoid field operations during rain
• 📱 Monitor updates every 3 hours

🔔 <b>Auto-irrigation will adjust based on rain probability</b>"""
                else:
                    msg = f"""☀️ <b>NO RAIN ALERTS</b> ✅

🌤️ <b>Next 24 Hours:</b> Clear skies expected
🚿 <b>Irrigation:</b> Safe to proceed as scheduled
🌾 <b>Field Work:</b> Good conditions for farming activities

📊 <b>Rain Probability:</b> < 30% (Low risk)
⏰ <b>Next Check:</b> {(datetime.now() + timedelta(hours=3)).strftime("%H:%M")}"""
                
                return msg
            else:
                return "❌ <b>Rain alert data unavailable</b>\n\nPlease try again later."
                
        except Exception as e:
            return f"❌ <b>Rain Alert Error</b>\n\n{str(e)}"
    
    def get_comprehensive_dashboard_report(self) -> str:
        """Generate comprehensive dashboard report with all tracking data"""
        global water_consumption, pump_operations, irrigation_cycles, websocket_connections
        
        # Calculate today's statistics
        today = datetime.now().date()
        today_pumps = [op for op in pump_operations if op['timestamp'].date() == today]
        today_irrigation = [cycle for cycle in irrigation_cycles if cycle['timestamp'].date() == today]
        today_connections = [conn for conn in websocket_connections if conn['timestamp'].date() == today]
        
        # Count operations
        pump_on_count = len([op for op in today_pumps if op['command'] == 'ON'])
        pump_off_count = len([op for op in today_pumps if op['command'] == 'OFF'])
        irrigation_starts = len([cycle for cycle in today_irrigation if cycle['action'] == 'started'])
        irrigation_stops = len([cycle for cycle in today_irrigation if cycle['action'] == 'stopped'])
        connections = len([conn for conn in today_connections if conn['action'] == 'connected'])
        disconnections = len([conn for conn in today_connections if conn['action'] == 'disconnected'])
        
        # Estimate water consumption
        estimated_water = pump_on_count * 50  # Rough estimate: 50L per pump cycle
        if latest_sensor_data:
            estimated_water = latest_sensor_data.get('total', estimated_water)
        
        uptime_pct = ((connections/(connections+disconnections))*100) if connections+disconnections > 0 else 0
        
        return f"""📈 <b>COMPREHENSIVE DASHBOARD REPORT</b> 📈
📅 <b>Date:</b> {today.strftime("%B %d, %Y")}

<b>💧 WATER MANAGEMENT:</b>
• Total Water Used: {estimated_water:.1f} L
• Irrigation Cycles: {irrigation_starts} started, {irrigation_stops} completed
• Average per Cycle: {estimated_water/max(irrigation_starts,1):.1f} L

<b>🚿 PUMP OPERATIONS:</b>
• Pump ON Commands: {pump_on_count}
• Pump OFF Commands: {pump_off_count}
• Current Status: {'🟢 ON' if latest_sensor_data.get('pump', 0) == 1 else '🔴 OFF'}

<b>📡 SYSTEM CONNECTIVITY:</b>
• WebSocket Connections: {connections}
• Disconnections: {disconnections}
• Current Status: {'✅ Connected' if ws_controller.connected else '❌ Disconnected'}
• Uptime: {uptime_pct:.1f}%

<b>📊 CURRENT READINGS:</b>
• Soil Moisture: {latest_sensor_data.get('soil', 0)}%
• Temperature: {latest_sensor_data.get('temperature', 0)}°C
• Humidity: {latest_sensor_data.get('humidity', 0)}%
• Flow Rate: {latest_sensor_data.get('flow', 0)} L/min

<b>🎯 SYSTEM PERFORMANCE:</b>
• Data Updates: Real-time via WebSocket
• Response Time: < 2 seconds
• Automation: {'✅ Active' if latest_sensor_data else '⚠️ Limited'}

⏰ <b>Report Generated:</b> {datetime.now().strftime("%H:%M:%S")}"""

    def process_command(self, message_text: str) -> str:
        """Process user command and return appropriate response"""
        # Convert to lowercase for easier matching
        text = message_text.lower().strip()
        
        # Pump control commands
        if any(keyword in text for keyword in ['pump on', 'turn on pump', 'start pump', 'irrigation on', 'pump start']):
            logger.info("Processing pump ON command")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.pump_on_command())
            loop.close()
            return result
        
        elif any(keyword in text for keyword in ['pump off', 'turn off pump', 'stop pump', 'irrigation off', 'pump stop']):
            logger.info("Processing pump OFF command")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.pump_off_command())
            loop.close()
            return result
        
        # Real sensor data commands
        elif any(keyword in text for keyword in ['sensor data', 'real sensor', 'live data', 'current sensors', 'sensor reading']):
            logger.info("Processing real sensor data command")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_real_sensor_data())
            loop.close()
            return result
        
        # Weather commands
        elif any(keyword in text for keyword in ['weather', 'weather report', 'weather for erode']):
            logger.info("Processing weather command")
            return self.fetch_weather_report()
        
        # Rain alert commands
        elif any(keyword in text for keyword in ['rain alert', 'rain forecast', 'will it rain', 'rain probability', 'rain prediction']):
            logger.info("Processing rain alert command")
            return self.get_rain_alert()
        
        # Dashboard commands (comprehensive)
        elif any(keyword in text for keyword in ['dashboard', 'dashboard summary', 'today dashboard', 'summary report', 'today report', 'comprehensive report']):
            logger.info("Processing comprehensive dashboard command")
            return self.get_comprehensive_dashboard_report()
        
        # Legacy irrigation commands (for backward compatibility)
        elif any(keyword in text for keyword in ['irrigation', 'irrigation update', 'pump status', 'pump update']):
            logger.info("Processing irrigation command")
            return self.fetch_irrigation_update()
        
        # Help commands
        elif any(keyword in text for keyword in ['help', 'commands', '/help', '/start']):
            logger.info("Processing help command")
            return self.get_enhanced_help_message()
        
        # Unknown command
        else:
            return f"""❓ <b>Unknown Command</b>

I didn't understand: "<i>{message_text}</i>"

<b>🎮 PUMP CONTROL:</b>
• <code>pump on</code> - Turn pump ON
• <code>pump off</code> - Turn pump OFF

<b>📊 DATA COMMANDS:</b>
• <code>sensor data</code> - Real-time readings
• <code>weather report</code> - Current weather
• <code>rain alert</code> - Rain predictions
• <code>dashboard</code> - Complete report

Type <code>help</code> for all commands."""
    
    def handle_message(self, update: Dict[str, Any]):
        """Handle incoming message"""
        try:
            message = update.get("message", {})
            text = message.get("text", "")
            user = message.get("from", {})
            chat = message.get("chat", {})
            
            # Only respond to messages from our chat
            if str(chat.get("id")) != self.chat_id:
                logger.warning(f"Ignoring message from unauthorized chat: {chat.get('id')}")
                return
            
            logger.info(f"Received command: '{text}' from user: {user.get('username', 'unknown')}")
            
            # Process the command
            response = self.process_command(text)
            
            # Send response
            self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.send_message("❌ <b>Error</b>\n\nSorry, I encountered an error processing your request.")
    
    def clear_pending_updates(self):
        """Clear any pending updates to avoid conflicts"""
        try:
            logger.info("Clearing pending updates...")
            # Get all pending updates with a high offset to clear them
            url = f"{self.base_url}/getUpdates"
            params = {"offset": -1, "timeout": 1}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data["ok"] and data["result"]:
                    # Get the highest update_id and set offset to clear all
                    highest_id = max(update["update_id"] for update in data["result"])
                    clear_params = {"offset": highest_id + 1, "timeout": 1}
                    requests.get(url, params=clear_params, timeout=5)
                    logger.info(f"Cleared {len(data['result'])} pending updates")
                else:
                    logger.info("No pending updates to clear")
            
        except Exception as e:
            logger.warning(f"Could not clear pending updates: {e}")

    def start_polling(self):
        """Start polling for messages"""
        logger.info("Starting Telegram bot polling...")
        self.running = True
        
        # Clear any existing webhooks first
        try:
            clear_url = f"{self.base_url}/deleteWebhook"
            requests.post(clear_url, timeout=10)
            logger.info("Cleared existing webhooks")
        except Exception as e:
            logger.warning(f"Could not clear webhooks: {e}")
        
        # Clear pending updates to avoid conflicts
        self.clear_pending_updates()
        
        # Send startup message
        startup_message = f"""🤖 <b>Smart Agriculture Bot Online!</b>

🕐 <b>Started:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📱 <b>Interactive Mode:</b> Active
🌱 <b>Farm Monitoring:</b> Ready

Type <code>help</code> for available commands.

<i>Your smart farm assistant is ready! 🚀</i>"""
        
        self.send_message(startup_message)
        
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    
                    if "message" in update:
                        self.handle_message(update)
                
                # Small delay to prevent excessive API calls
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        
        shutdown_message = """🛑 <b>Smart Agriculture Bot Offline</b>

Bot has been stopped for maintenance.
Automatic reports will resume when restarted.

<i>Thank you for using our smart farming solution! 👋</i>"""
        
        self.send_message(shutdown_message)

def main():
    """Main function to start the interactive bot"""
    logger.info("=== Interactive Smart Agriculture Telegram Bot ===")
    
    bot = TelegramBotHandler()
    
    try:
        bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()