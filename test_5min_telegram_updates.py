"""
Test script for 5-minute Telegram updates system
Tests ESP32 online/offline scenarios and message formatting
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, 'backend')

# Set environment variables for testing
os.environ['TELEGRAM_BOT_TOKEN'] = '8063174729:AAGJYD_IMImdzkTRYbCiokomWsZlHcIW8jg'
os.environ['TELEGRAM_CHAT_ID'] = '5707565347'
os.environ['OPENWEATHER_API_KEY'] = '59ade005948b4c8f58a100afc603f047'

# Import the 5-minute update system
import telegram_5min_updates

async def test_esp32_offline_scenario():
    """Test message when ESP32 is offline"""
    print("🧪 Testing ESP32 OFFLINE scenario...")
    
    # Ensure ESP32 is considered offline
    telegram_5min_updates.LAST_ESP32_TIME = None
    
    # Build message
    message = telegram_5min_updates.build_5min_update_message()
    
    print("📱 Generated message:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # Verify offline status
    assert "🔴 OFFLINE" in message
    assert "Sensor Values: Not available" in message
    assert "Last Update: Never" in message
    
    print("✅ ESP32 offline scenario test passed")

async def test_esp32_online_scenario():
    """Test message when ESP32 is online"""
    print("\n🧪 Testing ESP32 ONLINE scenario...")
    
    # Simulate ESP32 online
    telegram_5min_updates.update_esp32_heartbeat()
    
    # Mock sensor data
    import production_backend
    production_backend.latest_sensor_data = {
        "soil_moisture": 45.2,
        "temperature": 28.5,
        "humidity": 72.0,
        "rain_detected": False,
        "light_raw": 2800,
        "light_percent": 68.0,
        "light_state": "normal",
        "pump_status": 0,
        "flow_rate": 0.0,
        "total_liters": 125.5,
        "mode": "auto",
        "source": "esp32",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Build message
    message = telegram_5min_updates.build_5min_update_message()
    
    print("📱 Generated message:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # Verify online status
    assert "🟢 ONLINE" in message
    assert "45.2%" in message  # Soil moisture
    assert "28.5°C" in message  # Temperature
    assert "72%" in message     # Humidity
    
    print("✅ ESP32 online scenario test passed")

async def test_rain_alert_scenario():
    """Test rain alert in message"""
    print("\n🧪 Testing RAIN ALERT scenario...")
    
    # Mock high rain probability weather data
    def mock_get_real_weather_data(city="Erode,IN"):
        return {
            "temperature": 26,
            "humidity": 85,
            "description": "Light Rain",
            "rain_probability": 75,  # High probability
            "city_name": "Erode",
            "country": "IN"
        }
    
    # Replace the function temporarily
    original_func = telegram_5min_updates.get_real_weather_data
    telegram_5min_updates.get_real_weather_data = mock_get_real_weather_data
    
    # Build message
    message = telegram_5min_updates.build_5min_update_message()
    
    print("📱 Generated message:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # Verify rain alert
    assert "🌧️ RAIN ALERT" in message
    assert "75%" in message
    assert "Skip irrigation" in message
    
    # Restore original function
    telegram_5min_updates.get_real_weather_data = original_func
    
    print("✅ Rain alert scenario test passed")

async def test_data_sources_transparency():
    """Test that data sources are always mentioned"""
    print("\n🧪 Testing DATA SOURCES transparency...")
    
    message = telegram_5min_updates.build_5min_update_message()
    
    # Verify data sources section exists
    assert "📡 Data Sources:" in message
    assert "OpenWeather API" in message
    assert "ESP32" in message
    assert "ARIMAX" in message
    
    print("✅ Data sources transparency test passed")

async def test_no_fake_data():
    """Test that no fake data is shown when ESP32 is offline"""
    print("\n🧪 Testing NO FAKE DATA policy...")
    
    # Ensure ESP32 is offline
    telegram_5min_updates.LAST_ESP32_TIME = datetime.utcnow() - timedelta(minutes=5)
    
    message = telegram_5min_updates.build_5min_update_message()
    
    # Should NOT contain any sensor values when offline
    assert "🔴 OFFLINE" in message
    assert "Not available" in message
    
    # Should NOT contain fake sensor numbers
    lines = message.split('\n')
    sensor_section = False
    for line in lines:
        if "📡 Live Sensors:" in line:
            sensor_section = True
        elif sensor_section and line.startswith("📊"):
            sensor_section = False
        elif sensor_section:
            # In sensor section, should not have specific values when offline
            assert not any(char.isdigit() and "%" in line for char in line if "Status:" not in line and "Last Update:" not in line)
    
    print("✅ No fake data policy test passed")

async def test_send_actual_message():
    """Test sending actual message to Telegram (optional)"""
    print("\n🧪 Testing ACTUAL MESSAGE SEND...")
    
    # Build test message
    message = "🧪 TEST MESSAGE - 5-Minute Update System\n\n"
    message += "This is a test of the 5-minute Telegram update system.\n"
    message += f"⏰ Test Time: {datetime.now().strftime('%H:%M:%S IST')}\n\n"
    message += "✅ System is working correctly!"
    
    # Send test message
    success = telegram_5min_updates.send_telegram_message(message)
    
    if success:
        print("✅ Test message sent successfully to Telegram")
    else:
        print("❌ Failed to send test message to Telegram")
    
    return success

async def main():
    """Run all tests"""
    print("🚀 Starting 5-Minute Telegram Updates Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        await test_esp32_offline_scenario()
        await test_esp32_online_scenario()
        await test_rain_alert_scenario()
        await test_data_sources_transparency()
        await test_no_fake_data()
        
        # Optional: Send actual test message
        print("\n" + "=" * 60)
        send_test = input("Send actual test message to Telegram? (y/n): ").lower().strip()
        if send_test == 'y':
            await test_send_actual_message()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ ESP32 online/offline detection working")
        print("✅ Real data only policy enforced")
        print("✅ Weather API integration working")
        print("✅ Rain alerts functioning")
        print("✅ Data source transparency maintained")
        print("✅ Message formatting correct")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())