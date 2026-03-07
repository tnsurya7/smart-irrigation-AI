#!/usr/bin/env python3
"""
Test Daily Weather Email Service - Send Test Email Now
"""

import os
import asyncio
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("⚠️ dotenv not available, loading .env manually")
    # Manual .env loading
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ .env file loaded manually")
    except FileNotFoundError:
        print("❌ .env file not found")
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")

async def test_email_now():
    """Send a test weather email immediately"""
    print("🧪 Testing Daily Weather Email Service")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = {
        'OPENWEATHER_API_KEY': os.getenv('OPENWEATHER_API_KEY'),
        'EMAIL_USER': os.getenv('EMAIL_USER'),
        'EMAIL_PASS': os.getenv('EMAIL_PASS'),
        'EMAIL_RECIPIENTS': os.getenv('EMAIL_RECIPIENTS')
    }
    
    print("🔍 Checking Environment Variables:")
    missing_vars = []
    for var, value in required_vars.items():
        if value:
            if var == 'EMAIL_PASS':
                print(f"   ✅ {var}: {'*' * len(value)}")
            elif var == 'EMAIL_RECIPIENTS':
                recipients = value.split(',')
                print(f"   ✅ {var}: {len(recipients)} recipient(s)")
                for i, email in enumerate(recipients, 1):
                    print(f"      {i}. {email.strip()}")
            else:
                print(f"   ✅ {var}: {value[:10]}...")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False
    
    print("\n🚀 Initializing Weather Email Service...")
    
    try:
        # Import and initialize the service
        from daily_weather_email_service import DailyWeatherEmailService
        
        service = DailyWeatherEmailService()
        
        if not all([service.api_key, service.email_user, service.email_pass, service.recipients]):
            print("❌ Service initialization failed - missing configuration")
            return False
        
        print("✅ Service initialized successfully")
        print(f"📍 Weather Location: {service.city}")
        print(f"📧 SMTP Server: {service.smtp_host}:{service.smtp_port}")
        print(f"👤 Email User: {service.email_user}")
        print(f"📬 Recipients: {len(service.recipients)} email(s)")
        
        print("\n📤 Sending test email...")
        
        # Send test email
        await service.send_test_email("morning")
        
        print("\n✅ Test email sent successfully!")
        print("📧 Check your email inbox for the weather report")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🌤️ Daily Weather Email Test")
    print("Testing the updated every-3-hours email service")
    print("=" * 60)
    
    success = await test_email_now()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 EMAIL TEST COMPLETED SUCCESSFULLY!")
        print("📧 Weather email should arrive in your inbox shortly")
        print("⏰ Scheduled emails will now be sent every 3 hours")
    else:
        print("❌ EMAIL TEST FAILED")
        print("Please check your environment variables and try again")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)