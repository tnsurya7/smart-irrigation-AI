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
            greeting = "Good Morning ☀️<br>Have a nice day and a successful farming day ahead."
            report_title = "🌅 Morning Weather Report"
        else:
            greeting = "Good Evening 🌅<br>Here's your evening weather update for tomorrow's planning."
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
            <title>Daily Weather Report - Smart Agriculture</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                    padding: 20px;
                }}
                
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 28px;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                
                .header .date {{
                    font-size: 16px;
                    opacity: 0.9;
                }}
                
                .greeting {{
                    background: linear-gradient(135deg, #81c784 0%, #66bb6a 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: 500;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .weather-card {{
                    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-left: 5px solid #4caf50;
                }}
                
                .weather-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }}
                
                .weather-location {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #2e7d32;
                }}
                
                .weather-icon {{
                    width: 60px;
                    height: 60px;
                }}
                
                .weather-details {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .weather-item {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                
                .weather-item .label {{
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .weather-item .value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #2e7d32;
                }}
                
                .weather-item .unit {{
                    font-size: 14px;
                    color: #666;
                }}
                
                .irrigation-section {{
                    background: {irrigation_bg_color};
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-left: 5px solid {irrigation_border_color};
                }}
                
                .irrigation-question {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 15px;
                }}
                
                .irrigation-answer {{
                    font-size: 24px;
                    font-weight: 700;
                    color: {irrigation_text_color};
                    margin-bottom: 10px;
                }}
                
                .irrigation-reason {{
                    font-size: 14px;
                    color: #666;
                    font-style: italic;
                }}
                
                .rain-alert {{
                    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                    border: 2px solid #f44336;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 25px;
                    text-align: center;
                }}
                
                .rain-alert .alert-icon {{
                    font-size: 30px;
                    margin-bottom: 10px;
                }}
                
                .rain-alert .alert-text {{
                    font-size: 16px;
                    font-weight: 600;
                    color: #c62828;
                }}
                
                .footer {{
                    background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                }}
                
                .footer .system-name {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .footer .location {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                
                @media (max-width: 600px) {{
                    .weather-header {{
                        flex-direction: column;
                        text-align: center;
                    }}
                    
                    .weather-details {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header h1 {{
                        font-size: 24px;
                    }}
                    
                    .greeting {{
                        font-size: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌱 {report_title}</h1>
                    <div class="date">{current_date} - {current_time}</div>
                </div>
                
                <div class="greeting">
                    {greeting}
                </div>
                
                <div class="content">
                    <div class="weather-card">
                        <div class="weather-header">
                            <div class="weather-location">📍 {city_name}</div>
                            <img src="{weather_icon_url}" alt="{description}" class="weather-icon">
                        </div>
                        
                        <div class="weather-details">
                            <div class="weather-item">
                                <div class="label">Temperature</div>
                                <div class="value">{temperature}<span class="unit">°C</span></div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Humidity</div>
                                <div class="value">{humidity}<span class="unit">%</span></div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Condition</div>
                                <div class="value" style="font-size: 16px; text-transform: capitalize;">{description}</div>
                            </div>
                            <div class="weather-item">
                                <div class="label">Rain Chance</div>
                                <div class="value">{rain_probability}<span class="unit">%</span></div>
                            </div>
                        </div>
                    </div>
                    
                    {rain_alert_html}
                    
                    <div class="irrigation-section">
                        <div class="irrigation-question">🚿 Is today good for irrigation?</div>
                        <div class="irrigation-answer">{irrigation_status}</div>
                        <div class="irrigation-reason">{irrigation_recommendation}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="system-name">Smart Agriculture System</div>
                    <div class="location">Location: Erode, Tamil Nadu</div>
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