#!/usr/bin/env python3
"""
Test script to simulate sending a command to the Telegram bot
"""

import requests
import json

# Test the weather endpoint directly
def test_weather_api():
    print("🧪 Testing Weather API directly...")
    try:
        response = requests.get("http://localhost:8000/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weather API: {data['temperature']:.1f}°C, {data['humidity']}%, {data['location']}")
            return True
        else:
            print(f"❌ Weather API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

# Test the bot's weather processing logic
def test_bot_weather_logic():
    print("\n🤖 Testing Bot Weather Logic...")
    try:
        # Import the bot class
        import sys
        sys.path.append('.')
        from telegram_bot_interactive import TelegramBotHandler
        
        bot = TelegramBotHandler()
        
        # Test the weather fetch method
        weather_response = bot.fetch_weather_report()
        print("✅ Bot weather response generated:")
        print(weather_response[:200] + "..." if len(weather_response) > 200 else weather_response)
        return True
        
    except Exception as e:
        print(f"❌ Bot logic error: {e}")
        return False

# Test command processing
def test_command_processing():
    print("\n💬 Testing Command Processing...")
    try:
        from telegram_bot_interactive import TelegramBotHandler
        
        bot = TelegramBotHandler()
        
        # Test different weather command variations
        commands = ["weather", "weather report", "weather today", "Weather Today?"]
        
        for cmd in commands:
            response = bot.process_command(cmd)
            if "Weather Report" in response:
                print(f"✅ Command '{cmd}' -> Weather response")
            else:
                print(f"❌ Command '{cmd}' -> {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Command processing error: {e}")
        return False

def main():
    print("🔍 Telegram Bot Command Testing")
    print("=" * 50)
    
    tests = [
        test_weather_api,
        test_bot_weather_logic,
        test_command_processing
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Bot should be working correctly.")
        print("\n💡 If users are still getting connection errors:")
        print("   1. Check if bot process is running")
        print("   2. Verify backend is accessible")
        print("   3. Look for 409 conflicts in bot logs")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()