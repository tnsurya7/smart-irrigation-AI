"""
Auto-start Weather Email Service
Add this import to your backend.py to automatically start the weather email service:

# Add this line at the end of your backend.py:
# import auto_start_weather_emails

This will start the weather email service in the background without affecting your main app.
"""

import os
import threading
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_weather_email_service():
    """Start the weather email service in a background thread"""
    try:
        # Set environment variables
        os.environ['EMAIL_USER'] = 'suryakumar56394@gmail.com'
        os.environ['EMAIL_PASS'] = 'iyaweppkgwibgqry'
        os.environ['EMAIL_RECIPIENTS'] = 'suryakumar56394@gmail.com,monikam11g1@gmail.com'
        os.environ['OPENWEATHER_API_KEY'] = '59ade005948b4c8f58a100afc603f047'
        
        # Import and initialize the service
        from daily_weather_email_service import initialize_daily_weather_email
        
        logger.info("🌱 Auto-starting Daily Weather Email Service...")
        logger.info("📧 Recipients: suryakumar56394@gmail.com, monikam11g1@gmail.com")
        logger.info("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
        
        service = initialize_daily_weather_email()
        
        if service:
            logger.info("✅ Daily Weather Email Service auto-started successfully!")
        else:
            logger.warning("⚠️ Daily Weather Email Service failed to start (main app continues)")
            
    except Exception as e:
        logger.error(f"⚠️ Weather Email Service error: {e}")
        logger.info("⚠️ Main application continues without weather emails")

def start_in_background():
    """Start the service in a daemon thread"""
    thread = threading.Thread(target=start_weather_email_service, daemon=True)
    thread.start()
    logger.info("🔄 Weather Email Service thread started")

# Auto-start when this module is imported
logger.info("🚀 Auto-starting Daily Weather Email Service...")
start_in_background()
logger.info("✅ Weather Email Service initialization completed")