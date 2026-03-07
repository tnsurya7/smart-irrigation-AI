#!/usr/bin/env python3
"""
Test with Full Production Email Template
"""

import os
import asyncio
import smtplib
import aiohttp
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict

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

async def fetch_weather_data() -> Dict:
    """Fetch weather data from OpenWeather API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = "Erode,Tamil Nadu,IN"
    
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    
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

def generate_irrigation_decision(weather_data: Dict) -> Dict:
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

def generate_full_email_html(weather_data: Dict, decision: Dict, time_of_day: str = "morning") -> str:
    """Generate the FULL PRODUCTION HTML email template"""
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
        <title>🧪 FULL TEMPLATE TEST - {city_name}</title>
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
                    <span>🧪📧</span>
                    FULL TEMPLATE TEST
                </h1>
                <div class="date">{current_date} - {current_time}</div>
            </div>
            
            <!-- Greeting -->
            <div class="greeting-section">
                <h2>{greeting_title}</h2>
                <p>This is the FULL production email template with all styling and features!</p>
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
                    🧪 FULL TEMPLATE TEST - Every 3 Hours Schedule Active
                </div>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return html_content

async def send_full_template_email():
    """Send email with full production template"""
    print("🌤️ Fetching weather data...")
    weather_data = await fetch_weather_data()
    
    print("🧠 Generating irrigation decision...")
    decision = generate_irrigation_decision(weather_data)
    
    print("🎨 Generating FULL email template...")
    email_html = generate_full_email_html(weather_data, decision, "morning")
    
    print("📧 Sending email with full template...")
    
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    recipients = os.getenv('EMAIL_RECIPIENTS').split(',')
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🧪 FULL TEMPLATE TEST - {weather_data['city_name']} | Every 3 Hours"
    msg['From'] = f"Smart Agriculture System <{email_user}>"
    msg['To'] = ", ".join(recipients)
    
    html_part = MIMEText(email_html, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)

async def main():
    """Main test function"""
    print("🎨 FULL PRODUCTION EMAIL TEMPLATE TEST")
    print("=" * 50)
    
    try:
        await send_full_template_email()
        
        print("✅ FULL TEMPLATE EMAIL SENT!")
        print("📧 Check your inbox for the beautiful email template")
        print("🎨 This is the EXACT template used in production")
        print("⏰ Scheduled to send every 3 hours automatically")
        
        recipients = os.getenv('EMAIL_RECIPIENTS').split(',')
        print(f"\n📬 Recipients:")
        for email in recipients:
            print(f"   • {email.strip()}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())