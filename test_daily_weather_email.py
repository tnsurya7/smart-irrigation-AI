"""
Test Script for Daily Weather Email Service (Python Version)
Run this to test the email functionality manually
"""

import asyncio
import os
from daily_weather_email_service import DailyWeatherEmailService

async def test_weather_email():
    print("🧪 Testing Daily Weather Email Service (Python)...\n")
    
    try:
        # Create service instance
        service = DailyWeatherEmailService()
        
        print("📧 Email Configuration:")
        print(f"- SMTP Host: {service.smtp_host}")
        print(f"- SMTP Port: {service.smtp_port}")
        print(f"- Email User: {service.email_user}")
        print(f"- Recipients: {', '.join(service.recipients)}")
        print(f"- City: {service.city}")
        print(f"- API Key: {'Configured ✅' if service.api_key else 'Missing ❌'}")
        print("")
        
        # Test weather data fetch
        print("🌤️ Fetching weather data...")
        weather_data = await service.fetch_weather_data()
        print("Weather Data:", {
            "city": weather_data["city_name"],
            "temperature": str(weather_data["temperature"]) + "°C",
            "humidity": str(weather_data["humidity"]) + "%",
            "description": weather_data["description"],
            "has_rain": weather_data["has_rain"],
            "rain_probability": str(weather_data["rain_probability"]) + "%"
        })
        print("")
        
        # Test irrigation decision
        print("🚿 Generating irrigation decision...")
        decision = service.generate_irrigation_decision(weather_data)
        print("Irrigation Decision:", {
            "rain_alert": decision["rain_alert"],
            "irrigation_status": decision["irrigation_status"],
            "recommendation": decision["irrigation_recommendation"]
        })
        print("")
        
        # Test email generation
        print("📨 Testing email generation...")
        email_html = service.generate_email_html(weather_data, decision)
        print(f"✅ Email HTML generated successfully ({len(email_html)} characters)")
        
        # Uncomment the following lines to actually send a test email
        """
        print("📧 Sending test email...")
        await service.send_test_email()
        print("✅ Test email sent successfully!")
        """
        
        print("\n🎉 All tests passed! Daily Weather Email Service (Python) is working correctly.")
        print("\n📝 To send actual emails:")
        print("1. Set environment variables or update .env.local with your email credentials")
        print("2. Uncomment the email sending lines in this test script")
        print("3. Run this test again")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_weather_email())