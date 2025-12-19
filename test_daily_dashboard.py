#!/usr/bin/env python3
"""
Test script for Daily Dashboard Summary feature
Tests the comprehensive daily report functionality
"""

import requests
import json
from datetime import datetime
from telegram_integration import send_daily_dashboard_summary, test_telegram_connection

def test_daily_summary_api():
    """Test the daily summary API endpoint"""
    print("🧪 Testing Daily Summary API...")
    
    try:
        # Test the daily summary endpoint
        response = requests.get("http://localhost:8000/daily-summary", timeout=10)
        
        if response.status_code == 200:
            summary_data = response.json()
            print("✅ Daily summary API working")
            print(f"📊 Data points: {summary_data.get('averages', {}).get('data_points', 0)}")
            print(f"🌡️ Avg temp: {summary_data.get('averages', {}).get('avg_temperature', 0)}°C")
            print(f"💧 Avg soil: {summary_data.get('averages', {}).get('avg_soil_moisture', 0)}%")
            return summary_data
        else:
            print(f"❌ API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return None

def test_telegram_dashboard_report():
    """Test sending the dashboard report via Telegram"""
    print("\n📱 Testing Telegram Dashboard Report...")
    
    try:
        # Test sending via FastAPI endpoint
        response = requests.post("http://localhost:8000/send-daily-dashboard-report", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Dashboard report sent successfully")
            print(f"📅 Timestamp: {result.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to send report: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

def test_manual_dashboard_summary():
    """Test manual dashboard summary with mock data"""
    print("\n🔧 Testing Manual Dashboard Summary...")
    
    # Create mock summary data
    mock_summary = {
        "date": datetime.now().strftime("%B %d, %Y"),
        "location": "Erode",
        "averages": {
            "avg_temperature": 28.5,
            "avg_humidity": 65.2,
            "avg_soil_moisture": 42.8,
            "data_points": 1440
        },
        "weather": {
            "rain_probability": 35,
            "current_temp": 29.1,
            "current_humidity": 68
        },
        "irrigation": {
            "pump_on_count": 3,
            "pump_off_count": 3,
            "total_water_used": 15.6
        },
        "model": {
            "best_model": "ARIMAX",
            "arima_accuracy": 82.5,
            "arimax_accuracy": 94.6
        },
        "alerts": {
            "total_count": 2
        },
        "system": {
            "status": "live",
            "last_sensor_time": datetime.now().isoformat()
        }
    }
    
    # Test connection first
    if not test_telegram_connection():
        print("❌ Telegram connection failed")
        return False
    
    # Send manual summary
    success = send_daily_dashboard_summary(mock_summary)
    
    if success:
        print("✅ Manual dashboard summary sent")
        return True
    else:
        print("❌ Failed to send manual summary")
        return False

def main():
    """Main test function"""
    print("📊 Daily Dashboard Summary Test Suite")
    print("=" * 50)
    
    # Test 1: API endpoint
    summary_data = test_daily_summary_api()
    
    # Test 2: Telegram integration via API
    api_success = test_telegram_dashboard_report()
    
    # Test 3: Manual Telegram message
    manual_success = test_manual_dashboard_summary()
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"  API Endpoint: {'✅ Pass' if summary_data else '❌ Fail'}")
    print(f"  API → Telegram: {'✅ Pass' if api_success else '❌ Fail'}")
    print(f"  Manual Telegram: {'✅ Pass' if manual_success else '❌ Fail'}")
    
    if summary_data and (api_success or manual_success):
        print("\n🎉 Daily Dashboard Summary is working!")
        print("📱 Check your Telegram for the dashboard report.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()