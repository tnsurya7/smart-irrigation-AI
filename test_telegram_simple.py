#!/usr/bin/env python3
"""
Test the simple telegram bot functionality
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

def send_command(command):
    """Send a command to the bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": command
    }
    
    response = requests.post(url, json=payload)
    if response.ok:
        print(f"✅ Command sent: {command}")
        return True
    else:
        print(f"❌ Failed to send command: {response.text}")
        return False

def test_commands():
    """Test various bot commands"""
    commands = [
        "help",
        "weather",
        "dashboard",
        "pump on",
        "pump off"
    ]
    
    print("🧪 Testing Telegram Bot Commands")
    print("=" * 40)
    
    for cmd in commands:
        print(f"\n📤 Testing: {cmd}")
        if send_command(cmd):
            print("⏳ Waiting 3 seconds for response...")
            time.sleep(3)
        else:
            print("❌ Command failed")
    
    print("\n✅ All commands sent. Check Telegram for responses.")

if __name__ == "__main__":
    test_commands()