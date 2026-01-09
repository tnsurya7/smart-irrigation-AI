"""
Weather Email Integration Module
Import this in your main backend.py to automatically start the daily weather email service
This module is completely independent and won't affect existing functionality

Usage in backend.py:
# Add this single line at the end of backend.py:
# import weather_email_integration
"""

import os
import sys
import threading
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def start_weather_email_service():
    """Start the weather email service in a separate thread"""
    try:
        from daily_weather_email_service import initialize_daily_weather_email
        
        print("🌱 Auto-starting Daily Weather Email Service...")
        
        # Load environment variables from .env.local if it exists
        env_file = current_dir / ".env.local"
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
            print("✅ Daily Weather Email Service auto-started successfully!")
            print("📅 Scheduled to send daily emails at 6:30 AM IST")
        else:
            print("⚠️ Daily Weather Email Service failed to start (main app continues normally)")
            
    except Exception as e:
        print(f"⚠️ Daily Weather Email Service initialization error: {e}")
        print("⚠️ Main application will continue without daily weather emails")

def auto_start_in_thread():
    """Start the weather email service in a background thread"""
    def service_thread():
        start_weather_email_service()
    
    # Start in daemon thread so it doesn't prevent main app from shutting down
    thread = threading.Thread(target=service_thread, daemon=True)
    thread.start()

# Auto-start when this module is imported
print("🔄 Daily Weather Email Service: Auto-initialization starting...")
auto_start_in_thread()
print("🔄 Daily Weather Email Service: Auto-initialization completed")