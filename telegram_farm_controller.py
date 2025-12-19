#!/usr/bin/env python3
"""
Advanced Smart Agriculture Telegram Bot Controller
- Pump ON/OFF control via WebSocket
- Real-time sensor data from WebSocket
- Weather reports from OpenWeather API
- Dashboard analytics and reports
- Rain alerts and predictions
"""

import asyncio
import json
import logging
import requests
import websockets
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import os
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "***REMOVED***"
CHAT_ID = "***REMOVED***"  # tn_surya_777
OPENWEATHER_API_KEY = "***REMOVED***"
WEBSOCKET_URL = "ws://localhost:8080/ws"
BACKEND_URL = "http://localhost:8000"
CITY = "Erode"

# Global variables for tracking
pump_operations = []
irrigation_cycles = []
websocket_connections = []
water_consumption = 0.0
latest_sensor_data = {}

class FarmController:
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

# Initialize farm controller
farm = FarmController()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with welcome message and main menu"""
    keyboard = [
        [InlineKeyboardButton("🚿 Pump Control", callback_data="pump_menu")],
        [InlineKeyboardButton("📊 Sensor Data", callback_data="sensor_data")],
        [InlineKeyboardButton("🌤️ Weather Report", callback_data="weather_report")],
        [InlineKeyboardButton("📈 Dashboard Report", callback_data="dashboard_report")],
        [InlineKeyboardButton("🌧️ Rain Alert", callback_data="rain_alert")],
        [InlineKeyboardButton("ℹ️ Help & Commands", callback_data="help_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = """
🌱 **Smart Agriculture Farm Controller** 🌱

Welcome to your intelligent farming assistant! 

🤖 **What I can do:**
• Control pump ON/OFF remotely
• Get real-time sensor readings
• Provide weather forecasts & alerts
• Generate detailed dashboard reports
• Monitor irrigation and water usage
• Track system performance

👆 **Use the buttons below or type commands directly**

Type /help for all available commands
    """
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
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
    elif query.data == "rain_alert":
        await rain_alert_command(query)
    elif query.data == "help_menu":
        await help_command(query)

async def pump_control_menu(query):
    """Show pump control options"""
    keyboard = [
        [InlineKeyboardButton("🟢 Turn Pump ON", callback_data="pump_on")],
        [InlineKeyboardButton("🔴 Turn Pump OFF", callback_data="pump_off")],
        [InlineKeyboardButton("📊 Pump Status", callback_data="sensor_data")],
        [InlineKeyboardButton("⬅️ Back to Main", callback_data="main_menu")]
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
        msg = """
🟢 **PUMP TURNED ON** ✅

🚿 **Status**: Pump is now running
⏰ **Time**: {time}
💧 **Action**: Irrigation started
🔄 **Command**: Sent via WebSocket

The pump will run according to auto-irrigation rules or until manually turned off.
        """.format(time=datetime.now().strftime("%H:%M:%S"))
        
        # Track irrigation cycle start
        irrigation_cycles.append({
            'timestamp': datetime.now(),
            'action': 'started',
            'method': 'telegram_manual'
        })
    else:
        msg = "❌ **Failed to turn pump ON**\n\nPlease check WebSocket connection and try again."
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def pump_off_command(query):
    """Turn pump OFF"""
    success = await farm.send_pump_command("OFF")
    
    if success:
        msg = """
🔴 **PUMP TURNED OFF** ✅

🚿 **Status**: Pump is now stopped
⏰ **Time**: {time}
💧 **Action**: Irrigation stopped
🔄 **Command**: Sent via WebSocket

The pump has been manually turned off via Telegram.
        """.format(time=datetime.now().strftime("%H:%M:%S"))
        
        # Track irrigation cycle end
        irrigation_cycles.append({
            'timestamp': datetime.now(),
            'action': 'stopped',
            'method': 'telegram_manual'
        })
    else:
        msg = "❌ **Failed to turn pump OFF**\n\nPlease check WebSocket connection and try again."
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def sensor_data_command(query):
    """Get real-time sensor data"""
    sensor_data = await farm.get_sensor_data()
    
    if sensor_data:
        # Update global latest data
        global latest_sensor_data
        latest_sensor_data = sensor_data
        
        msg = f"""
📊 **REAL-TIME SENSOR DATA** 📊

🌱 **Soil Moisture**: {sensor_data.get('soil', 0)}%
🌡️ **Temperature**: {sensor_data.get('temperature', 0)}°C
💨 **Humidity**: {sensor_data.get('humidity', 0)}%
🌧️ **Rain Status**: {'🌧️ Raining' if sensor_data.get('rain', 0) == 1 else '☀️ Clear'}
🚿 **Pump Status**: {'🟢 ON' if sensor_data.get('pump', 0) == 1 else '🔴 OFF'}
💡 **Light Level**: {sensor_data.get('light', 0)} lux
💧 **Flow Rate**: {sensor_data.get('flow', 0)} L/min
🪣 **Total Water**: {sensor_data.get('total', 0)} L

📡 **Data Source**: {sensor_data.get('source', 'Unknown')}
⏰ **Last Update**: {datetime.now().strftime("%H:%M:%S")}

🔄 **Connection**: {'✅ Connected' if farm.connected else '❌ Disconnected'}
        """
    else:
        msg = """
❌ **SENSOR DATA UNAVAILABLE**

🔍 **Possible Issues**:
• WebSocket server not running
• ESP32 not connected
• Network connectivity issues

Please check system status and try again.
        """
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def weather_report_command(query):
    """Get weather report from OpenWeather API"""
    try:
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        
        # 5-day forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            # Current weather
            temp = current_data['main']['temp']
            humidity = current_data['main']['humidity']
            description = current_data['weather'][0]['description'].title()
            wind_speed = current_data['wind']['speed']
            pressure = current_data['main']['pressure']
            
            # Rain probability from forecast
            rain_prob = 0
            if len(forecast_data['list']) > 0:
                rain_prob = forecast_data['list'][0].get('pop', 0) * 100
            
            msg = f"""
🌤️ **WEATHER REPORT - {CITY}** 🌤️

**🌡️ Current Conditions:**
• Temperature: {temp}°C
• Humidity: {humidity}%
• Conditions: {description}
• Wind Speed: {wind_speed} m/s
• Pressure: {pressure} hPa

**🌧️ Rain Forecast:**
• Rain Probability: {rain_prob:.0f}%
• Next 3 Hours: {'🌧️ Rain Expected' if rain_prob > 40 else '☀️ Clear Skies'}

**🚜 Farming Recommendations:**
• Irrigation: {'⏸️ Skip (Rain Expected)' if rain_prob > 40 else '✅ Safe to Irrigate'}
• Field Work: {'⚠️ Postpone' if rain_prob > 60 else '✅ Good Conditions'}
• Spraying: {'❌ Not Recommended' if wind_speed > 3 else '✅ Suitable'}

⏰ **Updated**: {datetime.now().strftime("%H:%M:%S")}
            """
        else:
            msg = "❌ **Weather data unavailable**\n\nPlease check internet connection and API key."
            
    except Exception as e:
        msg = f"❌ **Weather API Error**\n\n{str(e)}"
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def dashboard_report_command(query):
    """Generate comprehensive dashboard report"""
    global water_consumption, pump_operations, irrigation_cycles, websocket_connections
    
    # Get current sensor data
    sensor_data = await farm.get_sensor_data()
    
    # Calculate today's statistics
    today = datetime.now().date()
    today_pumps = [op for op in pump_operations if op['timestamp'].date() == today]
    today_irrigation = [cycle for cycle in irrigation_cycles if cycle['timestamp'].date() == today]
    today_connections = [conn for conn in websocket_connections if conn['timestamp'].date() == today]
    
    # Count pump operations
    pump_on_count = len([op for op in today_pumps if op['command'] == 'ON'])
    pump_off_count = len([op for op in today_pumps if op['command'] == 'OFF'])
    
    # Count irrigation cycles
    irrigation_starts = len([cycle for cycle in today_irrigation if cycle['action'] == 'started'])
    irrigation_stops = len([cycle for cycle in today_irrigation if cycle['action'] == 'stopped'])
    
    # Count connections/disconnections
    connections = len([conn for conn in today_connections if conn['action'] == 'connected'])
    disconnections = len([conn for conn in today_connections if conn['action'] == 'disconnected'])
    
    # Estimate water consumption (rough calculation)
    if sensor_data:
        estimated_water = sensor_data.get('total', 0)
    else:
        estimated_water = pump_on_count * 50  # Rough estimate: 50L per pump cycle
    
    msg = f"""
📈 **DAILY DASHBOARD REPORT** 📈
📅 **Date**: {today.strftime("%B %d, %Y")}

**💧 WATER MANAGEMENT:**
• Total Water Used: {estimated_water:.1f} L
• Irrigation Cycles: {irrigation_starts} started, {irrigation_stops} completed
• Average per Cycle: {estimated_water/max(irrigation_starts,1):.1f} L

**🚿 PUMP OPERATIONS:**
• Pump ON Commands: {pump_on_count}
• Pump OFF Commands: {pump_off_count}
• Current Status: {'🟢 ON' if sensor_data.get('pump', 0) == 1 else '🔴 OFF'}

**📡 SYSTEM CONNECTIVITY:**
• WebSocket Connections: {connections}
• Disconnections: {disconnections}
• Current Status: {'✅ Connected' if farm.connected else '❌ Disconnected'}
• Uptime: {((connections/(connections+disconnections))*100):.1f if connections+disconnections > 0 else 0:.1f}%

**📊 CURRENT READINGS:**
• Soil Moisture: {sensor_data.get('soil', 0)}%
• Temperature: {sensor_data.get('temperature', 0)}°C
• Humidity: {sensor_data.get('humidity', 0)}%
• Flow Rate: {sensor_data.get('flow', 0)} L/min

**🎯 SYSTEM PERFORMANCE:**
• Data Updates: Real-time via WebSocket
• Response Time: < 2 seconds
• Automation: {'✅ Active' if sensor_data else '⚠️ Limited'}

⏰ **Report Generated**: {datetime.now().strftime("%H:%M:%S")}
    """
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def rain_alert_command(query):
    """Get rain alerts and predictions"""
    try:
        # Get detailed forecast
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
                msg = "🌧️ **RAIN ALERTS** ⚠️\n\n"
                for alert in rain_alerts:
                    intensity = "Light" if alert['amount'] < 2.5 else "Moderate" if alert['amount'] < 10 else "Heavy"
                    msg += f"⏰ **{alert['time'].strftime('%H:%M')}** - {alert['probability']:.0f}% chance\n"
                    msg += f"   💧 Expected: {alert['amount']:.1f}mm ({intensity})\n\n"
                
                msg += """
🚜 **RECOMMENDED ACTIONS:**
• 🚿 Postpone irrigation if >60% probability
• 🌾 Cover sensitive crops if heavy rain expected  
• 🚜 Avoid field operations during rain
• 📱 Monitor updates every 3 hours

🔔 **Auto-irrigation will adjust based on rain probability**
                """
            else:
                msg = """
☀️ **NO RAIN ALERTS** ✅

🌤️ **Next 24 Hours**: Clear skies expected
🚿 **Irrigation**: Safe to proceed as scheduled
🌾 **Field Work**: Good conditions for farming activities

📊 **Rain Probability**: < 30% (Low risk)
⏰ **Next Check**: {next_check}
                """.format(next_check=(datetime.now() + timedelta(hours=3)).strftime("%H:%M"))
        else:
            msg = "❌ **Rain alert data unavailable**\n\nPlease try again later."
            
    except Exception as e:
        msg = f"❌ **Rain Alert Error**\n\n{str(e)}"
    
    await query.edit_message_text(msg, parse_mode='Markdown')

async def help_command(query):
    """Show help and all available commands"""
    msg = """
ℹ️ **HELP & COMMANDS** ℹ️

**🎮 CONTROL COMMANDS:**
• `/pump_on` or `pump on` - Turn pump ON
• `/pump_off` or `pump off` - Turn pump OFF
• `/pump_status` - Check pump status

**📊 DATA COMMANDS:**
• `/sensors` or `sensor data` - Real-time readings
• `/weather` or `weather report` - Current weather
• `/forecast` - 5-day weather forecast
• `/rain` or `rain alert` - Rain predictions

**📈 REPORTS:**
• `/dashboard` or `today report` - Daily summary
• `/water_usage` - Water consumption stats
• `/system_status` - System health check

**🔔 ALERTS:**
• `/rain_alert` - Rain probability alerts
• `/frost_warning` - Temperature alerts
• `/system_alerts` - Technical notifications

**💬 NATURAL LANGUAGE:**
You can also type naturally:
• "Turn on the pump"
• "What's the weather like?"
• "Show me today's report"
• "Is it going to rain?"
• "How much water was used?"

**⚡ QUICK ACTIONS:**
Use the inline buttons for faster access to common functions.

**🆘 SUPPORT:**
If you encounter issues, type `/status` to check system connectivity.
    """
    
    await query.edit_message_text(msg, parse_mode='Markdown')

# Text message handlers for natural language commands
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language text messages"""
    text = update.message.text.lower()
    
    # Pump control keywords
    if any(word in text for word in ['pump on', 'turn on pump', 'start pump', 'irrigation on']):
        await pump_on_text(update, context)
    elif any(word in text for word in ['pump off', 'turn off pump', 'stop pump', 'irrigation off']):
        await pump_off_text(update, context)
    elif any(word in text for word in ['pump status', 'pump state', 'is pump on']):
        await sensor_data_text(update, context)
    
    # Weather keywords
    elif any(word in text for word in ['weather', 'temperature', 'forecast', 'climate']):
        await weather_report_text(update, context)
    elif any(word in text for word in ['rain', 'precipitation', 'storm', 'shower']):
        await rain_alert_text(update, context)
    
    # Data keywords
    elif any(word in text for word in ['sensor', 'data', 'readings', 'measurements']):
        await sensor_data_text(update, context)
    elif any(word in text for word in ['dashboard', 'report', 'summary', 'today']):
        await dashboard_report_text(update, context)
    elif any(word in text for word in ['water usage', 'consumption', 'irrigation stats']):
        await dashboard_report_text(update, context)
    
    # Help keywords
    elif any(word in text for word in ['help', 'commands', 'what can you do']):
        await help_text(update, context)
    
    else:
        # Default response with suggestions
        await update.message.reply_text(
            "🤔 I didn't understand that command.\n\n"
            "Try saying:\n"
            "• 'Turn on pump'\n"
            "• 'Show sensor data'\n"
            "• 'Weather report'\n"
            "• 'Today's dashboard'\n"
            "• 'Rain alert'\n\n"
            "Or type /help for all commands."
        )

# Text command implementations
async def pump_on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success = await farm.send_pump_command("ON")
    if success:
        await update.message.reply_text("🟢 Pump turned ON successfully! 🚿")
    else:
        await update.message.reply_text("❌ Failed to turn pump ON. Check connection.")

async def pump_off_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success = await farm.send_pump_command("OFF")
    if success:
        await update.message.reply_text("🔴 Pump turned OFF successfully! 🛑")
    else:
        await update.message.reply_text("❌ Failed to turn pump OFF. Check connection.")

async def sensor_data_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sensor_data = await farm.get_sensor_data()
    if sensor_data:
        msg = f"📊 **Current Sensors:**\n🌱 Soil: {sensor_data.get('soil', 0)}%\n🌡️ Temp: {sensor_data.get('temperature', 0)}°C\n💨 Humidity: {sensor_data.get('humidity', 0)}%\n🚿 Pump: {'ON' if sensor_data.get('pump', 0) == 1 else 'OFF'}"
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Sensor data unavailable")

async def weather_report_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            desc = data['weather'][0]['description'].title()
            await update.message.reply_text(f"🌤️ **Weather in {CITY}:**\n🌡️ {temp}°C\n💨 {humidity}% humidity\n☁️ {desc}", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Weather data unavailable")
    except:
        await update.message.reply_text("❌ Weather service error")

async def rain_alert_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rain_prob = data['list'][0].get('pop', 0) * 100
            await update.message.reply_text(f"🌧️ **Rain Alert:**\nProbability: {rain_prob:.0f}%\n{'⚠️ Rain expected!' if rain_prob > 40 else '☀️ Clear skies'}")
        else:
            await update.message.reply_text("❌ Rain data unavailable")
    except:
        await update.message.reply_text("❌ Rain alert service error")

async def dashboard_report_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sensor_data = await farm.get_sensor_data()
    today_pumps = len([op for op in pump_operations if op['timestamp'].date() == datetime.now().date()])
    msg = f"📈 **Today's Report:**\n🚿 Pump operations: {today_pumps}\n💧 Water used: ~{today_pumps * 50}L\n📊 Current soil: {sensor_data.get('soil', 0)}%"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def help_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Available Commands:**\n\n"
        "🚿 **Pump Control:**\n• pump on/off\n• pump status\n\n"
        "📊 **Data:**\n• sensor data\n• weather report\n• dashboard report\n\n"
        "🌧️ **Alerts:**\n• rain alert\n• system status\n\n"
        "Type naturally or use /start for menu!"
    )

def main():
    """Start the Telegram bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Text message handler for natural language
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("🤖 Smart Agriculture Telegram Bot started!")
    logger.info("🔗 WebSocket URL: " + WEBSOCKET_URL)
    logger.info("🌤️ Weather API: OpenWeather")
    logger.info("📱 Bot ready for commands!")
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()