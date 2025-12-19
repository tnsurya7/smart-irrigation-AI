#!/usr/bin/env python3
"""
Test script for Interactive Telegram Bot
Tests various API endpoints that the bot uses
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

def test_weather_endpoint():
    """Test weather endpoint"""
    print("🌤️ Testing Weather Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weather: {data['temperature']}°C, {data['humidity']}%, Rain: {data['rain_probability']}%")
            return True
        else:
            print(f"❌ Weather API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    print("\n📊 Testing Dashboard Summary...")
    try:
        response = requests.get(f"{BACKEND_URL}/daily-summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard: {data['averages']['avg_soil_moisture']}% soil, {data['irrigation']['pump_on_count']} pump cycles")
            return True
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard API error: {e}")
        return False

def test_sensor_status():
    """Test sensor status endpoint"""
    print("\n🚿 Testing Sensor Status...")
    try:
        response = requests.get(f"{BACKEND_URL}/sensor-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sensors: {data['status']}, Pump: {data['pump_status']}")
            return True
        else:
            print(f"❌ Sensor API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sensor API error: {e}")
        return False

def test_model_report():
    """Test model report endpoint"""
    print("\n🤖 Testing Model Report...")
    try:
        response = requests.get(f"{BACKEND_URL}/model-report", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models: ARIMA {data['arima_accuracy']}%, ARIMAX {data['arimax_accuracy']}%")
            return True
        else:
            print(f"❌ Model API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model API error: {e}")
        return False

def test_telegram_connection():
    """Test Telegram connection"""
    print("\n📱 Testing Telegram Connection...")
    try:
        response = requests.post(f"{BACKEND_URL}/telegram/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Telegram: {data['status']}")
            return True
        else:
            print(f"❌ Telegram API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Interactive Telegram Bot API Tests")
    print("=" * 50)
    
    tests = [
        test_weather_endpoint,
        test_dashboard_summary,
        test_sensor_status,
        test_model_report,
        test_telegram_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Interactive bot is ready!")
    else:
        print("⚠️ Some tests failed. Check the backend services.")

if __name__ == "__main__":
    main()