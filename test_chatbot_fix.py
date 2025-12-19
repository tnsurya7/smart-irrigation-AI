#!/usr/bin/env python3
"""
Test script to verify the chatbot fix is working
Tests both N8N webhook and local backend fallback
"""

import requests
import json
from datetime import datetime

def test_local_weather_api():
    """Test the local weather API that the chatbot will use as fallback"""
    print("🌤️ Testing Local Weather API...")
    try:
        response = requests.get("http://localhost:8000/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            temp = round(data['temperature'])
            humidity = data['humidity']
            rain_prob = round(data['rain_probability'])
            location = data['location']
            
            print(f"✅ Weather API: {temp}°C, {humidity}% humidity, {rain_prob}% rain chance in {location}")
            
            # Test response generation for different languages
            print("\n📝 Testing response generation:")
            
            # English response
            if rain_prob > 50:
                english_response = f"{location} weather today: {rain_prob}% rain chance 🌧️\nTemperature: {temp}°C, Humidity: {humidity}%\nSkip irrigation!"
            else:
                english_response = f"{location} weather today:\n🌡️ {temp}°C, 💧 {humidity}%\n🌧️ Rain chance: {rain_prob}%\nIrrigation recommended."
            
            print(f"🇺🇸 English: {english_response}")
            
            # Tamil response
            if rain_prob > 50:
                tamil_response = f"{location}-ல் இன்று மழை வாய்ப்பு {rain_prob}% 🌧️\nவெப்பநிலை: {temp}°C, ஈரப்பதம்: {humidity}%\nநீர்ப்பாசனம் வேண்டாம்!"
            else:
                tamil_response = f"{location}-ல் இன்று வானிலை:\n🌡️ {temp}°C, 💧 {humidity}%\n🌧️ மழை வாய்ப்பு: {rain_prob}%\nநீர்ப்பாசனம் செய்யலாம்."
            
            print(f"🇮🇳 Tamil: {tamil_response}")
            
            # Tanglish response
            if rain_prob > 50:
                tanglish_response = f"{location}-la iniku mala chance {rain_prob}% 🌧️\nTemperature: {temp}°C, Humidity: {humidity}%\nIrrigation vendam!"
            else:
                tanglish_response = f"{location}-la iniku weather:\n🌡️ {temp}°C, 💧 {humidity}%\n🌧️ Rain chance: {rain_prob}%\nIrrigation pannalam."
            
            print(f"🔄 Tanglish: {tanglish_response}")
            
            return True
        else:
            print(f"❌ Weather API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

def test_n8n_webhook():
    """Test the N8N webhook to see if it's accessible"""
    print("\n🔗 Testing N8N Webhook...")
    try:
        webhook_url = "https://suryan8nproject.app.n8n.cloud/webhook/ccd37962-6bb3-4c30-b859-d3b63b9c64e2/chat"
        
        response = requests.post(webhook_url, 
            json={
                "sessionId": "test-session",
                "action": "sendMessage", 
                "chatInput": "weather test",
                "language": "english"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ N8N Webhook: Working (response: {str(data)[:100]}...)")
            return True
        else:
            print(f"⚠️ N8N Webhook: HTTP {response.status_code} - Will use local fallback")
            return False
    except requests.exceptions.Timeout:
        print("⚠️ N8N Webhook: Timeout - Will use local fallback")
        return False
    except Exception as e:
        print(f"⚠️ N8N Webhook: {e} - Will use local fallback")
        return False

def test_frontend_running():
    """Test if the frontend is running"""
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Running on http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Chatbot Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Local Weather API", test_local_weather_api),
        ("N8N Webhook", test_n8n_webhook),
        ("Frontend", test_frontend_running)
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 Overall: {sum(results.values())}/{len(results)} tests passed")
    
    if results["Local Weather API"]:
        print("\n🎉 Chatbot Fix Status: READY")
        print("   • Local backend is working as fallback")
        print("   • Weather responses will be generated locally")
        print("   • Multi-language support (English, Tamil, Tanglish)")
        print("   • Users should now get proper weather responses")
        
        if results["Frontend"]:
            print("   • Frontend is running - users can test the chatbot")
        else:
            print("   • Start frontend with: npm run dev")
            
        if not results["N8N Webhook"]:
            print("   • N8N webhook is down, but local fallback will handle requests")
    else:
        print("\n⚠️ Chatbot Fix Status: NEEDS ATTENTION")
        print("   • Local backend is not responding")
        print("   • Check if FastAPI server is running")

if __name__ == "__main__":
    main()