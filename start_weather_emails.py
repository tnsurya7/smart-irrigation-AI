#!/usr/bin/env python3
"""
Start Daily Weather Email Service
Configured to send emails to:
- suryakumar56394@gmail.com
- monikam11g1@gmail.com

Schedule:
- Morning: 6:00 AM IST
- Evening: 7:00 PM IST
"""

import os
import sys
import time
from pathlib import Path

# Set environment variables
os.environ['EMAIL_RECIPIENTS'] = 'suryakumar56394@gmail.com,monikam11g1@gmail.com'
os.environ['OPENWEATHER_API_KEY'] = '59ade005948b4c8f58a100afc603f047'

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from daily_weather_email_service import initialize_daily_weather_email

def main():
    """Start the daily weather email service"""
    print("🌱 Starting Daily Weather Email Service...")
    print("📧 Recipients: suryakumar56394@gmail.com, monikam11g1@gmail.com")
    print("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
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
    
    # Initialize the service
    service = initialize_daily_weather_email()
    
    if service:
        print("✅ Daily Weather Email Service is running!")
        print("📅 Emails will be sent at 6:00 AM and 7:00 PM IST daily")
        print("🔄 Service is running in the background...")
        print("")
        print("💡 To send a test email now, uncomment the test lines in the service")
        print("🛑 Press Ctrl+C to stop the service")
        print("")
        
        # Keep the service running
        try:
            while True:
                time.sleep(60)  # Sleep for 1 minute
        except KeyboardInterrupt:
            print("\n👋 Daily Weather Email Service stopped by user")
    else:
        print("❌ Failed to start Daily Weather Email Service")
        print("💡 Please check your email configuration in .env.local")
        sys.exit(1)

if __name__ == "__main__":
    main()