#!/usr/bin/env python3
"""
Smart Agriculture Telegram System Startup Script
Starts all required services for the complete system
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def check_backend_running():
    """Check if FastAPI backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "fastapi_arimax_autoretrain.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for backend to start
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_running():
            print("✅ FastAPI backend is running on http://localhost:8000")
            return backend_process
        time.sleep(1)
        print(f"⏳ Waiting for backend... ({i+1}/30)")
    
    print("❌ Failed to start backend")
    return None

def start_interactive_bot():
    """Start interactive Telegram bot"""
    print("🤖 Starting Interactive Telegram Bot...")
    bot_process = subprocess.Popen([
        sys.executable, "telegram_bot_interactive.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(3)  # Give bot time to start
    print("✅ Interactive Telegram Bot started")
    return bot_process

def main():
    """Main startup function"""
    print("🌱 Smart Agriculture Telegram System Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("fastapi_arimax_autoretrain.py").exists():
        print("❌ Error: Run this script from the project root directory")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start backend if not running
        if not check_backend_running():
            backend_process = start_backend()
            if backend_process:
                processes.append(("FastAPI Backend", backend_process))
            else:
                print("❌ Cannot start system without backend")
                sys.exit(1)
        else:
            print("✅ FastAPI backend already running")
        
        # Start interactive bot
        bot_process = start_interactive_bot()
        if bot_process:
            processes.append(("Interactive Bot", bot_process))
        
        print("\n🎉 Smart Agriculture Telegram System is running!")
        print("\n📱 Available Services:")
        print("   • FastAPI Backend: http://localhost:8000")
        print("   • Interactive Telegram Bot: @Arimax_Alert_Bot")
        print("   • Automatic Alerts: Active")
        print("   • Daily Reports: Scheduled")
        
        print("\n💬 Try these Telegram commands:")
        print("   • weather report")
        print("   • dashboard summary") 
        print("   • irrigation update")
        print("   • help")
        
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} stopped unexpectedly")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping Smart Agriculture System...")
        
        # Terminate all processes
        for name, process in processes:
            print(f"⏹️ Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()