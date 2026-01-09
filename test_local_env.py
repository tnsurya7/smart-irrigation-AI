#!/usr/bin/env python3
"""
Test script to verify local environment variables are loaded correctly
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")

def test_env_vars():
    """Test if all required environment variables are set"""
    required_vars = {
        # Weather Email Service
        'EMAIL_USER': 'Weather email sender',
        'EMAIL_PASS': 'Weather email password', 
        'EMAIL_RECIPIENTS': 'Weather email recipients',
        'OPENWEATHER_API_KEY': 'OpenWeather API key',
        
        # Telegram Bot
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'TELEGRAM_CHAT_ID': 'Telegram chat ID',
        
        # Supabase Database
        'SUPABASE_URL': 'Supabase database URL',
        'SUPABASE_SERVICE_ROLE_KEY': 'Supabase service role key',
        'VITE_SUPABASE_URL': 'Frontend Supabase URL',
        'VITE_SUPABASE_ANON_KEY': 'Frontend Supabase anon key',
        
        # API Endpoints
        'VITE_API_BASE_URL': 'Frontend API base URL',
        'VITE_WS_URL': 'Frontend WebSocket URL',
        'BACKEND_URL': 'Backend URL for Telegram bot'
    }
    
    print("\n🔍 Checking environment variables:")
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if any(keyword in var.upper() for keyword in ['PASS', 'KEY', 'TOKEN']):
                if len(value) > 12:
                    masked_value = value[:6] + '*' * (len(value) - 12) + value[-6:]
                else:
                    masked_value = '*' * len(value)
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set ({description})")
            all_set = False
    
    return all_set

def test_weather_service():
    """Test if weather email service can be initialized"""
    try:
        from daily_weather_email_service import DailyWeatherEmailService
        
        print("\n🌤️ Testing weather email service initialization...")
        service = DailyWeatherEmailService()
        
        if service.api_key and service.email_user and service.email_pass and service.recipients:
            print("✅ Weather email service initialized successfully")
            print(f"📧 Recipients: {len(service.recipients)} configured")
            print(f"📍 Location: {service.city}")
            return True
        else:
            print("❌ Weather email service missing required configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing weather email service: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Local Environment Configuration")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ Found .env file: {env_file.absolute()}")
    else:
        print("⚠️ No .env file found, using system environment variables")
    
    # Test environment variables
    env_ok = test_env_vars()
    
    # Test weather service
    service_ok = test_weather_service()
    
    print("\n" + "=" * 50)
    if env_ok and service_ok:
        print("🎉 All tests passed! Local environment is configured correctly.")
        print("🚀 You can now run the weather email service locally.")
    else:
        print("❌ Some tests failed. Please check your .env file configuration.")
        print("📝 Make sure all required environment variables are set in .env file.")