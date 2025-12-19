#!/usr/bin/env python3
import asyncio
import websockets
import json
from datetime import datetime

WS_URL = "ws://localhost:8080/ws"

async def connect_and_show_live_data():
    print("🔌 Connecting to WebSocket server...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket server at ws://localhost:8080/ws")
            print("📡 Listening for live Arduino data...\n")
            
            message_count = 0
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"📊 Message #{message_count} at {timestamp}")
                    print(f"🌡️  Temperature: {data.get('temperature', 'N/A')}°C")
                    print(f"💨 Humidity: {data.get('humidity', 'N/A')}%")
                    print(f"💧 Soil: {data.get('soil', 'N/A')}%")
                    print(f"🌞 Light: {data.get('light', 'N/A')} lux")
                    print(f"🌧️  Rain: {'🌧️ Raining' if data.get('rain') == 1 else '☀️ Clear'}")
                    print(f"🚿 Pump: {'🟢 ON' if data.get('pump') == 1 else '🔴 OFF'}")
                    print(f"💧 Flow: {data.get('flow', 'N/A')} L/min")
                    print(f"📊 Total: {data.get('total', 'N/A')} L")
                    print("-" * 50)
                    
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🚀 Arduino Live Data Monitor")
    print("=" * 50)
    asyncio.run(connect_and_show_live_data())