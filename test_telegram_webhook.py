#!/usr/bin/env python3
"""
Test Telegram Bot Webhook Integration
Tests webhook setup and bot functionality
"""

import os
import requests
import json
from datetime import datetime

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BACKEND_URL = os.getenv("BACKEND_URL", "https://smart-agriculture-backend-my7c.onrender.com")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing environment variables: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
    exit(1)

# Telegram API
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def test_backend_health():
    """Test if backend is healthy"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"✅ Backend health: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend health failed: {e}")
        return False

def test_telegram_webhook_info():
    """Check current webhook status"""
    print("\n🔍 Checking webhook status...")
    try:
        response = requests.get(f"{TG_API}/getWebhookInfo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook info: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Failed to get webhook info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Webhook info error: {e}")
        return None

def set_telegram_webhook():
    """Set webhook URL"""
    webhook_url = f"{BACKEND_URL}/telegram/webhook"
    print(f"\n🔧 Setting webhook to: {webhook_url}")
    
    try:
        response = requests.post(
            f"{TG_API}/setWebhook",
            json={"url": webhook_url},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook set successfully: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Failed to set webhook: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook setup error: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint directly"""
    webhook_url = f"{BACKEND_URL}/telegram/webhook"
    print(f"\n🔍 Testing webhook endpoint: {webhook_url}")
    
    # Simulate Telegram webhook payload
    test_payload = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": int(CHAT_ID),
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": int(CHAT_ID),
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": "/start"
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Webhook test: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def send_test_message():
    """Send test message to verify bot is working"""
    print(f"\n📱 Sending test message to chat {CHAT_ID}...")
    
    message = f"""🤖 **Telegram Bot Test** 🤖

⏰ **Time:** {datetime.now().strftime("%H:%M:%S")}
🔗 **Backend:** {BACKEND_URL}
✅ **Status:** Webhook integration test

**Test Commands:**
• Type `sensor data` for live readings
• Type `weather report` for current weather
• Type `pump on` to test pump control

**Bot is ready for production use!** 🚀"""
    
    try:
        response = requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Test message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send test message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test message error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TELEGRAM BOT WEBHOOK TEST")
    print("=" * 50)
    
    # Test 1: Backend health
    backend_ok = test_backend_health()
    
    # Test 2: Current webhook status
    webhook_info = test_telegram_webhook_info()
    
    # Test 3: Set webhook if needed
    if not webhook_info or not webhook_info.get("result", {}).get("url"):
        print("\n⚠️ Webhook not set, setting now...")
        set_telegram_webhook()
    else:
        current_url = webhook_info.get("result", {}).get("url", "")
        expected_url = f"{BACKEND_URL}/telegram/webhook"
        if current_url != expected_url:
            print(f"\n⚠️ Webhook URL mismatch. Current: {current_url}, Expected: {expected_url}")
            set_telegram_webhook()
        else:
            print(f"\n✅ Webhook already set correctly: {current_url}")
    
    # Test 4: Test webhook endpoint
    webhook_ok = test_webhook_endpoint()
    
    # Test 5: Send test message
    message_ok = send_test_message()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Webhook Setup: {'✅ PASS' if webhook_ok else '❌ FAIL'}")
    print(f"Test Message: {'✅ PASS' if message_ok else '❌ FAIL'}")
    
    if backend_ok and webhook_ok and message_ok:
        print("\n🎉 ALL TESTS PASSED! Bot is ready for production use.")
        print(f"📱 Open Telegram and chat with @Arimax_Alert_Bot")
        print(f"💬 Your Chat ID: {CHAT_ID}")
        print(f"🔗 Backend: {BACKEND_URL}")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return backend_ok and webhook_ok and message_ok

if __name__ == "__main__":
    main()