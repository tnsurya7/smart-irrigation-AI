"""
Simple test for 5-minute Telegram message format
Tests message structure without dependencies
"""

def test_message_format():
    """Test the message format matches requirements"""
    
    # Mock weather data
    weather_data = {
        "temperature": 29,
        "humidity": 68,
        "description": "Clear Sky",
        "rain_probability": 15,
        "city_name": "Erode",
        "country": "IN"
    }
    
    # Mock sensor data (ESP32 online)
    sensor_data = {
        "soil_moisture": 45.2,
        "temperature": 28.5,
        "humidity": 72.0,
        "rain_detected": False,
        "light_percent": 68.0,
        "light_state": "normal",
        "pump_status": 0,
        "total_liters": 125.5
    }
    
    # Mock pump data
    pump_data = {
        "pump_status": 0,
        "mode": "AUTO",
        "total_liters": 125.5
    }
    
    # Build message (ESP32 online scenario)
    message = "📈 SMART AGRICULTURE UPDATE (5-Min)\n\n"
    
    # Weather section
    message += f"🌤️ Weather (OpenWeather)\n"
    message += f"• Location: {weather_data['city_name']}\n"
    message += f"• Temperature: {weather_data['temperature']}°C\n"
    message += f"• Humidity: {weather_data['humidity']}%\n"
    message += f"• Condition: {weather_data['description']}\n"
    message += f"• Rain Probability: {weather_data['rain_probability']}%\n\n"
    
    # Sensor section (online)
    message += "📡 Live Sensors:\n"
    message += f"• Status: 🟢 ONLINE\n"
    message += f"• Soil Moisture: {sensor_data['soil_moisture']}%\n"
    message += f"• Temperature: {sensor_data['temperature']}°C\n"
    message += f"• Humidity: {sensor_data['humidity']}%\n"
    message += f"• Light: {sensor_data['light_percent']}% ({sensor_data['light_state']})\n"
    message += f"• Rain Detected: {'🌧️ Yes' if sensor_data['rain_detected'] else '☀️ No'}\n\n"
    
    # System status
    message += "📊 System Status\n"
    pump_status = "🟢 ON" if pump_data['pump_status'] == 1 else "🔴 OFF"
    message += f"• Pump: {pump_status}\n"
    message += f"• Mode: {pump_data['mode']}\n"
    message += f"• Water Used: {pump_data['total_liters']} L\n"
    message += f"• ARIMAX: 🟢 ACTIVE\n\n"
    
    # Data sources
    message += "📡 Data Sources:\n"
    message += f"• Weather: OpenWeather API\n"
    message += f"• Sensors: ESP32 (online)\n"
    message += f"• Prediction: ARIMAX\n\n"
    
    # Report time
    message += f"⏰ Report Time: 14:30:15 IST"
    
    print("📱 ESP32 ONLINE Message Format:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # Test ESP32 offline scenario
    message_offline = "📈 SMART AGRICULTURE UPDATE (5-Min)\n\n"
    
    # Weather section (same)
    message_offline += f"🌤️ Weather (OpenWeather)\n"
    message_offline += f"• Location: {weather_data['city_name']}\n"
    message_offline += f"• Temperature: {weather_data['temperature']}°C\n"
    message_offline += f"• Humidity: {weather_data['humidity']}%\n"
    message_offline += f"• Condition: {weather_data['description']}\n"
    message_offline += f"• Rain Probability: {weather_data['rain_probability']}%\n\n"
    
    # Sensor section (offline)
    message_offline += "📡 Live Sensors:\n"
    message_offline += f"• Status: 🔴 OFFLINE\n"
    message_offline += f"• Last Update: 5 minutes ago\n"
    message_offline += f"• Sensor Values: Not available\n\n"
    
    # System status (same)
    message_offline += "📊 System Status\n"
    message_offline += f"• Pump: {pump_status}\n"
    message_offline += f"• Mode: {pump_data['mode']}\n"
    message_offline += f"• Water Used: {pump_data['total_liters']} L\n"
    message_offline += f"• ARIMAX: 🟢 ACTIVE\n\n"
    
    # Data sources (offline)
    message_offline += "📡 Data Sources:\n"
    message_offline += f"• Weather: OpenWeather API\n"
    message_offline += f"• Sensors: ESP32 (offline)\n"
    message_offline += f"• Prediction: ARIMAX\n\n"
    
    # Report time
    message_offline += f"⏰ Report Time: 14:30:15 IST"
    
    print("\n📱 ESP32 OFFLINE Message Format:")
    print("=" * 50)
    print(message_offline)
    print("=" * 50)
    
    # Test rain alert scenario
    weather_rain = weather_data.copy()
    weather_rain['rain_probability'] = 75
    
    message_rain = message.replace(f"• Rain Probability: {weather_data['rain_probability']}%", 
                                  f"• Rain Probability: {weather_rain['rain_probability']}%")
    
    # Add rain alert
    rain_alert = "\n🌧️ RAIN ALERT\n"
    rain_alert += f"• High rain probability: {weather_rain['rain_probability']}%\n"
    rain_alert += f"• Recommendation: Skip irrigation\n"
    
    message_rain = message_rain.replace("📡 Data Sources:", rain_alert + "\n📡 Data Sources:")
    
    print("\n📱 RAIN ALERT Message Format:")
    print("=" * 50)
    print(message_rain)
    print("=" * 50)
    
    # Validation checks
    print("\n🧪 VALIDATION CHECKS:")
    
    # Check required sections
    required_sections = [
        "📈 SMART AGRICULTURE UPDATE (5-Min)",
        "🌤️ Weather (OpenWeather)",
        "📡 Live Sensors:",
        "📊 System Status",
        "📡 Data Sources:",
        "⏰ Report Time:"
    ]
    
    for section in required_sections:
        if section in message:
            print(f"✅ {section}")
        else:
            print(f"❌ Missing: {section}")
    
    # Check offline transparency
    if "🔴 OFFLINE" in message_offline and "Not available" in message_offline:
        print("✅ ESP32 offline transparency")
    else:
        print("❌ ESP32 offline transparency missing")
    
    # Check data sources transparency
    if all(source in message for source in ["OpenWeather API", "ESP32", "ARIMAX"]):
        print("✅ Data sources transparency")
    else:
        print("❌ Data sources transparency missing")
    
    # Check rain alert
    if "🌧️ RAIN ALERT" in message_rain and "Skip irrigation" in message_rain:
        print("✅ Rain alert functionality")
    else:
        print("❌ Rain alert functionality missing")
    
    print("\n🎉 Message format validation complete!")

if __name__ == "__main__":
    test_message_format()