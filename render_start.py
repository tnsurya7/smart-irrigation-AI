#!/usr/bin/env python3
"""
Render Startup Script
This script starts both your main FastAPI backend and the weather email service
Use this as your Render start command: python render_start.py
"""

import os
import sys
import threading
import time
import logging
from pathlib import Path

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def start_weather_email_service():
    """Start the weather email service"""
    try:
        # Set environment variables for weather service
        os.environ['EMAIL_USER'] = 'suryakumar56394@gmail.com'
        os.environ['EMAIL_PASS'] = 'iyaweppkgwibgqry'
        os.environ['EMAIL_RECIPIENTS'] = 'suryakumar56394@gmail.com,monikam11g1@gmail.com'
        os.environ['OPENWEATHER_API_KEY'] = '59ade005948b4c8f58a100afc603f047'
        
        from daily_weather_email_service import initialize_daily_weather_email
        
        logger.info("🌱 Starting Daily Weather Email Service on Render...")
        service = initialize_daily_weather_email()
        
        if service:
            logger.info("✅ Weather Email Service started successfully!")
            logger.info("📧 Recipients: suryakumar56394@gmail.com, monikam11g1@gmail.com")
            logger.info("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
        else:
            logger.warning("⚠️ Weather Email Service failed to start")
            
    except Exception as e:
        logger.error(f"❌ Weather Email Service error: {e}")

def start_main_backend():
    """Start the main FastAPI backend"""
    try:
        logger.info("🚀 Starting main FastAPI backend...")
        
        # Import and run the main backend
        import uvicorn
        from backend import app
        
        # Get port from environment (Render sets this)
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"🌐 Starting FastAPI on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        logger.error(f"❌ Main backend error: {e}")
        sys.exit(1)

def main():
    """Main function for Render deployment"""
    logger.info("🚀 Starting Smart Agriculture System on Render...")
    
    # Start weather email service in background thread
    weather_thread = threading.Thread(target=start_weather_email_service, daemon=True)
    weather_thread.start()
    
    # Give weather service a moment to start
    time.sleep(2)
    
    # Start main backend (this will block)
    start_main_backend()

if __name__ == "__main__":
    main()