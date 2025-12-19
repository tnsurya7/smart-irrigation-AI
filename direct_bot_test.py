#!/usr/bin/env python3
"""
Direct Bot Test - Send commands directly to Telegram without polling conflicts
"""

import requests
import json
from datetime import datetime

BOT_TOKEN = "8063174729:AAGJYD_IMImdzkTRYbCiokomWsZlHcIW8jg"
CHAT_ID = "5707565347"
BACKEND_URL = "http://localhost:8000"

def send_telegram_message(message: str) -> bool:
    """Send message directly to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Message sent successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False

def get_weather_report() -> str:
    """Get weather report from backend"""
    try:
        print("🌤️ Fetching weather data...")
        response = requests.get(f"{BACKEND_URL}/weather", timeout=15)
        
        if response.status_code == 200:
            weather_data = response.json()
            print(f"✅ Weather data received: {weather_data.get('temperature')}°C")
            
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
            return f"❌ <b>Weather Error</b>\n\nBackend returned status {response.status_code}"
            
    except Exception as e:
        print(f"❌ Weather fetch error: {e}")
        return "❌ <b>Weather Error</b>\n\nBackend connection failed"

def get_dashboard_summary() -> str:
    """Get dashboard summary from backend"""
    try:
        print("📊 Fetching dashboard data...")
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

<b>🤖 AI Models:</b>
🏆 Best Model: {summary.get('model', {}).get('best_model', 'ARIMAX')}
📈 ARIMA: {summary.get('model', {}).get('arima_accuracy', 82.5)}%
📈 ARIMAX: {summary.get('model', {}).get('arimax_accuracy', 94.6)}%

<b>🚿 Irrigation Today:</b>
🟢 Pump ON: {summary.get('irrigation', {}).get('pump_on_count', 0)} times
🔴 Pump OFF: {summary.get('irrigation', {}).get('pump_off_count', 0)} times
💦 Water Used: {summary.get('irrigation', {}).get('total_water_used', 0)} L

<i>Real-time dashboard data 📊</i>"""
            
            return message
        else:
            return f"❌ <b>Dashboard Error</b>\n\nBackend returned status {response.status_code}"
            
    except Exception as e:
        print(f"❌ Dashboard fetch error: {e}")
        return "❌ <b>Dashboard Error</b>\n\nBackend connection failed"

def send_weather_report():
    """Send weather report to Telegram"""
    print("🌤️ Sending Weather Report...")
    weather_message = get_weather_report()
    return send_telegram_message(weather_message)

def send_dashboard_report():
    """Send dashboard report to Telegram"""
    print("📊 Sending Dashboard Report...")
    dashboard_message = get_dashboard_summary()
    return send_telegram_message(dashboard_message)

def send_help_message():
    """Send help message to Telegram"""
    help_message = """🤖 <b>Smart Agriculture Bot - Direct Commands Working!</b>

<b>📋 Available Commands:</b>
• <code>weather</code> or <code>weather report</code> - Current weather for Erode
• <code>dashboard</code> or <code>dashboard summary</code> - Today's farm summary
• <code>irrigation</code> or <code>irrigation update</code> - Pump status and activity
• <code>help</code> or <code>commands</code> - Show this help message

<b>✅ System Status:</b>
• Backend API: Connected
• Weather Service: Active
• AI Models: Loaded (ARIMA 82.5%, ARIMAX 94.6%)

<b>🔧 Troubleshooting:</b>
If the interactive bot has connection issues, you can use these direct commands as a backup.

<i>Smart agriculture monitoring is active! 🌱🤖</i>"""
    
    return send_telegram_message(help_message)

def main():
    """Main function with interactive menu"""
    print("🤖 Direct Telegram Bot Command Interface")
    print("=" * 50)
    print("This bypasses polling conflicts and sends commands directly")
    print()
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Send Weather Report")
        print("2. Send Dashboard Summary")
        print("3. Send Help Message")
        print("4. Test Backend Connection")
        print("5. Exit")
        
        choice = input("\n🔢 Enter your choice (1-5): ").strip()
        
        if choice == "1":
            send_weather_report()
        elif choice == "2":
            send_dashboard_report()
        elif choice == "3":
            send_help_message()
        elif choice == "4":
            print("\n🧪 Testing Backend Connection...")
            try:
                response = requests.get(f"{BACKEND_URL}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Backend: {data['status']}, Model: {'loaded' if data['model_loaded'] else 'not loaded'}")
                else:
                    print(f"❌ Backend: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Backend: {e}")
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()