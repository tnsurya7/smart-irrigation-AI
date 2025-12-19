#!/usr/bin/env python3
"""
Smart Agriculture System Status Checker
Checks the status of all system components
"""

import requests
import json
from datetime import datetime

def check_backend():
    """Check FastAPI backend status"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Backend: {data['status']}, Model: {'loaded' if data['model_loaded'] else 'not loaded'}"
        else:
            return False, f"❌ Backend: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Backend: {str(e)}"

def check_weather_api():
    """Check weather API"""
    try:
        response = requests.get("http://localhost:8000/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Weather: {data['temperature']}°C, {data['location']}"
        else:
            return False, f"❌ Weather: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Weather: {str(e)}"

def check_model_status():
    """Check AI model status"""
    try:
        response = requests.get("http://localhost:8000/model-report", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Models: ARIMA {data['arima_accuracy']}%, ARIMAX {data['arimax_accuracy']}%"
        else:
            return False, f"❌ Models: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Models: {str(e)}"

def check_telegram():
    """Check Telegram integration"""
    try:
        response = requests.post("http://localhost:8000/telegram/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Telegram: {data['status']}"
        else:
            return False, f"❌ Telegram: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Telegram: {str(e)}"

def check_dashboard_data():
    """Check dashboard data availability"""
    try:
        response = requests.get("http://localhost:8000/daily-summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Dashboard: {data['averages']['avg_soil_moisture']}% soil, {data['irrigation']['pump_on_count']} cycles"
        else:
            return False, f"❌ Dashboard: HTTP {response.status_code}"
    except Exception as e:
        return False, f"❌ Dashboard: {str(e)}"

def main():
    """Run system status check"""
    print("🔍 Smart Agriculture System Status Check")
    print("=" * 60)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Backend API", check_backend),
        ("Weather Service", check_weather_api),
        ("AI Models", check_model_status),
        ("Telegram Bot", check_telegram),
        ("Dashboard Data", check_dashboard_data)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            success, message = check_func()
            print(f"{message}")
            if success:
                passed += 1
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 System Health: {passed}/{total} services operational")
    
    if passed == total:
        print("🎉 All systems operational! Smart agriculture is ready!")
        print("\n💬 Try these Telegram commands:")
        print("   • Send 'weather report' to @Arimax_Alert_Bot")
        print("   • Send 'dashboard summary' to @Arimax_Alert_Bot")
        print("   • Send 'irrigation update' to @Arimax_Alert_Bot")
    else:
        print("⚠️ Some services need attention. Check the errors above.")
        
        if passed == 0:
            print("\n🚀 To start the system, run:")
            print("   python start_telegram_system.py")

if __name__ == "__main__":
    main()