#!/usr/bin/env python3
"""
Test the telegram bot functions directly without network calls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot_simple import TelegramBot

def test_bot_commands():
    """Test bot command processing"""
    print("🧪 Testing Telegram Bot Functions")
    print("=" * 50)
    
    bot = TelegramBot()
    
    # Test commands
    test_cases = [
        ("help", "Should show help menu"),
        ("weather", "Should show weather report for Erode"),
        ("dashboard", "Should show sensor data and dashboard summary"),
        ("pump on", "Should send pump ON command"),
        ("pump off", "Should send pump OFF command"),
        ("unknown command", "Should show unknown command message")
    ]
    
    for command, description in test_cases:
        print(f"\n📤 Testing: '{command}'")
        print(f"📝 Expected: {description}")
        
        try:
            response = bot.process_command(command)
            print(f"✅ Response received ({len(response)} chars)")
            print(f"📄 Preview: {response[:100]}...")
            
            # Check if response contains expected elements
            if command == "help":
                assert "Commands" in response, "Help should contain 'Commands'"
            elif command == "weather":
                assert "Weather Report" in response, "Weather should contain 'Weather Report'"
            elif command == "dashboard":
                assert "Dashboard Report" in response, "Dashboard should contain 'Dashboard Report'"
            elif "pump" in command:
                assert "Pump" in response, "Pump commands should contain 'Pump'"
            
            print("✅ Response validation passed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎉 Bot function tests completed!")

if __name__ == "__main__":
    test_bot_commands()