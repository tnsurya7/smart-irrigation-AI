#!/usr/bin/env python3
"""
Test Enhanced Telegram Bot Features
Tests all the new functionality including:
- Dashboard summary
- Pump control
- Rain alerts
- Weather reports with OpenWeather API
- Comprehensive command processing
"""
import requests
import json
import time
import asyncio
import websockets

def send_telegram_command(message):
    """Send a command to the Telegram bot"""
    bot_token = "8063174729:AAGJYD_IMImdzkTRYbCiokomWsZlHcIW8jg"
    chat_id = "5707565347"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Sent: '{message}'")
            return True
        else:
            print(f"❌ Failed to send '{message}': {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending '{message}': {e}")
        return False

async def send_test_sensor_data():
    """Send test sensor data to populate the system"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("📡 Sending test sensor data...")
            
            # Send realistic sensor data
            test_data = {
                "source": "esp32_wifi",
                "soil": 45,
                "temperature": 28.5,
                "humidity": 65,
                "rain": 0,
                "pump": 1,
                "light": 500,
                "flow": 2.5,
                "total": 25.0
            }
            
            await websocket.send(json.dumps(test_data))
            print(f"📤 Sent sensor data: Soil={test_data['soil']}%, Temp={test_data['temperature']}°C")
            
            # Wait a moment for data to be processed
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"❌ Failed to send sensor data: {e}")

def test_api_endpoints():
    """Test API endpoints that Telegram bot uses"""
    print("🔍 Testing API endpoints...")
    
    endpoints = [
        "/weather",
        "/api/system-status",
        "/api/sensor-status",
        "/api/daily-summary"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {str(e)[:30]}")

async def main():
    """Run comprehensive Telegram bot tests"""
    print("🤖 Enhanced Telegram Bot Feature Test")
    print("=" * 60)
    print(f"📅 Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API endpoints first
    test_api_endpoints()
    print()
    
    # Send test sensor data
    await send_test_sensor_data()
    print()
    
    # Test all Telegram commands
    print("📱 Testing Enhanced Telegram Commands...")
    print("Note: Check your Telegram chat @Arimax_Alert_Bot for responses")
    print()
    
    # Test commands with delays between each
    test_commands = [
        ("help", "📖 Help command - should show comprehensive command guide"),
        ("sensor data", "📊 Should show detailed sensor readings"),
        ("weather report", "🌤️ Should show weather with rain probability"),
        ("dashboard summary", "📊 Should show comprehensive dashboard data"),
        ("pump on", "🟢 Should turn pump ON with detailed response"),
        ("pump off", "🔴 Should turn pump OFF with detailed response"),
        ("rain alert", "🌧️ Should check rain probability and alerts"),
        ("today report", "📈 Should show today's activity summary"),
        ("unknown command test", "❓ Should show unknown command help")
    ]
    
    for i, (command, description) in enumerate(test_commands, 1):
        print(f"{i:2d}. Testing: '{command}'")
        print(f"    Expected: {description}")
        
        success = send_telegram_command(command)
        if success:
            print(f"    ✅ Command sent successfully")
        else:
            print(f"    ❌ Failed to send command")
        
        print()
        time.sleep(3)  # Wait between commands to avoid rate limiting
    
    print("=" * 60)
    print("🎯 Test Summary:")
    print("✅ All enhanced features have been tested")
    print("📱 Check your Telegram chat for bot responses")
    print("🔍 Verify the following features work:")
    print("   • Detailed sensor data display")
    print("   • Weather reports with rain alerts")
    print("   • Comprehensive dashboard summaries")
    print("   • Enhanced pump control messages")
    print("   • Natural language command processing")
    print("   • Unknown command handling")
    print()
    print("⏰ Scheduled Features (check logs):")
    print("   • 7:00 AM - Morning weather reports")
    print("   • 8:00 PM - Evening dashboard summaries")
    print("   • Hourly - Rain alert monitoring")
    print()
    print("🌐 Dashboard: http://localhost:8000")
    print("🤖 Bot: @Arimax_Alert_Bot")

if __name__ == "__main__":
    asyncio.run(main())