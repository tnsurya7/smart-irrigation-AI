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
    """Start the weather email service in a background thread with proper event loop"""
    try:
        # Create and set event loop for this thread
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use environment variables only - no hardcoded credentials
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        email_recipients = os.getenv('EMAIL_RECIPIENTS')
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not all([email_user, email_pass, email_recipients, api_key]):
            logger.warning("⚠️ Weather email service: Missing required environment variables")
            logger.info("Required: EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENTS, OPENWEATHER_API_KEY")
            return
        
        # Import and initialize the service
        from daily_weather_email_service import initialize_daily_weather_email
        
        logger.info("🌱 Auto-starting Daily Weather Email Service...")
        logger.info("📧 Email service configured via environment variables")
        logger.info("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
        
        service = initialize_daily_weather_email()
        
        if service:
            logger.info("✅ Daily Weather Email Service auto-started successfully!")
            # Keep the event loop running to maintain the scheduler
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("🛑 Weather Email Service stopped")
                if hasattr(service, 'scheduler') and service.scheduler.running:
                    service.stop_scheduler()
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