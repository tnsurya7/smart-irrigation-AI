#!/usr/bin/env python3
"""
Send Test Weather Emails
This script sends immediate test emails to verify the email functionality
Recipients: ***REMOVED***, ***REMOVED***
"""

import os
import sys
import asyncio
from pathlib import Path

# Set environment variables
os.environ['EMAIL_RECIPIENTS'] = '***REMOVED***,***REMOVED***'
os.environ['OPENWEATHER_API_KEY'] = '***REMOVED***'

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from daily_weather_email_service import DailyWeatherEmailService

async def send_test_emails():
    """Send test emails for both morning and evening"""
    print("🧪 Testing Daily Weather Email Service...")
    print("📧 Recipients: ***REMOVED***, ***REMOVED***")
    print("📍 Location: Erode, Tamil Nadu")
    print("")
    
    # Load environment variables from .env.local if it exists
    env_file = Path(".env.local")
    if env_file.exists():
        print("📄 Loading environment variables from .env.local")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("")
    
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
        
        # Check if email credentials are configured
        if service.email_user == "your-email@gmail.com" or service.email_pass == "your-app-password":
            print("⚠️ WARNING: Email credentials not configured!")
            print("📝 Please update .env.local with your actual email credentials:")
            print("   EMAIL_USER=your-actual-email@gmail.com")
            print("   EMAIL_PASS=your-app-password")
            print("")
            print("🧪 Continuing with weather data test only...")
            
            # Test weather data fetch only
            print("🌤️ Testing weather data fetch...")
            weather_data = await service.fetch_weather_data()
            print("✅ Weather data fetched successfully:")
            print(f"   🏙️ City: {weather_data['city_name']}")
            print(f"   🌡️ Temperature: {weather_data['temperature']}°C")
            print(f"   💧 Humidity: {weather_data['humidity']}%")
            print(f"   🌤️ Condition: {weather_data['description']}")
            print(f"   🌧️ Rain Probability: {weather_data['rain_probability']}%")
            
            # Test irrigation decision
            decision = service.generate_irrigation_decision(weather_data)
            print(f"   🚿 Irrigation Recommended: {decision['irrigation_status']}")
            print(f"   💡 Reason: {decision['irrigation_recommendation']}")
            
            return
        
        # Test weather data fetch
        print("🌤️ Fetching weather data...")
        weather_data = await service.fetch_weather_data()
        print("✅ Weather data fetched successfully")
        print("")
        
        # Send morning test email
        print("🌅 Sending morning test email...")
        await service.send_test_email("morning")
        print("✅ Morning test email sent!")
        print("")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Send evening test email
        print("🌆 Sending evening test email...")
        await service.send_test_email("evening")
        print("✅ Evening test email sent!")
        print("")
        
        print("🎉 All test emails sent successfully!")
        print("📧 Check the inboxes of:")
        print("   - ***REMOVED***")
        print("   - ***REMOVED***")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("")
        print("💡 Common issues:")
        print("   1. Email credentials not configured in .env.local")
        print("   2. Gmail app password not set up correctly")
        print("   3. Internet connection issues")
        print("   4. OpenWeather API rate limits")

if __name__ == "__main__":
    asyncio.run(send_test_emails())