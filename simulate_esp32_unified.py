#!/usr/bin/env python3
"""
Simulate ESP32 connection to unified system
Tests the exact data format ESP32 will send
"""
import asyncio
import websockets
import json
import time
import random

async def simulate_esp32():
    """Simulate ESP32 sending sensor data to unified system"""
    uri = "ws://localhost:8000/ws"
    
    print("🔌 ESP32 Simulator - Connecting to unified system...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ ESP32 connected to unified WebSocket server")
            
            # Simulate continuous sensor data like real ESP32
            for i in range(10):
                # Generate realistic sensor data
                sensor_data = {
                    "source": "esp32_wifi",
                    "soil": random.randint(30, 80),
                    "temperature": round(random.uniform(25.0, 35.0), 1),
                    "humidity": random.randint(40, 80),
                    "rain": random.choice([0, 1]),  # 0 = no rain, 1 = rain
                    "pump": random.choice([0, 1]),  # 0 = OFF, 1 = ON
                    "light": random.randint(200, 800),
                    "flow": round(random.uniform(0.0, 5.0), 1),
                    "total": round(random.uniform(0.0, 100.0), 1)
                }
                
                await websocket.send(json.dumps(sensor_data))
                print(f"📤 ESP32 Sent: Soil={sensor_data['soil']}%, Temp={sensor_data['temperature']}°C, Pump={'ON' if sensor_data['pump'] else 'OFF'}")
                
                # Wait for any server response (like pump commands)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    response_data = json.loads(response)
                    if response_data.get("type") == "cmd" and response_data.get("cmd") == "pump":
                        print(f"📩 ESP32 Received pump command: {response_data.get('value')}")
                except asyncio.TimeoutError:
                    pass  # No command received, continue
                except json.JSONDecodeError:
                    pass  # Invalid JSON, ignore
                
                await asyncio.sleep(2)  # Send data every 2 seconds like real ESP32
            
            print("✅ ESP32 simulation completed")
            
    except Exception as e:
        print(f"❌ ESP32 simulation failed: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_esp32())