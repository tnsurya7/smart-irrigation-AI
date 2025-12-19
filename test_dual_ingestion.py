#!/usr/bin/env python3
"""
Test client for Smart Agriculture Dual Data Ingestion System
Tests both WiFi and USB data sources with automatic fallback
"""

import asyncio
import websockets
import json
import time
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"
WIFI_WS_URL = "ws://localhost:8080/wifi"

class DualIngestionTester:
    def __init__(self):
        self.test_results = []
    
    async def test_wifi_connection(self):
        """Test WiFi WebSocket connection"""
        print("🔧 Testing WiFi WebSocket Connection...")
        
        try:
            async with websockets.connect(WIFI_WS_URL) as websocket:
                print("✅ WiFi WebSocket connected")
                
                # Send test sensor data
                test_data = {
                    "soil": 45,
                    "temperature": 28.5,
                    "humidity": 65.0,
                    "rain": 0,
                    "pump": 1,
                    "light": 350,
                    "flow": 2.1,
                    "total": 45.8
                }
                
                await websocket.send(json.dumps(test_data))
                print(f"📤 Sent WiFi test data: {test_data}")
                
                # Wait a moment
                await asyncio.sleep(1)
                
                return True
                
        except Exception as e:
            print(f"❌ WiFi WebSocket test failed: {e}")
            return False
    
    async def test_dashboard_connection(self):
        """Test dashboard WebSocket connection"""
        print("🔧 Testing Dashboard WebSocket Connection...")
        
        try:
            async with websockets.connect(WS_URL) as websocket:
                print("✅ Dashboard WebSocket connected")
                
                # Listen for data
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"📨 Received dashboard data: {data}")
                    return True
                except asyncio.TimeoutError:
                    print("⏰ No data received within timeout")
                    return False
                    
        except Exception as e:
            print(f"❌ Dashboard WebSocket test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test REST API endpoints"""
        print("🔧 Testing API Endpoints...")
        
        try:
            # Test source status endpoint
            response = requests.get(f"{BACKEND_URL}/api/source-status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Source Status: {status}")
                
                # Test latest data endpoint
                response = requests.get(f"{BACKEND_URL}/api/latest-data")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Latest Data: {data}")
                    return True
                else:
                    print(f"❌ Latest data endpoint failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Source status endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    async def test_fallback_mechanism(self):
        """Test automatic fallback from WiFi to USB"""
        print("🔧 Testing Fallback Mechanism...")
        
        try:
            # First, send WiFi data
            async with websockets.connect(WIFI_WS_URL) as websocket:
                wifi_data = {
                    "soil": 50,
                    "temperature": 29.0,
                    "humidity": 60.0,
                    "rain": 0,
                    "pump": 0,
                    "light": 400,
                    "flow": 0.0,
                    "total": 50.0
                }
                
                await websocket.send(json.dumps(wifi_data))
                print("📤 Sent WiFi data")
                await asyncio.sleep(1)
                
                # Check source status
                response = requests.get(f"{BACKEND_URL}/api/source-status")
                status = response.json()
                print(f"📊 Source after WiFi: {status['active_source']}")
                
            # Wait for WiFi timeout (should switch to USB)
            print("⏳ Waiting for WiFi timeout (4 seconds)...")
            await asyncio.sleep(4)
            
            # Check source status again
            response = requests.get(f"{BACKEND_URL}/api/source-status")
            status = response.json()
            print(f"📊 Source after timeout: {status['active_source']}")
            
            if status['active_source'] == 'USB':
                print("✅ Fallback mechanism working!")
                return True
            else:
                print("❌ Fallback mechanism not working")
                return False
                
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
            return False
    
    async def simulate_sensor_data_stream(self, duration=30):
        """Simulate continuous sensor data stream"""
        print(f"🔧 Simulating sensor data stream for {duration} seconds...")
        
        try:
            async with websockets.connect(WIFI_WS_URL) as websocket:
                start_time = time.time()
                count = 0
                
                while time.time() - start_time < duration:
                    # Generate realistic sensor data
                    data = {
                        "soil": 30 + (count % 40),  # Varying soil moisture
                        "temperature": 25.0 + (count % 10),  # Varying temperature
                        "humidity": 50.0 + (count % 30),  # Varying humidity
                        "rain": 1 if count % 10 == 0 else 0,  # Occasional rain
                        "pump": 1 if (30 + (count % 40)) < 40 else 0,  # Auto pump logic
                        "light": 200 + (count % 200),  # Varying light
                        "flow": 2.0 if (1 if (30 + (count % 40)) < 40 else 0) else 0.0,  # Flow when pump on
                        "total": count * 0.1  # Accumulating total
                    }
                    
                    await websocket.send(json.dumps(data))
                    print(f"📤 Stream #{count+1}: Soil={data['soil']}%, Temp={data['temperature']}°C, Pump={'ON' if data['pump'] else 'OFF'}")
                    
                    count += 1
                    await asyncio.sleep(2)
                
                print(f"✅ Sent {count} sensor data packets")
                return True
                
        except Exception as e:
            print(f"❌ Data stream simulation failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Smart Agriculture Dual Ingestion System Tests")
        print("=" * 60)
        
        tests = [
            ("WiFi Connection", self.test_wifi_connection()),
            ("Dashboard Connection", self.test_dashboard_connection()),
            ("API Endpoints", self.test_api_endpoints()),
            ("Fallback Mechanism", self.test_fallback_mechanism()),
            ("Data Stream Simulation", self.simulate_sensor_data_stream(10))
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            results.append((test_name, result))
            print(f"Result: {'✅ PASS' if result else '❌ FAIL'}")
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Dual ingestion system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the backend and hardware connections.")

async def main():
    tester = DualIngestionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())