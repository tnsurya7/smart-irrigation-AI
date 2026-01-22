#!/usr/bin/env python3
"""
Comprehensive System Status Check for Unified Smart Agriculture System
"""
import requests
import json
import asyncio
import websockets
from datetime import datetime

def check_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/api/status", 
        "/api/system-status",
        "/api/sensor-status",
        "/weather",
        "/model-report",
        "/health",
        "/irrigation-recommendation?current_soil=45"
    ]
    
    print("🔍 Testing API Endpoints:")
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}")
                results[endpoint] = "OK"
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
                results[endpoint] = f"Error {response.status_code}"
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {str(e)[:50]}")
            results[endpoint] = "Failed"
    
    return results

async def check_websocket():
    """Test WebSocket connection"""
    print("\n🔌 Testing WebSocket:")
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("  ✅ WebSocket connection successful")
            
            # Send test data
            test_data = {"source": "status_check", "soil": 50, "temperature": 25}
            await websocket.send(json.dumps(test_data))
            print("  ✅ Data sent successfully")
            
            return True
    except Exception as e:
        print(f"  ❌ WebSocket failed: {e}")
        return False

def check_telegram_bot():
    """Test Telegram bot"""
    print("\n🤖 Testing Telegram Bot:")
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            return
        
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                print(f"  ✅ Bot active: @{data['result']['username']}")
                return True
        
        print(f"  ❌ Bot not responding")
        return False
    except Exception as e:
        print(f"  ❌ Telegram error: {e}")
        return False

def check_static_files():
    """Test static file serving"""
    print("\n📁 Testing Static Files:")
    base_url = "http://localhost:8000"
    files = [
        "/favicon.svg",
        "/leaf-cursor.svg", 
        "/assets/index-COOGF4dC.js",
        "/assets/index-CZOAs6Nz.css",
        "/soil_moisture_training.csv"
    ]
    
    results = {}
    for file_path in files:
        try:
            response = requests.head(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {file_path}")
                results[file_path] = "OK"
            else:
                print(f"  ❌ {file_path} - Status: {response.status_code}")
                results[file_path] = f"Error {response.status_code}"
        except Exception as e:
            print(f"  ❌ {file_path} - Error: {str(e)[:30]}")
            results[file_path] = "Failed"
    
    return results

async def main():
    """Run all system checks"""
    print("🌱 Smart Agriculture - Unified System Status Check")
    print("=" * 60)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check API endpoints
    api_results = check_api_endpoints()
    
    # Check WebSocket
    ws_ok = await check_websocket()
    
    # Check Telegram bot
    telegram_ok = check_telegram_bot()
    
    # Check static files
    static_results = check_static_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYSTEM STATUS SUMMARY")
    print("=" * 60)
    
    api_ok = all(result == "OK" for result in api_results.values())
    static_ok = all(result == "OK" for result in static_results.values())
    
    print(f"🔗 API Endpoints: {'✅ ALL OK' if api_ok else '❌ ISSUES FOUND'}")
    print(f"🔌 WebSocket: {'✅ OK' if ws_ok else '❌ FAILED'}")
    print(f"🤖 Telegram Bot: {'✅ OK' if telegram_ok else '❌ FAILED'}")
    print(f"📁 Static Files: {'✅ ALL OK' if static_ok else '❌ ISSUES FOUND'}")
    
    overall_status = api_ok and ws_ok and telegram_ok and static_ok
    
    print()
    if overall_status:
        print("🎉 UNIFIED SYSTEM FULLY OPERATIONAL!")
        print("🌐 Frontend: http://localhost:8000")
        print("📡 API: http://localhost:8000/api/*")
        print("🔌 WebSocket: ws://localhost:8000/ws")
        print("🤖 Telegram: @Arimax_Alert_Bot")
    else:
        print("⚠️ SYSTEM HAS ISSUES - Check failed components above")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())