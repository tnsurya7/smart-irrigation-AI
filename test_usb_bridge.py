#!/usr/bin/env python3
"""
Test ESP32 USB Bridge Setup
"""

import requests
import json
import time

# Test data that mimics ESP32 output
test_esp32_data = {
    "source": "esp32",
    "soil": 45,
    "temperature": 28.5,
    "humidity": 62,
    "rain_detected": False,
    "light_percent": 75,
    "light_state": "bright",
    "flow": 0,
    "total": 0,
    "pump": 0,
    "mode": "auto",
    "rain_expected": False
}

def test_backend_endpoint():
    """Test the backend USB bridge endpoint"""
    print("🧪 Testing ESP32 USB Bridge Backend Endpoint")
    print("=" * 50)
    
    backend_url = "https://smart-agriculture-backend-my7c.onrender.com"
    endpoint = "/demo/esp32"
    
    try:
        print(f"📡 Sending test data to {backend_url}{endpoint}")
        print(f"📊 Test data: {json.dumps(test_esp32_data, indent=2)}")
        
        response = requests.post(
            f"{backend_url}{endpoint}",
            json=test_esp32_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend endpoint working!")
            print(f"📧 Response: {json.dumps(result, indent=2)}")
            print(f"👥 Clients notified: {result.get('clients_notified', 0)}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Backend timeout - this is normal for Render cold starts")
        print("🔄 Try again in a few seconds")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def simulate_esp32_data():
    """Simulate sending multiple ESP32 data packets"""
    print("\n🔄 Simulating ESP32 data stream...")
    
    backend_url = "https://smart-agriculture-backend-my7c.onrender.com"
    endpoint = "/demo/esp32"
    
    for i in range(5):
        # Vary the data slightly
        test_data = test_esp32_data.copy()
        test_data["temperature"] = 28.5 + (i * 0.5)
        test_data["humidity"] = 62 + (i * 2)
        test_data["soil"] = 45 - (i * 3)
        
        try:
            response = requests.post(
                f"{backend_url}{endpoint}",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Packet {i+1}: Temp {test_data['temperature']}°C, Soil {test_data['soil']}% → {result['clients_notified']} clients")
            else:
                print(f"❌ Packet {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Packet {i+1} error: {e}")
        
        time.sleep(2)  # Wait 2 seconds between packets

def main():
    print("🌱 ESP32 USB Bridge Test Suite")
    print("=" * 60)
    
    # Test 1: Basic endpoint test
    test_backend_endpoint()
    
    # Test 2: Simulate data stream
    simulate_esp32_data()
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("📋 Next steps:")
    print("   1. Connect ESP32 via USB")
    print("   2. Run: node usb_esp32_bridge.js")
    print("   3. Open dashboard to see live data")
    print("   4. Mobile app will also show the same data")

if __name__ == "__main__":
    main()