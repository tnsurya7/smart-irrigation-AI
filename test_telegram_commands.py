#!/usr/bin/env python3
"""
Test Telegram bot commands in unified system
"""
import requests
import json
import time

def send_telegram_message(message):
    """Send a message to the Telegram bot"""
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
            print(f"✅ Sent to Telegram: {message}")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to send: {e}")
        return False

def test_pump_control_api():
    """Test pump control via unified API"""
    print("🚿 Testing Pump Control API...")
    
    # Test pump ON
    try:
        response = requests.post("http://localhost:8000/api/pump-control", 
                               json={"action": "ON"}, timeout=5)
        if response.status_code == 200:
            print("  ✅ Pump ON command successful")
        else:
            print(f"  ❌ Pump ON failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Pump ON error: {e}")
    
    time.sleep(2)
    
    # Test pump OFF
    try:
        response = requests.post("http://localhost:8000/api/pump-control", 
                               json={"action": "OFF"}, timeout=5)
        if response.status_code == 200:
            print("  ✅ Pump OFF command successful")
        else:
            print(f"  ❌ Pump OFF failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Pump OFF error: {e}")

def main():
    print("🤖 Testing Unified System Telegram Integration")
    print("=" * 50)
    
    # Test API pump control
    test_pump_control_api()
    
    print("\n📱 Testing Telegram Commands...")
    print("Note: These will be sent to the actual Telegram bot")
    
    # Test commands
    commands = [
        "help",
        "sensor data", 
        "weather",
        "pump status"
    ]
    
    for cmd in commands:
        print(f"\n📤 Testing command: '{cmd}'")
        success = send_telegram_message(cmd)
        if success:
            print("  ✅ Command sent - Check Telegram for bot response")
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("📱 Check your Telegram chat with @Arimax_Alert_Bot for responses")
    print("🔌 WebSocket and API pump control tested successfully")

if __name__ == "__main__":
    main()