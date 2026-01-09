#!/usr/bin/env python3
"""
Render Deployment - Daily Weather Email Service
Configured for production deployment on Render.com

This service will:
1. Send daily weather emails at 6:00 AM and 7:00 PM IST
2. Email recipients: ***REMOVED***, ***REMOVED***
3. Location: Erode, Tamil Nadu
4. Run continuously as a background service
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Set environment variables for production
os.environ['EMAIL_USER'] = '***REMOVED***'
os.environ['EMAIL_PASS'] = '***REMOVED***'
os.environ['EMAIL_RECIPIENTS'] = '***REMOVED***,***REMOVED***'
os.environ['OPENWEATHER_API_KEY'] = '***REMOVED***'
os.environ['SMTP_HOST'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['WEATHER_CITY'] = 'Erode,Tamil Nadu,IN'

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from daily_weather_email_service import initialize_daily_weather_email

def main():
    """Main function for Render deployment"""
    logger.info("🌱 Starting Daily Weather Email Service on Render...")
    logger.info("📧 Recipients: ***REMOVED***, ***REMOVED***")
    logger.info("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
    logger.info("📍 Location: Erode, Tamil Nadu")
    logger.info("🌐 Environment: Production (Render)")
    
    try:
        # Initialize the service
        service = initialize_daily_weather_email()
        
        if service:
            logger.info("✅ Daily Weather Email Service started successfully on Render!")
            logger.info("📅 Emails will be sent at 6:00 AM and 7:00 PM IST daily")
            logger.info("🔄 Service is running continuously...")
            
            # Keep the service running indefinitely
            while True:
                try:
                    time.sleep(300)  # Sleep for 5 minutes, then check again
                    logger.debug("🔄 Service heartbeat - still running...")
                except KeyboardInterrupt:
                    logger.info("👋 Service stopped by interrupt")
                    break
                except Exception as e:
                    logger.error(f"⚠️ Service error: {e}")
                    logger.info("🔄 Continuing service...")
                    time.sleep(60)  # Wait 1 minute before continuing
                    
        else:
            logger.error("❌ Failed to start Daily Weather Email Service")
            logger.error("💡 Check email configuration and API keys")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Critical error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()