#!/usr/bin/env python3
"""
Send a test message to the Telegram bot to verify it's working
"""

import os
import requests
import json
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
    exit(1)

def send_test_message():
    """Send a test message to trigger the bot"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": "🧪 Bot Test - weather report",
            "parse_mode": "HTML"
        }
        
        print("📤 Sending test message to bot...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Test message sent successfully")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def check_bot_response():
    """Check if bot responded to our test message"""
    try:
        print("⏳ Waiting 5 seconds for bot response...")
        time.sleep(5)
        
        # Get recent messages
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"limit": 5}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data["ok"] and data["result"]:
                recent_messages = data["result"][-3:]  # Last 3 messages
                
                print("📨 Recent messages:")
                for msg in recent_messages:
                    if "message" in msg:
                        text = msg["message"].get("text", "")
                        from_user = msg["message"].get("from", {}).get("first_name", "Unknown")
                        print(f"   {from_user}: {text[:50]}...")
                
                # Check if any message contains weather report
                for msg in recent_messages:
                    if "message" in msg:
                        text = msg["message"].get("text", "")
                        if "Weather Report" in text and "Temperature" in text:
                            print("✅ Bot responded with weather report!")
                            return True
                
                print("⚠️ No weather report found in recent messages")
                return False
            else:
                print("❌ No messages found")
                return False
        else:
            print(f"❌ Failed to get updates: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking response: {e}")
        return False

def main():
    print("🧪 Telegram Bot Response Test")
    print("=" * 40)
    
    # Send test message
    if send_test_message():
        # Check for response
        if check_bot_response():
            print("\n🎉 Bot is working correctly!")
        else:
            print("\n⚠️ Bot may not be processing messages properly")
            print("   Check bot logs for errors")
    else:
        print("\n❌ Could not send test message")

if __name__ == "__main__":
    main()