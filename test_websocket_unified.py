#!/usr/bin/env python3
"""
Test WebSocket connection to unified server
"""
import asyncio
import websockets
import json
import time

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to unified WebSocket server")
            
            # Send test sensor data
            test_data = {
                "source": "test_client",
                "soil": 45,
                "temperature": 28.5,
                "humidity": 62,
                "rain": 0,
                "pump": 0,
                "light": 500,
                "flow": 0.0,
                "total": 0.0
            }
            
            await websocket.send(json.dumps(test_data))
            print(f"📤 Sent test data: {test_data}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received (timeout)")
            
            print("✅ WebSocket test completed")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())