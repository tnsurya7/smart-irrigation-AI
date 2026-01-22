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
    weather_keywords = ["weather", "rain", "temperature", "humidity", "mala", "mazha", "barani", "climate", "temp", "hot", "cold", "sunny", "cloudy"]
    return any(keyword in user_message.lower() for keyword in weather_keywords)

def extract_city(user_message: str) -> str:
    """Extract city from user message"""
    message_lower = user_message.lower()
    
    if "erode" in message_lower:
        return "Erode"
    elif "tiruchengode" in message_lower or "thiruchengode" in message_lower:
        return "Tiruchengode"
    else:
        return "India"  # Default fallback

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

def get_weather_fallback(city: str) -> str:
    """STEP 3: Weather API fallback (NO AI)"""
    if not OPENWEATHER_API_KEY:
        raise Exception("Weather API key not configured")
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        city_name = data["name"]
        temperature = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        
        return f"🌤️ Weather in {city_name} today:\nTemperature: {temperature}°C\nHumidity: {humidity}%\nCondition: {description.title()}"
        
    except Exception as e:
        logger.warning(f"Weather API failed: {e} - using static fallback")
        raise Exception(f"Weather API failed: {e}")

def get_static_fallback() -> str:
    """STEP 4: Static final fallback"""
    return "⚠️ Service temporarily unavailable. Please try again later."

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Failsafe Response System with Priority Order:
    1️⃣ OpenRouter API → 2️⃣ Gemini API → 3️⃣ Weather API → 4️⃣ Static Fallback
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            return ChatResponse(reply="Hello! 🌱 How can I help you with your farming needs today?")
        
        logger.info(f"Chat request: {user_message}")
        
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
                
                # STEP 3: Weather Fallback (if weather intent detected)
                if detect_weather_intent(user_message):
                    try:
                        city = extract_city(user_message)
                        reply = get_weather_fallback(city)
                        logger.info(f"✅ Weather fallback response successful for {city}")
                        return ChatResponse(reply=reply)
                    except Exception as weather_error:
                        logger.warning(f"Weather API failed: {weather_error}")
                
                # STEP 4: Static Final Fallback
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