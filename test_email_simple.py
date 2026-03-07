#!/usr/bin/env python3
"""
Simple Email Test - Send weather email without APScheduler
"""

import os
import asyncio
import smtplib
import aiohttp
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env file manually
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✅ .env file loaded")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

async def fetch_weather():
    """Fetch weather data"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = "Erode,Tamil Nadu,IN"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            return {
                "temperature": round(data["main"]["temp"]),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "city_name": data["name"]
            }

def send_email(weather_data):
    """Send email"""
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    recipients = os.getenv('EMAIL_RECIPIENTS').split(',')
    
    # Simple HTML email
    html_content = f"""
    <html>
    <body>
        <h2>🌤️ Weather Test Email</h2>
        <p><strong>Location:</strong> {weather_data['city_name']}</p>
        <p><strong>Temperature:</strong> {weather_data['temperature']}°C</p>
        <p><strong>Humidity:</strong> {weather_data['humidity']}%</p>
        <p><strong>Condition:</strong> {weather_data['description']}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <p><em>✅ Email service test successful!</em></p>
        <p><em>⏰ Scheduled emails will be sent every 3 hours</em></p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🧪 Weather Email Test - {weather_data['city_name']}"
    msg['From'] = f"Smart Agriculture <{email_user}>"
    msg['To'] = ", ".join(recipients)
    
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)

async def main():
    """Main test function"""
    print("🧪 Simple Weather Email Test")
    print("=" * 40)
    
    try:
        print("🌤️ Fetching weather data...")
        weather_data = await fetch_weather()
        print(f"✅ Weather: {weather_data['temperature']}°C, {weather_data['description']}")
        
        print("📧 Sending test email...")
        send_email(weather_data)
        print("✅ Test email sent successfully!")
        
        recipients = os.getenv('EMAIL_RECIPIENTS').split(',')
        print(f"📬 Check these inboxes:")
        for email in recipients:
            print(f"   • {email.strip()}")
        
        print("\n🎉 EMAIL TEST COMPLETED!")
        print("⏰ The scheduled service will send emails every 3 hours")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())