#!/usr/bin/env python3
"""
Test WebSocket client to simulate ESP32 sensor data
Sends realistic sensor data to test the dashboard
"""

import asyncio
import websockets
import json
import random
import time
from datetime import datetime

async def simulate_esp32():
    uri = "ws://localhost:8080"
    
    # Initial sensor values
    soil_pct = 45.0  # Start with moderate soil moisture
    temperature = 28.5
    humidity = 65.0
    rain_raw = 1000  # No rain initially
    ldr_raw = 400    # Normal light
    flow_lmin = 0.0
    total_l = 0.0
    pump = 0         # Pump OFF initially
    mode = "AUTO"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket server at {uri}")
            
            # Register as ESP32 device
            register_msg = {
                "type": "register",
                "role": "esp32",
                "id": "esp32_test"
            }
            await websocket.send(json.dumps(register_msg))
            print("📡 Registered as ESP32 device")
            
            # Send sensor data every 3 seconds
            while True:
                # Simulate realistic sensor changes
                soil_pct += random.uniform(-2.0, 1.5)  # Gradual soil moisture change
                soil_pct = max(0, min(100, soil_pct))  # Keep in valid range
                
                temperature += random.uniform(-0.5, 0.5)
                temperature = max(20, min(40, temperature))
                
                humidity += random.uniform(-2.0, 2.0)
                humidity = max(30, min(90, humidity))
                
                # Simulate occasional rain
                if random.random() < 0.05:  # 5% chance of rain
                    rain_raw = random.randint(200, 499)  # Rain detected
                else:
                    rain_raw = random.randint(800, 1023)  # No rain
                
                # Simulate light changes
                ldr_raw += random.randint(-50, 50)
                ldr_raw = max(0, min(1023, ldr_raw))
                
                # Simulate pump flow when ON
                if pump == 1:
                    flow_lmin = random.uniform(2.0, 3.5)
                    total_l += flow_lmin / 20  # Accumulate total liters
                else:
                    flow_lmin = 0.0
                
                # Create sensor message in ESP32 format
                sensor_msg = {
                    "type": "sensors",
                    "soil_pct": round(soil_pct, 1),
                    "rain_raw": rain_raw,
                    "ldr_raw": ldr_raw,
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "flow_lmin": round(flow_lmin, 2),
                    "total_l": round(total_l, 2),
                    "pump": pump,
                    "mode": mode
                }
                
                await websocket.send(json.dumps(sensor_msg))
                print(f"📊 Sent: Soil={soil_pct:.1f}%, Temp={temperature:.1f}°C, Pump={'ON' if pump else 'OFF'}, Rain={rain_raw}")
                
                # Listen for pump commands from dashboard
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    cmd_data = json.loads(response)
                    if cmd_data.get("type") == "cmd" and cmd_data.get("cmd") == "pump":
                        new_pump_state = 1 if cmd_data.get("value") == "ON" else 0
                        if new_pump_state != pump:
                            pump = new_pump_state
                            print(f"🔧 Pump command received: {'ON' if pump else 'OFF'}")
                except asyncio.TimeoutError:
                    pass  # No command received, continue
                except json.JSONDecodeError:
                    pass  # Invalid JSON, ignore
                
                await asyncio.sleep(3)  # Send data every 3 seconds
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket connection closed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting ESP32 WebSocket simulator...")
    print("📡 Will connect to ws://localhost:8080")
    print("📊 Sending realistic sensor data every 3 seconds")
    print("🔧 Listening for pump commands from dashboard")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        asyncio.run(simulate_esp32())
    except KeyboardInterrupt:
        print("\n⏹️  Simulator stopped by user")