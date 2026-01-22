"""
OpenRouter ChatGPT-4o Chatbot Router
Integrated chatbot for Smart Agriculture Dashboard
Works with Web Dashboard, Mobile App, and Telegram Bot
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

def call_openrouter(messages: list, model: str = "openai/chatgpt-4o-latest") -> str:
    """Call OpenRouter API with ChatGPT-4o"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smart-agriculture-dashboard.vercel.app",
        "X-Title": "Smart Agriculture Chatbot"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API error: {e}")
        raise HTTPException(status_code=500, detail="Chatbot service temporarily unavailable")
    except (KeyError, IndexError) as e:
        logger.error(f"OpenRouter response parsing error: {e}")
        raise HTTPException(status_code=500, detail="Invalid response from chatbot service")

def detect_intent(user_message: str) -> Dict[str, Any]:
    """Step 1: Detect user intent using ChatGPT-4o"""
    
    intent_prompt = f"""
Analyze this user message and detect the intent. Return ONLY valid JSON.

User message: "{user_message}"

Return JSON format:
{{
    "intent": "weather" or "chat",
    "city": "city name if weather intent, null otherwise"
}}

Rules:
- If user asks about weather, temperature, rain, humidity, irrigation, farming conditions: intent = "weather"
- Extract city name if mentioned, default to "Erode" if weather intent but no city specified
- For all other messages: intent = "chat"
- Return ONLY the JSON, no other text
"""

    messages = [{"role": "user", "content": intent_prompt}]
    
    try:
        response = call_openrouter(messages)
        # Clean response and parse JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "").strip()
        
        intent_data = json.loads(response)
        return intent_data
        
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse intent JSON: {response}")
        # Fallback: simple keyword detection
        weather_keywords = ["weather", "temperature", "rain", "humidity", "irrigation", "farming", "climate", "forecast"]
        if any(keyword in user_message.lower() for keyword in weather_keywords):
            return {"intent": "weather", "city": "Erode"}
        else:
            return {"intent": "chat", "city": None}
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        return {"intent": "chat", "city": None}

def get_weather_data(city: str) -> Dict[str, Any]:
    """Get weather data from OpenWeather API"""
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key not configured")
    
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
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API error: {e}")
        raise HTTPException(status_code=500, detail="Weather service temporarily unavailable")
    except KeyError as e:
        logger.error(f"Weather data parsing error: {e}")
        raise HTTPException(status_code=404, detail=f"Weather data not found for {city}")

def generate_weather_response(user_message: str, weather_data: Dict[str, Any]) -> str:
    """Step 2: Generate farmer-friendly weather response"""
    
    weather_prompt = f"""
You are a helpful farming assistant. A farmer asked: "{user_message}"

Current weather data for {weather_data['city']}:
- Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
- Humidity: {weather_data['humidity']}%
- Condition: {weather_data['condition']}
- Rain probability: {weather_data['rain_probability']}%
- Wind speed: {weather_data['wind_speed']} m/s

Generate a farmer-friendly response that:
1. Answers their weather question in simple language
2. Uses appropriate emojis (🌡️🌧️🌱💧☀️🌤️)
3. Includes practical irrigation/farming advice
4. Responds in the same language as the user's question
5. Keep it concise (2-3 sentences max)
6. NO JSON in the response, just natural text

Example format:
"🌡️ Current temperature in [city] is [temp]°C with [condition]. 💧 Humidity is [humidity]% and rain chance is [rain]%. 🌱 [Irrigation advice based on conditions]."
"""

    messages = [{"role": "user", "content": weather_prompt}]
    return call_openrouter(messages)

def generate_chat_response(user_message: str) -> str:
    """Step 3: Generate normal chat response"""
    
    chat_prompt = f"""
You are a helpful farming and agriculture assistant chatbot for a Smart Agriculture Dashboard.

User message: "{user_message}"

Respond helpfully in:
- Simple, clear language
- Same language as the user's message
- Friendly, supportive tone
- Focus on farming/agriculture topics when relevant
- Keep responses concise (2-3 sentences)
- Use emojis when appropriate 🌱🚜👨‍🌾

If the question is not about farming, still be helpful but try to relate it back to agriculture when possible.
"""

    messages = [{"role": "user", "content": chat_prompt}]
    return call_openrouter(messages)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chatbot endpoint for Smart Agriculture Dashboard
    Works with Web Dashboard, Mobile App, and Telegram Bot
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            return ChatResponse(reply="Hello! 🌱 How can I help you with your farming needs today?")
        
        logger.info(f"Chat request: {user_message}")
        
        # Step 1: Detect Intent
        intent_data = detect_intent(user_message)
        intent = intent_data.get("intent", "chat")
        city = intent_data.get("city", "Erode")
        
        logger.info(f"Detected intent: {intent}, city: {city}")
        
        # Step 2: Handle Weather Intent
        if intent == "weather":
            try:
                weather_data = get_weather_data(city)
                reply = generate_weather_response(user_message, weather_data)
            except HTTPException as e:
                if e.status_code == 404:
                    reply = f"🌍 Sorry, I couldn't find weather data for {city}. Please check the city name and try again."
                else:
                    reply = "🌤️ Weather service is temporarily unavailable. Please try again in a moment."
        
        # Step 3: Handle Normal Chat
        else:
            reply = generate_chat_response(user_message)
        
        logger.info(f"Chat response generated successfully")
        return ChatResponse(reply=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(reply="🤖 I'm having some technical difficulties right now. Please try again in a moment.")

@router.get("/chat/health")
async def chat_health():
    """Health check for chatbot service"""
    return {
        "status": "healthy",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "weather_api_configured": bool(OPENWEATHER_API_KEY),
        "service": "Smart Agriculture Chatbot"
    }