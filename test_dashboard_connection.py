#!/usr/bin/env python3
"""
Test dashboard WebSocket connection
"""
import asyncio
import websockets
import json

async def test_dashboard_connection():
    uri = "ws://localhost:8080/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Dashboard connected to WebSocket server")
            
            # Register as dashboard
            register_msg = {
                "type": "register",
                "role": "dashboard",
                "id": "test_dashboard"
            }
            await websocket.send(json.dumps(register_msg))
            print("📤 Sent dashboard registration")
            
            # Listen for messages
            print("👂 Listening for messages...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    print(f"📥 Received: {data}")
                    
                    if 'soil' in data:
                        print(f"🌱 Soil: {data['soil']}%")
                        print(f"🌡️ Temperature: {data['temperature']}°C")
                        print(f"💨 Humidity: {data['humidity']}%")
                        break
                        
            except asyncio.TimeoutError:
                print("⏰ No messages received in 10 seconds")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_dashboard_connection())