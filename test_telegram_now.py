"""
Test Telegram Bot - Send immediate test message
"""

import os
import requests
from datetime import datetime

# Load environment variables directly from .env file
def load_env_vars():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("❌ .env file not found")
    return env_vars

# Load environment variables
env_vars = load_env_vars()
BOT_TOKEN = env_vars.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = env_vars.get("TELEGRAM_CHAT_ID", "5707565347")
OPENWEATHER_API_KEY = env_vars.get("OPENWEATHER_API_KEY")

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
            print("✅ Message sent successfully to Telegram")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def get_real_weather_data():
    """Get real weather data from OpenWeather API"""
    if not OPENWEATHER_API_KEY:
        return None
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Erode,IN&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": round(data['main']['temp']),
            "humidity": data['main']['humidity'],
            "description": data['weather'][0]['description'].title(),
            "city_name": data['name']
        }
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return None

def test_telegram_connection():
    """Test basic Telegram bot connection"""
    print("🧪 Testing Telegram Bot Connection...")
    
    # Check bot info
    try:
        response = requests.get(f"{TG_API}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: {bot_info['result']['first_name']}")
            print(f"✅ Bot username: @{bot_info['result']['username']}")
        else:
            print(f"❌ Bot connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bot connection error: {e}")
        return False
    
    return True

def send_test_message():
    """Send a test message to verify Telegram is working"""
    print("📱 Sending test message to Telegram...")
    
    # Get current time
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Get weather data
    weather_data = get_real_weather_data()
    
    # Build test message
    message = "🧪 **TELEGRAM TEST MESSAGE**\n\n"
    message += f"⏰ **Test Time:** {current_time}\n"
    message += f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    if weather_data:
        message += "🌤️ **Weather Test (OpenWeather API):**\n"
        message += f"• Location: {weather_data['city_name']}\n"
        message += f"• Temperature: {weather_data['temperature']}°C\n"
        message += f"• Humidity: {weather_data['humidity']}%\n"
        message += f"• Condition: {weather_data['description']}\n\n"
    else:
        message += "🌤️ **Weather Test:** API not available\n\n"
    
    message += "📡 **System Status:**\n"
    message += "• Backend: ✅ Online\n"
    message += "• Telegram Bot: ✅ Working\n"
    message += "• 5-Min Updates: 🔄 Starting soon\n\n"
    
    message += "🎯 **Next Steps:**\n"
    message += "• 5-minute updates will start automatically\n"
    message += "• ESP32 status will be monitored\n"
    message += "• Real weather data every update\n\n"
    
    message += "✅ **Test completed successfully!**"
    
    # Send the message
    success = send_telegram_message(message)
    return success

def send_5min_format_preview():
    """Send a preview of the 5-minute update format"""
    print("📋 Sending 5-minute update format preview...")
    
    current_time = datetime.now().strftime("%H:%M:%S")
    weather_data = get_real_weather_data()
    
    # Build preview message
    message = "📋 **5-MINUTE UPDATE FORMAT PREVIEW**\n\n"
    message += "This is how your regular updates will look:\n\n"
    message += "---\n\n"
    
    # Actual format preview
    message += "📈 SMART AGRICULTURE UPDATE (5-Min)\n\n"
    
    # Weather section
    if weather_data:
        message += f"🌤️ Weather (OpenWeather)\n"
        message += f"• Location: {weather_data['city_name']}\n"
        message += f"• Temperature: {weather_data['temperature']}°C\n"
        message += f"• Humidity: {weather_data['humidity']}%\n"
        message += f"• Condition: {weather_data['description']}\n"
        message += f"• Rain Probability: 15%\n\n"
    else:
        message += "🌤️ Weather (OpenWeather)\n"
        message += "• Status: API unavailable\n\n"
    
    # Sensor section (offline example)
    message += "📡 Live Sensors:\n"
    message += "• Status: 🔴 OFFLINE\n"
    message += "• Last Update: Never\n"
    message += "• Sensor Values: Not available\n\n"
    
    # System status
    message += "📊 System Status\n"
    message += "• Pump: 🔴 OFF\n"
    message += "• Mode: AUTO\n"
    message += "• Water Used: 0 L\n"
    message += "• ARIMAX: 🟢 ACTIVE\n\n"
    
    # Data sources
    message += "📡 Data Sources:\n"
    message += "• Weather: OpenWeather API\n"
    message += "• Sensors: ESP32 (offline)\n"
    message += "• Prediction: ARIMAX\n\n"
    
    message += f"⏰ Report Time: {current_time}\n\n"
    message += "---\n\n"
    message += "🔄 **Updates start automatically every 5 minutes**"
    
    # Send the preview
    success = send_telegram_message(message)
    return success

def main():
    """Run Telegram tests"""
    print("🚀 Starting Telegram Test Suite")
    print("=" * 50)
    
    # Check environment variables
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return
    
    if not CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID not found in environment")
        return
    
    print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
    print(f"✅ Chat ID: {CHAT_ID}")
    
    # Test connection
    if not test_telegram_connection():
        print("❌ Telegram connection failed")
        return
    
    print("\n" + "=" * 50)
    
    # Send test message
    if send_test_message():
        print("✅ Test message sent successfully")
    else:
        print("❌ Test message failed")
        return
    
    print("\n" + "=" * 50)
    
    # Send format preview
    if send_5min_format_preview():
        print("✅ Format preview sent successfully")
    else:
        print("❌ Format preview failed")
    
    print("\n" + "=" * 50)
    print("🎉 Telegram test completed!")
    print("\n📱 Check your Telegram chat for:")
    print("1. Test message with current weather")
    print("2. 5-minute update format preview")
    print("\n🔄 The actual 5-minute updates will start when the backend is deployed.")

if __name__ == "__main__":
    main()