"""
OpenRouter ChatGPT-4o Chatbot Router
Smart Agriculture Dashboard with intelligent query classification
Reduces API costs by using rule-based responses for weather/irrigation
"""

import os
import json
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def classify_query(text: str) -> str:
    """Classify user query to reduce API costs"""
    t = text.lower()
    
    # Weather queries (NO AI needed)
    weather_keywords = ["weather", "mala", "rain", "varuma", "temperature", "temp", "climate", "hot", "cold", "sunny", "cloudy", "mausam"]
    if any(w in t for w in weather_keywords):
        return "weather"
    
    # Irrigation queries (Rule-based, NO AI needed)
    irrigation_keywords = ["irrigation", "watering", "paani", "neer", "water", "pump", "spray"]
    if any(w in t for w in irrigation_keywords):
        return "irrigation"
    
    # Everything else uses AI (controlled usage)
    return "ai"

def get_weather_data(city: str = "Erode") -> Dict[str, Any]:
    """Get weather data from OpenWeather API"""
    if not OPENWEATHER_API_KEY:
        raise Exception("Weather API key not configured")
    
    try:
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        # Forecast for rain probability
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        rain_probability = 0
        if forecast_response.ok:
            forecast_data = forecast_response.json()
            next_24h = forecast_data['list'][:8]  # Next 24 hours
            rain_forecasts = [f for f in next_24h if 'rain' in f.get('weather', [{}])[0].get('main', '').lower()]
            rain_probability = round((len(rain_forecasts) / len(next_24h)) * 100)
        
        return {
            "city": current_data['name'],
            "temperature": round(current_data['main']['temp']),
            "humidity": current_data['main']['humidity'],
            "condition": current_data['weather'][0]['description'],
            "rain_probability": rain_probability,
            "feels_like": round(current_data['main']['feels_like']),
            "wind_speed": current_data.get('wind', {}).get('speed', 0)
        }
        
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        raise Exception("Weather service temporarily unavailable")

def format_weather_response(weather_data: Dict[str, Any], user_message: str) -> str:
    """Format weather response in appropriate language"""
    temp = weather_data['temperature']
    humidity = weather_data['humidity']
    rain_prob = weather_data['rain_probability']
    condition = weather_data['condition']
    city = weather_data['city']
    
    # Detect language from user message
    if any(word in user_message.lower() for word in ['mala', 'varuma', 'iniku', 'nalla']):
        # Tamil/Tanglish
        return f"🌤️ {city}-la iniku weather: {temp}°C, {condition}. 💧 Humidity {humidity}%, 🌧️ Rain chance {rain_prob}%. {'💧 Irrigation pannalam!' if rain_prob < 30 else '🌧️ Rain varalam, irrigation vendam!'} Let me know if you need more help 🙂"
    else:
        # English
        return f"🌤️ {city} weather today: {temp}°C, {condition}. 💧 Humidity {humidity}%, 🌧️ Rain chance {rain_prob}%. {'💧 Good for irrigation!' if rain_prob < 30 else '🌧️ Rain expected, avoid irrigation!'} Let me know if you need more help 🙂"

def get_irrigation_advice(user_message: str) -> str:
    """Rule-based irrigation advice (NO AI cost)"""
    try:
        # Get current weather for irrigation decision
        weather = get_weather_data()
        rain_prob = weather['rain_probability']
        
        # Detect language
        if any(word in user_message.lower() for word in ['paani', 'neer', 'irrigation']):
            if rain_prob > 40:
                return "🌧️ Rain expected today. Avoid irrigation to prevent waterlogging. Check again tomorrow! Let me know if you need more help 🙂"
            else:
                return "💧 Good time for irrigation! Water early morning (6-8 AM) or evening (6-8 PM) for best results. Let me know if you need more help 🙂"
        else:
            if rain_prob > 40:
                return "🌧️ மழை வரும், இன்று நீர்ப்பாசனம் வேண்டாம். நாளை பார்க்கலாம்! மேலும் உதவி வேண்டுமா 🙂"
            else:
                return "💧 நீர்ப்பாசனம் செய்யலாம்! காலை 6-8 மணி அல்லது மாலை 6-8 மணிக்கு தண்ணீர் கொடுங்கள். மேலும் உதவி வேண்டுமா 🙂"
                
    except Exception:
        return "💧 For irrigation advice, check weather conditions first. Water early morning or evening for best results. Let me know if you need more help 🙂"

def call_openrouter_safe(user_message: str) -> str:
    """Call OpenRouter with cost protection and limits"""
    if not OPENROUTER_API_KEY:
        return "🤖 AI service not configured. I can still help with weather and irrigation questions! Let me know if you need more help 🙂"
    
    # Hard limits to prevent cost overrun
    if len(user_message) > 300:
        return "Please ask in shorter sentences for better help. Let me know if you need more help 🙂"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smart-agriculture-dashboard.vercel.app",
        "X-Title": "Smart Agriculture Chatbot"
    }
    
    # Cost-controlled payload
    payload = {
        "model": "openai/gpt-4o-mini",  # Cheaper model
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful farming assistant. Answer briefly in 2 lines max. Use emojis. Be friendly."
            },
            {
                "role": "user",
                "content": user_message[:200]  # Hard cut input
            }
        ],
        "max_tokens": 80,  # Hard limit
        "temperature": 0.3,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 402:
            return "🤖 AI service needs credits. I can still help with weather and irrigation questions! Let me know if you need more help 🙂"
        
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API error: {e}")
        return "🤖 AI service temporarily busy. I can help with weather and irrigation questions! Let me know if you need more help 🙂"
    except Exception as e:
        logger.error(f"OpenRouter response error: {e}")
        return "🤖 Having technical difficulties. Try asking about weather or irrigation! Let me know if you need more help 🙂"

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Smart Agriculture Chatbot with intelligent query classification
    Reduces API costs by using rule-based responses for weather/irrigation
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            return ChatResponse(reply="Hello! 🌱 How can I help you with your farming needs today?")
        
        logger.info(f"Chat request: {user_message}")
        
        # Step 1: Classify Query (NO API cost)
        query_type = classify_query(user_message)
        logger.info(f"Query classified as: {query_type}")
        
        # Step 2: Handle Weather Queries (NO AI cost)
        if query_type == "weather":
            try:
                weather_data = get_weather_data("Erode")
                reply = format_weather_response(weather_data, user_message)
                logger.info("Weather response generated (cost: ₹0.00)")
                return ChatResponse(reply=reply)
            except Exception as e:
                logger.error(f"Weather service error: {e}")
                return ChatResponse(reply="🌤️ Weather service temporarily unavailable. Please try again in a moment. Let me know if you need more help 🙂")
        
        # Step 3: Handle Irrigation Queries (Rule-based, NO AI cost)
        elif query_type == "irrigation":
            reply = get_irrigation_advice(user_message)
            logger.info("Irrigation advice generated (cost: ₹0.00)")
            return ChatResponse(reply=reply)
        
        # Step 4: Handle AI Queries (Controlled cost)
        else:
            reply = call_openrouter_safe(user_message)
            logger.info("AI response generated (controlled cost)")
            return ChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(reply="🤖 I'm having some technical difficulties right now. I can help with weather and irrigation questions! Let me know if you need more help 🙂")

@router.get("/chat/health")
async def chat_health():
    """Health check for chatbot service"""
    return {
        "status": "healthy",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "weather_api_configured": bool(OPENWEATHER_API_KEY),
        "service": "Smart Agriculture Chatbot"
    }