#!/usr/bin/env python3
"""
Test Telegram bot functionality in unified server
"""
import requests
import json
import os

def test_telegram_bot():
    """Test if Telegram bot is responding"""
    
    # Test bot info
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    try:
        # Get bot info
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                print(f"✅ Telegram bot active: @{data['result']['username']}")
                return True
            else:
                print(f"❌ Telegram bot error: {data}")
                return False
        else:
            print(f"❌ Telegram API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

def test_pump_control():
    """Test pump control via unified API"""
    try:
        url = "http://localhost:8000/api/pump-control"
        data = {"action": "ON"}
        
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pump control API working: {result}")
            return True
        else:
            print(f"❌ Pump control failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Pump control test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing Unified System Components...")
    print()
    
    print("1. Testing Telegram Bot Connection:")
    telegram_ok = test_telegram_bot()
    print()
    
    print("2. Testing Pump Control API:")
    pump_ok = test_pump_control()
    print()
    
    if telegram_ok and pump_ok:
        print("✅ All unified system components working!")
    else:
        print("⚠️ Some components need attention")