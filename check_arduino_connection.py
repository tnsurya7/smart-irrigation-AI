#!/usr/bin/env python3
import asyncio
import websockets
import json
from datetime import datetime

WS_URL = "ws://localhost:8080/ws"

async def monitor_real_arduino():
    print("🔍 Monitoring for REAL Arduino connections...")
    print("📡 WebSocket URL:", WS_URL)
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket server")
            print("⏳ Waiting for REAL Arduino data...")
            print("💡 Make sure your ESP8266 is:")
            print("   - Connected to 'Karan' WiFi")
            print("   - Programmed with WebSocket client code")
            print("   - Sending data to ws://192.168.233.157:8080/ws")
            print("-" * 60)
            
            message_count = 0
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Check if this is real Arduino data
                    if all(key in data for key in ['soil', 'temperature', 'humidity', 'rain', 'pump', 'light']):
                        print(f"🎉 REAL ARDUINO DATA #{message_count} at {timestamp}")
                        print(f"🌡️  Temperature: {data['temperature']}°C")
                        print(f"💨 Humidity: {data['humidity']}%")
                        print(f"💧 Soil: {data['soil']}%")
                        print(f"🌞 Light: {data['light']} lux")
                        print(f"🌧️  Rain: {'🌧️ Raining' if data['rain'] == 1 else '☀️ Clear'}")
                        print(f"🚿 Pump: {'🟢 ON' if data['pump'] == 1 else '🔴 OFF'}")
                        print(f"💧 Flow: {data.get('flow', 0)} L/min")
                        print(f"📊 Total: {data.get('total', 0)} L")
                        print("✅ This data will appear on dashboard!")
                        print("=" * 60)
                    else:
                        print(f"⚠️  Non-Arduino data received: {data}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure WebSocket server is running on port 8080")

if __name__ == "__main__":
    asyncio.run(monitor_real_arduino())