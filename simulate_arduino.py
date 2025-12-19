import asyncio
import websockets
import json
import random
import time

WS_URL = "ws://localhost:8080/ws"

async def simulate_arduino():
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=None) as ws:
                print("✅ Arduino Simulator Connected to WebSocket")
                while True:
                    # Generate realistic Arduino data
                    arduino_data = {
                        "soil": random.randint(20, 80),
                        "temp": round(random.uniform(20, 35), 1),
                        "hum": round(random.uniform(40, 90), 1),
                        "rain": random.randint(0, 1),
                        "pump": random.randint(0, 1),
                        "light": random.randint(100, 2000),
                        "flow": round(random.uniform(0, 5), 1),
                        "total": round(random.uniform(0, 100), 1)
                    }
                    
                    await ws.send(json.dumps(arduino_data))
                    print(f"📤 Arduino Data: Soil={arduino_data['soil']}%, Temp={arduino_data['temp']}°C, Pump={'ON' if arduino_data['pump'] else 'OFF'}")
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(5)

asyncio.run(simulate_arduino())