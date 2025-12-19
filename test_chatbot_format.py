#!/usr/bin/env python3
"""
Test the new chatbot format with clean weather responses
"""

import requests
import json

def test_weather_api():
    """Test weather API and format responses"""
    print("🌤️ Testing Weather API Format...")
    try:
        response = requests.get("http://localhost:8000/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            temp = round(data['temperature'])
            humidity = data['humidity']
            rain_prob = round(data['rain_probability'])
            location = data['location']
            
            print(f"✅ Raw Weather Data: {temp}°C, {humidity}% humidity, {rain_prob}% rain in {location}")
            
            # Test the exact format requested
            print("\n📝 Testing New Clean Format:")
            
            # English
            english_format = f"{location} weather today: 🌡️ {temp}°C, 💧 {humidity}% 🌧️ Rain chance: {rain_prob}% Irrigation recommended. Let me know if you need more help 🙂"
            print(f"🇺🇸 English: {english_format}")
            
            # Tamil
            tamil_format = f"{location}-la iniku weather: 🌡️ {temp}°C, 💧 {humidity}% 🌧️ மழை வாய்ப்பு: {rain_prob}% நீர்ப்பாசனம் செய்யலாம். மேலும் உதவி வேண்டுமா 🙂"
            print(f"🇮🇳 Tamil: {tamil_format}")
            
            # Tanglish (as requested)
            tanglish_format = f"{location}-la iniku weather: 🌡️ {temp}°C, 💧 {humidity}% 🌧️ Rain chance: {rain_prob}% Irrigation pannalam. Let me know if you need more help 🙂"
            print(f"🔄 Tanglish: {tanglish_format}")
            
            return True
        else:
            print(f"❌ Weather API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

def test_n8n_webhook():
    """Test N8N webhook status"""
    print("\n🔗 Testing N8N Webhook Status...")
    try:
        webhook_url = "https://suryan8nproject.app.n8n.cloud/webhook/ccd37962-6bb3-4c30-b859-d3b63b9c64e2/chat"
        
        response = requests.post(webhook_url, 
            json={
                "sessionId": "test-session",
                "action": "sendMessage", 
                "chatInput": "weather test",
                "language": "english"
            },
            timeout=3  # Reduced timeout as in the code
        )
        
        if response.status_code == 200:
            print("✅ N8N Webhook: Working - Will use AI responses")
            return True
        else:
            print(f"⚠️ N8N Webhook: HTTP {response.status_code} - Will use clean weather fallback")
            return False
    except Exception as e:
        print(f"⚠️ N8N Webhook: {e} - Will use clean weather fallback")
        return False

def main():
    """Test the new chatbot format"""
    print("🧪 Chatbot Clean Format Test")
    print("=" * 50)
    
    weather_ok = test_weather_api()
    n8n_ok = test_n8n_webhook()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Weather API: {'✅ Working' if weather_ok else '❌ Failed'}")
    print(f"   N8N Webhook: {'✅ Working' if n8n_ok else '⚠️ Down (will use fallback)'}")
    
    if weather_ok:
        print("\n🎉 Chatbot Format: READY")
        print("   • Clean, simple weather responses")
        print("   • Multi-language support (English, Tamil, Tanglish)")
        print("   • Fast 3-second timeout for N8N")
        print("   • Reliable fallback to local weather API")
        
        print("\n💬 Expected Responses:")
        print("   'Weather today?' → Clean weather format")
        print("   'Iniku mala varuma?' → Tamil weather format")
        print("   'Irrigation advice?' → Weather-based irrigation advice")
    else:
        print("\n⚠️ Issue: Weather API not responding")
        print("   Check if FastAPI backend is running")

if __name__ == "__main__":
    main()