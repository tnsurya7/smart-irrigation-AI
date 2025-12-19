#!/usr/bin/env python3
import asyncio
import websockets
import json
import random
import time

WS_URL = "ws://localhost:8080/ws"

async def send_test_data():
    print("🔌 Connecting to WebSocket server to send test data...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected! Sending test Arduino data...")
            
            for i in range(10):
                # Generate test Arduino data
                test_data = {
                    "soil": random.randint(20, 80),
                    "temperature": round(random.uniform(25, 35), 1),
                    "humidity": round(random.uniform(50, 80), 1),
                    "rain": random.randint(0, 1),
                    "pump": random.randint(0, 1),
                    "light": random.randint(150, 300),
                    "flow": round(random.uniform(0, 3), 1),
                    "total": round(random.uniform(0, 50), 1)
                }
                
                await websocket.send(json.dumps(test_data))
                print(f"📤 Sent test data #{i+1}: {test_data}")
                await asyncio.sleep(2)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_data())