"""
OpenRouter ChatGPT-4o Chatbot Router with Failsafe Response System
Priority: OpenRouter → Gemini → Weather → Static Fallback
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def detect_weather_intent(user_message: str) -> bool:
    """Detect if user is asking about weather"""
    weather_keywords = ["weather", "rain", "temperature", "humidity", "mala", "mazha", "barani", "climate", "temp", "hot", "cold", "sunny", "cloudy", "varuma", "forecast"]
    return any(keyword in user_message.lower() for keyword in weather_keywords)

def extract_city(user_message: str) -> str:
    """Extract city from user message - India only"""
    message_lower = user_message.lower()
    
    # Specific city detection
    if "erode" in message_lower:
        return "Erode,IN"
    elif "salem" in message_lower:
        return "Salem,IN"
    elif "tiruchengode" in message_lower or "thiruchengode" in message_lower:
        return "Tiruchengode,IN"
    elif "kerala" in message_lower:
        return "Kerala,IN"
    elif "chennai" in message_lower:
        return "Chennai,IN"
    elif "bangalore" in message_lower or "bengaluru" in message_lower:
        return "Bangalore,IN"
    elif "mumbai" in message_lower:
        return "Mumbai,IN"
    elif "delhi" in message_lower:
        return "Delhi,IN"
    elif "hyderabad" in message_lower:
        return "Hyderabad,IN"
    elif "pune" in message_lower:
        return "Pune,IN"
    else:
        return "India"  # Default fallback

def get_real_weather_data(city: str) -> str:
    """Get REAL weather data from OpenWeather API - NEVER use AI for weather"""
    if not OPENWEATHER_API_KEY:
        return "🌤️ Weather service not configured. Please try again later."
    
    try:
        # Direct OpenWeather API call
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        city_name = data["name"]
        temperature = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"].title()
        
        # Format real weather response
        return f"🌤️ Weather in {city_name}\n🌡️ Temperature: {temperature}°C\n💧 Humidity: {humidity}%\n☁️ Condition: {description}"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenWeather API error: {e}")
        return "🌤️ Weather service temporarily unavailable. Please try again later."
    except KeyError as e:
        logger.error(f"Weather data parsing error: {e}")
        return f"🌍 Weather data not found for {city}. Please check the city name."
    except Exception as e:
        logger.error(f"Weather service error: {e}")
        return "🌤️ Weather service temporarily unavailable. Please try again later."

def call_openrouter_primary(user_message: str) -> str:
    """STEP 1: OpenRouter API (Primary) with strict token limits"""
    if not OPENROUTER_API_KEY:
        raise Exception("OpenRouter API key not configured")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smart-agriculture-dashboard.vercel.app",
        "X-Title": "Smart Agriculture Chatbot"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful farming assistant. Answer briefly in 2 lines max. Use emojis. Be friendly."
            },
            {
                "role": "user",
                "content": user_message[:300]  # Input limit
            }
        ],
        "max_tokens": 200,  # STRICT LIMIT to avoid 402 errors
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        # Check for 402 Payment Required
        if response.status_code == 402:
            logger.warning("OpenRouter 402 Payment Required - falling back to Gemini")
            raise Exception("OpenRouter payment required")
        
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        logger.warning(f"OpenRouter failed: {e} - falling back to Gemini")
        raise Exception(f"OpenRouter failed: {e}")

def call_gemini_secondary(user_message: str) -> str:
    """STEP 2: Gemini API (Secondary) with output limits"""
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not configured")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You are a helpful farming assistant. Answer this question briefly in 2 lines max with emojis: {user_message[:300]}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 200,  # Limit output length
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip()
        else:
            raise Exception("No valid response from Gemini")
            
    except Exception as e:
        logger.warning(f"Gemini failed: {e} - falling back to weather")
        raise Exception(f"Gemini failed: {e}")

def get_static_fallback() -> str:
    """STEP 4: Static final fallback"""
    return "⚠️ Service temporarily unavailable. Please try again later."

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    CORRECT CHAT FLOW:
    Weather Intent → OpenWeather API (NEVER AI)
    Non-Weather → OpenRouter → Gemini → Static Fallback
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            return ChatResponse(reply="Hello! 🌱 How can I help you with your farming needs today?")
        
        logger.info(f"Chat request: {user_message}")
        
        # PRIORITY 1: Weather Intent Detection (NEVER use AI for weather)
        if detect_weather_intent(user_message):
            city = extract_city(user_message)
            reply = get_real_weather_data(city)
            logger.info(f"✅ Real weather data returned for {city}")
            return ChatResponse(reply=reply)
        
        # PRIORITY 2: Non-Weather Queries - Use AI Failsafe System
        # STEP 1: Try OpenRouter (Primary)
        try:
            reply = call_openrouter_primary(user_message)
            logger.info("✅ OpenRouter response successful")
            return ChatResponse(reply=reply)
        except Exception as openrouter_error:
            logger.warning(f"OpenRouter failed: {openrouter_error}")
            
            # STEP 2: Try Gemini (Secondary)
            try:
                reply = call_gemini_secondary(user_message)
                logger.info("✅ Gemini fallback response successful")
                return ChatResponse(reply=reply)
            except Exception as gemini_error:
                logger.warning(f"Gemini failed: {gemini_error}")
                
                # STEP 3: Static Final Fallback
                reply = get_static_fallback()
                logger.info("⚠️ Using static final fallback")
                return ChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"Chat endpoint critical error: {e}")
        # Even if everything fails, return static fallback (never crash)
        return ChatResponse(reply=get_static_fallback())

@router.get("/chat/health")
async def chat_health():
    """Health check for chatbot service"""
    return {
        "status": "healthy",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "weather_api_configured": bool(OPENWEATHER_API_KEY),
        "service": "Smart Agriculture Chatbot"
    }