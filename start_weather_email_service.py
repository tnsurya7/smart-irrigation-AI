"""
Standalone starter for Daily Weather Email Service
This can be run independently or imported into the main application
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from daily_weather_email_service import initialize_daily_weather_email

def main():
    """Start the daily weather email service"""
    print("🌱 Starting Daily Weather Email Service...")
    
    # Load environment variables from .env.local if it exists
    env_file = Path(".env.local")
    if env_file.exists():
        print("📄 Loading environment variables from .env.local")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Initialize the service
    service = initialize_daily_weather_email()
    
    if service:
        print("✅ Daily Weather Email Service is running!")
        print("📅 Scheduled to send daily emails at 6:30 AM IST")
        print("🔄 Service will run in the background...")
        
        # Keep the service running
        try:
            import time
            while True:
                time.sleep(60)  # Sleep for 1 minute
        except KeyboardInterrupt:
            print("\n👋 Daily Weather Email Service stopped by user")
    else:
        print("❌ Failed to start Daily Weather Email Service")
        sys.exit(1)

if __name__ == "__main__":
    main()