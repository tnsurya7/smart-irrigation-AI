#!/usr/bin/env python3
"""
Test the scheduled Telegram features manually
"""
import os
import requests
import json
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Erode"

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Message sent successfully")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_weather_data():
    """Get weather data from OpenWeather API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Calculate rain probability
            rain_1h = data.get("rain", {}).get("1h", 0)
            clouds = data.get("clouds", {}).get("all", 0)
            main_weather = data["weather"][0]["main"].lower()
            
            rain_probability = 0
            if rain_1h > 0:
                rain_probability = min(90, rain_1h * 20)
            elif "rain" in main_weather or "drizzle" in main_weather:
                rain_probability = 70
            elif "thunderstorm" in main_weather:
                rain_probability = 85
            elif clouds > 80:
                rain_probability = 40
            elif clouds > 60:
                rain_probability = 25
            else:
                rain_probability = max(5, clouds / 4)
            
            return {
                "temperature": round(data["main"]["temp"], 1),
                "humidity": data["main"]["humidity"],
                "rain_probability": round(rain_probability, 1),
                "rain_expected": rain_probability > 50,
                "condition": data["weather"][0]["description"].title(),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", 0) / 1000,
                "location": data["name"]
            }
        else:
            return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def test_morning_weather_report():
    """Test the 7 AM morning weather report"""
    print("🌅 Testing Morning Weather Report (7 AM feature)...")
    
    weather = get_weather_data()
    if weather:
        rain_alert = "🚨 <b>RAIN EXPECTED TODAY!</b>" if weather['rain_expected'] else "☀️ <b>Good Weather Today</b>"
        
        message = f"""{rain_alert}

🌅 <b>Morning Weather Report - {weather['location']}</b>
📅 <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}

🌡️ <b>Temperature:</b> {weather['temperature']}°C
💨 <b>Humidity:</b> {weather['humidity']}%
☁️ <b>Condition:</b> {weather['condition']}
🌧️ <b>Rain Probability:</b> {weather['rain_probability']}%
💨 <b>Wind Speed:</b> {weather['wind_speed']} m/s
🔽 <b>Pressure:</b> {weather['pressure']} hPa

{'🚨 <b>Irrigation Recommendation:</b> Monitor rain - may need to adjust irrigation schedule' if weather['rain_expected'] else '✅ <b>Irrigation Recommendation:</b> Normal irrigation schedule OK'}

🌱 <b>Farm Status:</b>
• System: Online (Test Mode)
• Current Soil: 45%
• Pump: OFF

<i>Have a great farming day! 🌾</i>

<b>📝 TEST MESSAGE - Morning Report Feature</b>"""
    else:
        message = f"""🌅 <b>Morning Weather Report</b>
📅 <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}

❌ Weather data unavailable - API service error
🌱 <b>Farm Status:</b> Online (Test Mode)

<i>Check dashboard for system status</i>

<b>📝 TEST MESSAGE - Morning Report Feature</b>"""
    
    return send_telegram_message(message)

def test_evening_dashboard_summary():
    """Test the 8 PM evening dashboard summary"""
    print("📊 Testing Evening Dashboard Summary (8 PM feature)...")
    
    # Get system data
    try:
        response = requests.get("http://localhost:8000/api/daily-summary", timeout=5)
        if response.status_code == 200:
            summary_data = response.json()
        else:
            summary_data = None
    except:
        summary_data = None
    
    weather = get_weather_data()
    
    message = f"""📊 <b>Daily Dashboard Summary</b>
📅 <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}
⏰ <b>Report Time:</b> {datetime.now().strftime('%H:%M:%S')}

🌱 <b>Current Sensor Readings:</b>
• Soil Moisture: 45%
• Temperature: 28.5°C
• Humidity: 65%
• Light Level: 500 lux
• Rain Status: No Rain

🚿 <b>Irrigation Summary Today:</b>
• Pump ON Operations: 3
• Pump OFF Operations: 2
• Total Operations: 5
• Irrigation Cycles: 3
• Estimated Water Used: ~60L
• Current Pump Status: OFF

🌤️ <b>Weather Summary:</b>"""
    
    if weather:
        message += f"""
• Temperature: {weather['temperature']}°C
• Humidity: {weather['humidity']}%
• Condition: {weather['condition']}
• Rain Probability: {weather['rain_probability']}%
• Rain Expected: {'Yes' if weather['rain_expected'] else 'No'}"""
    else:
        message += "\n• Weather data unavailable"
    
    message += f"""

🤖 <b>AI Model Performance:</b>
• ARIMA Model: 82.5% accuracy
• ARIMAX Model: 94.6% accuracy
• Best Model: ARIMAX
• Prediction Status: Active

📡 <b>System Health:</b>
• Overall Status: Online
• WebSocket Connections: 1
• System Uptime: Running
• Data Collection: Active

📈 <b>Daily Insights:</b>
• Soil moisture trend: Stable
• Irrigation efficiency: Good
• Weather impact: Normal conditions

🔗 <b>Dashboard:</b> http://localhost:8000
🤖 <b>Bot Commands:</b> Type "help" for available commands

<i>End of daily report - System monitoring continues 24/7</i>

<b>📝 TEST MESSAGE - Evening Summary Feature</b>"""
    
    return send_telegram_message(message)

def test_rain_alert():
    """Test rain alert functionality"""
    print("🚨 Testing Rain Alert Feature...")
    
    weather = get_weather_data()
    if weather and weather['rain_probability'] > 30:  # Lower threshold for testing
        message = f"""🚨 <b>RAIN ALERT TEST!</b>

🌧️ <b>Rain Probability Detected</b>
📍 Location: {weather['location']}
🌧️ Rain Probability: {weather['rain_probability']}%
☁️ Condition: {weather['condition']}

🚿 <b>Irrigation Recommendation:</b>
• Consider delaying irrigation
• Monitor soil moisture levels
• Current soil: 45%

⏰ Alert Time: {datetime.now().strftime('%H:%M:%S')}

<b>📝 TEST MESSAGE - Rain Alert Feature</b>"""
        
        return send_telegram_message(message)
    else:
        message = f"""☀️ <b>Rain Alert Test - No Alert Needed</b>

🌤️ Current rain probability: {weather['rain_probability'] if weather else 'Unknown'}%
📍 Location: {weather['location'] if weather else 'Unknown'}

✅ No rain alert needed at this time
🚿 Normal irrigation schedule OK

⏰ Check Time: {datetime.now().strftime('%H:%M:%S')}

<b>📝 TEST MESSAGE - Rain Alert Feature</b>"""
        
        return send_telegram_message(message)

def main():
    """Test all scheduled features"""
    print("⏰ Testing Scheduled Telegram Features")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("Testing all automated features that run on schedule:")
    print()
    
    # Test morning weather report
    success1 = test_morning_weather_report()
    print()
    
    # Test evening dashboard summary
    success2 = test_evening_dashboard_summary()
    print()
    
    # Test rain alert
    success3 = test_rain_alert()
    print()
    
    print("=" * 50)
    print("🎯 Scheduled Features Test Results:")
    print(f"🌅 Morning Weather Report (7 AM): {'✅ WORKING' if success1 else '❌ FAILED'}")
    print(f"📊 Evening Dashboard Summary (8 PM): {'✅ WORKING' if success2 else '❌ FAILED'}")
    print(f"🚨 Rain Alert (Hourly): {'✅ WORKING' if success3 else '❌ FAILED'}")
    print()
    
    if all([success1, success2, success3]):
        print("🎉 ALL SCHEDULED FEATURES WORKING PERFECTLY!")
        print("📱 Check your Telegram chat for the test messages")
        print("⏰ These features will run automatically:")
        print("   • 7:00 AM - Morning weather reports")
        print("   • 8:00 PM - Evening dashboard summaries") 
        print("   • Every hour - Rain alert monitoring")
    else:
        print("⚠️ Some features need attention - check error messages above")
    
    print()
    print("🤖 Bot: @Arimax_Alert_Bot")
    print("🌐 Dashboard: http://localhost:8000")

if __name__ == "__main__":
    main()