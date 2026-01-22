"""
Daily Weather Email Automation Service (Python Version)
Standalone module for sending daily weather reports via email
Does not modify any existing Smart Agriculture functionality
"""

import os
import asyncio
import smtplib
import aiohttp
import schedule
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import json
import threading
from pathlib import Path

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

class DailyWeatherEmailService:
    def __init__(self):
        # Load environment variables
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.city = "Erode,Tamil Nadu,IN"
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        self.recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
        
        # Validate required environment variables
        if not all([self.api_key, self.email_user, self.email_pass, self.recipients]):
            print("❌ Daily Weather Email Service: Missing required environment variables")
            print("Required: OPENWEATHER_API_KEY, EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENTS")
            return
        
        print("📧 Daily Weather Email Service (Python): Initialized")

    async def fetch_weather_data(self) -> Dict:
        """Fetch weather data from OpenWeather API"""
        try:
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=metric"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(current_url) as current_response:
                    current_data = await current_response.json()
                
                async with session.get(forecast_url) as forecast_response:
                    forecast_data = await forecast_response.json()
            
            # Calculate rain probability from forecast
            rain_probability = 0
            has_rain = False
            
            if "list" in forecast_data and forecast_data["list"]:
                # Check next 8 forecasts (24 hours)
                today_forecasts = forecast_data["list"][:8]
                rain_forecasts = [
                    f for f in today_forecasts 
                    if "rain" in f.get("weather", [{}])[0].get("main", "").lower() or 
                    f.get("rain", {}).get("3h", 0) > 0
                ]
                rain_probability = round((len(rain_forecasts) / len(today_forecasts)) * 100)
                has_rain = len(rain_forecasts) > 0
            
            return {
                "temperature": round(current_data["main"]["temp"]),
                "humidity": current_data["main"]["humidity"],
                "description": current_data["weather"][0]["description"],
                "icon": current_data["weather"][0]["icon"],
                "has_rain": has_rain or "rain" in current_data["weather"][0]["main"].lower(),
                "rain_probability": rain_probability,
                "city_name": current_data["name"],
                "country": current_data["sys"]["country"]
            }
            
        except Exception as e:
            print(f"❌ Daily Weather Email Service: Failed to fetch weather data: {e}")
            raise e

    def generate_irrigation_decision(self, weather_data: Dict) -> Dict:
        """Generate irrigation decision based on weather data"""
        rain_probability = weather_data["rain_probability"]
        humidity = weather_data["humidity"]
        has_rain = weather_data["has_rain"]
        
        # Rain Alert Logic
        rain_alert = rain_probability > 50 or has_rain
        
        # Irrigation Decision Logic
        if rain_alert:
            irrigation_recommendation = "Not recommended - Rain expected"
            irrigation_status = "No"
        elif rain_probability <= 30 and humidity < 70:
            irrigation_recommendation = "Good for irrigation"
            irrigation_status = "Yes"
        else:
            irrigation_recommendation = "Not recommended - High humidity or rain chance"
            irrigation_status = "No"
        
        return {
            "rain_alert": rain_alert,
            "irrigation_recommendation": irrigation_recommendation,
            "irrigation_status": irrigation_status
        }

    def generate_email_html(self, weather_data: Dict, decision: Dict, time_of_day: str = "morning") -> str:
        """Generate HTML email content"""
        temperature = weather_data["temperature"]
        humidity = weather_data["humidity"]
        description = weather_data["description"]
        icon = weather_data["icon"]
        rain_probability = weather_data["rain_probability"]
        city_name = weather_data["city_name"]
        
        rain_alert = decision["rain_alert"]
        irrigation_recommendation = decision["irrigation_recommendation"]
        irrigation_status = decision["irrigation_status"]
        
        weather_icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Different greetings based on time of day
        if time_of_day == "morning":
            greeting_title = "Good Morning ☀️"
            greeting_message = "Have a nice day and a successful farming day ahead."
            report_title = "🌅 Morning Weather Report"
        else:
            greeting_title = "Good Evening 🌙"
            greeting_message = "Here's your evening weather update for tomorrow's planning."
            report_title = "🌆 Evening Weather Report"
        
        rain_alert_html = ""
        if rain_alert:
            rain_alert_html = """
            <div class="rain-alert">
                <div class="alert-icon">⚠️</div>
                <div class="alert-text">Rain expected today in Erode. Please avoid irrigation.</div>
            </div>
            """
        
        irrigation_bg_color = "linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)" if irrigation_status == "Yes" else "linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)"
        irrigation_border_color = "#4caf50" if irrigation_status == "Yes" else "#ff9800"
        irrigation_text_color = "#2e7d32" if irrigation_status == "Yes" else "#f57c00"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{time_of_day.title()} Weather Report - {city_name}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
                    min-height: 100vh;
                }}
                
                .email-container {{
                    max-width: 400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                
                .header {{
                    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                }}
                
                .header h1 {{
                    margin: 0;
                    font-size: 20px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}
                
                .header .date {{
                    margin: 8px 0 0 0;
                    font-size: 14px;
                    opacity: 0.9;
                    font-weight: 400;
                }}
                
                .greeting-section {{
                    background: #f8f9fa;
                    padding: 25px 20px;
                    text-align: center;
                }}
                
                .greeting-section h2 {{
                    margin: 0 0 8px 0;
                    color: #4CAF50;
                    font-size: 22px;
                    font-weight: 600;
                }}
                
                .greeting-section p {{
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                    line-height: 1.4;
                }}
                
                .location-section {{
                    background: #e8f5e8;
                    padding: 15px 20px;
                    text-align: center;
                }}
                
                .location-section p {{
                    margin: 0;
                    color: #4CAF50;
                    font-size: 16px;
                    font-weight: 600;
                }}
                
                .weather-cards {{
                    padding: 25px 20px;
                    background: white;
                }}
                
                .cards-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr 1fr;
                    gap: 2px;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                
                .weather-card {{
                    padding: 20px 12px;
                    text-align: center;
                    position: relative;
                }}
                
                .weather-card.temperature {{
                    background: linear-gradient(135deg, #FFF3CD 0%, #FFF8DC 100%);
                    border-left: 4px solid #FFC107;
                }}
                
                .weather-card.humidity {{
                    background: linear-gradient(135deg, #D1ECF1 0%, #E1F5FE 100%);
                    border-left: 4px solid #17A2B8;
                }}
                
                .weather-card.condition {{
                    background: linear-gradient(135deg, #D4EDDA 0%, #E8F5E9 100%);
                    border-left: 4px solid #28A745;
                }}
                
                .weather-card.rain {{
                    background: linear-gradient(135deg, #F8D7DA 0%, #FFEBEE 100%);
                    border-left: 4px solid #DC3545;
                }}
                
                .card-icon {{
                    font-size: 20px;
                    margin-bottom: 8px;
                    display: block;
                }}
                
                .card-label {{
                    font-size: 12px;
                    color: #666;
                    font-weight: 600;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .card-value {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #2E7D32;
                    line-height: 1;
                }}
                
                .card-value.condition-text {{
                    font-size: 11px;
                    text-transform: capitalize;
                    line-height: 1.2;
                    font-weight: 600;
                }}
                
                .irrigation-section {{
                    background: white;
                    padding: 25px 20px;
                    text-align: center;
                }}
                
                .irrigation-question {{
                    color: #4CAF50;
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                
                .irrigation-answer {{
                    background: white;
                    border: 2px solid {irrigation_border_color};
                    border-radius: 12px;
                    padding: 20px;
                    margin: 0 auto;
                    max-width: 280px;
                }}
                
                .irrigation-status {{
                    font-size: 28px;
                    font-weight: 700;
                    color: {irrigation_text_color};
                    margin-bottom: 8px;
                }}
                
                .irrigation-message {{
                    font-size: 14px;
                    color: {irrigation_text_color};
                    font-weight: 600;
                }}
                
                .footer {{
                    background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                
                .footer h3 {{
                    margin: 0 0 5px 0;
                    font-size: 16px;
                    font-weight: 600;
                }}
                
                .footer p {{
                    margin: 0;
                    font-size: 13px;
                    opacity: 0.9;
                }}
                
                .footer .test-note {{
                    margin-top: 10px;
                    font-size: 11px;
                    opacity: 0.7;
                }}
                
                /* Mobile Responsive */
                @media (max-width: 480px) {{
                    .email-container {{
                        margin: 10px;
                        max-width: none;
                    }}
                    
                    .cards-grid {{
                        grid-template-columns: 1fr 1fr;
                        gap: 8px;
                    }}
                    
                    .weather-card {{
                        padding: 15px 8px;
                    }}
                    
                    .card-value {{
                        font-size: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                
                <!-- Header -->
                <div class="header">
                    <h1>
                        <span>🌱📊</span>
                        {time_of_day.title()} Weather Report
                    </h1>
                    <div class="date">{current_date} - {current_time}</div>
                </div>
                
                <!-- Greeting -->
                <div class="greeting-section">
                    <h2>{greeting_title}</h2>
                    <p>{greeting_message}</p>
                </div>
                
                <!-- Location -->
                <div class="location-section">
                    <p>📍 {city_name}</p>
                </div>
                
                <!-- Weather Cards -->
                <div class="weather-cards">
                    <div class="cards-grid">
                        <div class="weather-card temperature">
                            <span class="card-icon">🌡️</span>
                            <div class="card-label">Temperature</div>
                            <div class="card-value">{temperature}°C</div>
                        </div>
                        
                        <div class="weather-card humidity">
                            <span class="card-icon">💧</span>
                            <div class="card-label">Humidity</div>
                            <div class="card-value">{humidity}%</div>
                        </div>
                        
                        <div class="weather-card condition">
                            <span class="card-icon">☁️</span>
                            <div class="card-label">Condition</div>
                            <div class="card-value condition-text">{description}</div>
                        </div>
                        
                        <div class="weather-card rain">
                            <span class="card-icon">🌧️</span>
                            <div class="card-label">Rain Chance</div>
                            <div class="card-value">{rain_probability}%</div>
                        </div>
                    </div>
                </div>
                
                <!-- Irrigation Section -->
                <div class="irrigation-section">
                    <div class="irrigation-question">
                        🚿 Is today good for irrigation?
                    </div>
                    <div class="irrigation-answer">
                        <div class="irrigation-status">{irrigation_status}</div>
                        <div class="irrigation-message">{irrigation_recommendation}</div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <h3>Smart Agriculture System</h3>
                    <p>Location: {city_name}, Tamil Nadu</p>
                    <div class="test-note">
                        ✅ Updated template design with proper grid layout
                    </div>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return html_content

    async def send_daily_weather_email(self, time_of_day: str = "morning"):
        """Send daily weather email"""
        try:
            print(f"🌤️ Daily Weather Email Service: Starting {time_of_day} weather email process...")
            
            # Fetch weather data
            weather_data = await self.fetch_weather_data()
            print(f"✅ Weather data fetched successfully for {weather_data['city_name']}")
            
            # Generate irrigation decision
            decision = self.generate_irrigation_decision(weather_data)
            
            # Generate email HTML
            email_html = self.generate_email_html(weather_data, decision, time_of_day)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            report_type = "Morning" if time_of_day == "morning" else "Evening"
            msg['Subject'] = f"🌱 {report_type} Weather Report - {weather_data['city_name']} | {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = f"Smart Agriculture System <{self.email_user}>"
            msg['To'] = ", ".join(self.recipients)
            
            # Attach HTML content
            html_part = MIMEText(email_html, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print(f"✅ {report_type} weather email sent successfully")
            print(f"📧 Recipients: {', '.join(self.recipients)}")
            print(f"🌡️ Temperature: {weather_data['temperature']}°C")
            print(f"💧 Humidity: {weather_data['humidity']}%")
            print(f"🌧️ Rain Probability: {weather_data['rain_probability']}%")
            print(f"🚿 Irrigation Recommended: {decision['irrigation_status']}")
            
        except Exception as e:
            print(f"❌ Daily Weather Email Service: Failed to send {time_of_day} weather email: {e}")
            # Don't raise error to prevent affecting main application

    def schedule_daily_email(self):
        """Schedule daily emails at 6:00 AM and 7:00 PM IST"""
        print("⏰ Daily Weather Email Service: Scheduling daily emails at 6:00 AM and 7:00 PM IST")
        
        # Schedule morning email at 6:00 AM IST
        schedule.every().day.at("06:00").do(
            lambda: asyncio.run(self.send_daily_weather_email("morning"))
        )
        
        # Schedule evening email at 7:00 PM IST (19:00)
        schedule.every().day.at("19:00").do(
            lambda: asyncio.run(self.send_daily_weather_email("evening"))
        )
        
        print("✅ Daily Weather Email Service: Morning (6:00 AM) and Evening (7:00 PM) schedules configured")

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        print("✅ Daily Weather Email Service: Scheduler thread started")

    async def send_test_email(self, time_of_day: str = "morning"):
        """Send a test email immediately"""
        print(f"🧪 Daily Weather Email Service: Sending test {time_of_day} email...")
        await self.send_daily_weather_email(time_of_day)

    def initialize(self):
        """Initialize the daily weather email service"""
        try:
            print("🚀 Daily Weather Email Service (Python): Initializing...")
            self.schedule_daily_email()
            self.run_scheduler()
            print("✅ Daily Weather Email Service (Python): Initialized successfully")
            print("📧 Email service configured via environment variables")
            print("⏰ Schedule: 6:00 AM and 7:00 PM IST daily")
            
            # Uncomment to send a test email on startup
            # asyncio.create_task(self.send_test_email("morning"))
            
        except Exception as e:
            print(f"❌ Daily Weather Email Service: Initialization failed: {e}")

# Global service instance
weather_email_service = None

def initialize_daily_weather_email():
    """Initialize the daily weather email service"""
    global weather_email_service
    try:
        print("🌱 Initializing Daily Weather Email Automation (Python)...")
        weather_email_service = DailyWeatherEmailService()
        weather_email_service.initialize()
        print("✅ Daily Weather Email Automation (Python) initialized successfully")
        return weather_email_service
    except Exception as e:
        print(f"❌ Failed to initialize Daily Weather Email Service: {e}")
        print("⚠️ Main application will continue without daily weather emails")
        return None

if __name__ == "__main__":
    # For testing purposes
    service = initialize_daily_weather_email()
    if service:
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Daily Weather Email Service stopped")