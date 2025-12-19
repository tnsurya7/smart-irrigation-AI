#!/usr/bin/env python3
"""
Test script for Telegram Alert System
Tests all alert types and functionality
"""

import time
from telegram_integration import (
    test_telegram_connection,
    notify_weather_alert,
    notify_irrigation_change,
    notify_critical_soil,
    notify_sensor_offline,
    notify_manual_override,
    send_daily_weather_report,
    send_water_usage_summary
)

def test_all_alerts():
    """Test all Telegram alert types"""
    print("🧪 Testing Telegram Alert System")
    print("=" * 40)
    
    # Test 1: Connection Test
    print("1. Testing connection...")
    if test_telegram_connection():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        return
    
    time.sleep(2)
    
    # Test 2: Weather Alert
    print("2. Testing weather alert...")
    weather_data = {
        "rain_probability": 65,
        "temperature": 28.5,
        "humidity": 75,
        "location": "Erode"
    }
    notify_weather_alert(weather_data)
    time.sleep(2)
    
    # Test 3: Irrigation Alert
    print("3. Testing irrigation alert...")
    notify_irrigation_change(True, "soil moisture low", 25.5)
    time.sleep(2)
    
    # Test 4: Critical Soil Alert
    print("4. Testing critical soil alert...")
    notify_critical_soil(12.3)
    time.sleep(2)
    
    # Test 5: Sensor Offline Alert
    print("5. Testing sensor offline alert...")
    notify_sensor_offline(8)
    time.sleep(2)
    
    # Test 6: Manual Override Alert
    print("6. Testing manual override alert...")
    notify_manual_override("ON", "admin")
    time.sleep(2)
    
    # Test 7: Daily Weather Report
    print("7. Testing daily weather report...")
    weather_report_data = {
        "location": "Erode",
        "temperature": 29.1,
        "humidity": 68,
        "rain_probability": 25,
        "weather_condition": "Partly Cloudy"
    }
    send_daily_weather_report(weather_report_data)
    time.sleep(2)
    
    # Test 8: Water Usage Summary
    print("8. Testing water usage summary...")
    send_water_usage_summary(45.7, 120)
    
    print("\n✅ All tests completed!")
    print("Check your Telegram chat for the messages.")

if __name__ == "__main__":
    test_all_alerts()