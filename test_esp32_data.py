#!/usr/bin/env python3
"""
Test ESP32 data simulation to verify WebSocket connection
"""
import asyncio
import websockets
import json
import time

async def send_esp32_data():
    uri = "ws://localhost:8080/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Send ESP32-style data
            esp32_data = {
                "source": "esp32_wifi",
                "soil": 45,
                "temperature": 28.5,
                "humidity": 62,
                "rain": 0,
                "pump": 0,
                "light": 500,
                "flow": 0.0,
                "total": 0.0
            }
            
            for i in range(5):
                # Vary the data slightly
                esp32_data["soil"] = 45 + (i * 2)
                esp32_data["temperature"] = 28.5 + (i * 0.5)
                esp32_data["humidity"] = 62 + i
                
                await websocket.send(json.dumps(esp32_data))
                print(f"📤 Sent ESP32 data #{i+1}: {esp32_data}")
                
                await asyncio.sleep(2)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_esp32_data())