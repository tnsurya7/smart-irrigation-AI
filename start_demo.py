#!/usr/bin/env python3
"""
Demo Startup Script
Starts the USB Serial Reader for ESP32 demo
"""

import subprocess
import sys
import os
import time

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['serial', 'flask', 'flask_cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'serial':
                import serial
            elif package == 'flask':
                import flask
            elif package == 'flask_cors':
                import flask_cors
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            if package == 'serial':
                print("   pip install pyserial")
            else:
                print(f"   pip install {package}")
        print("\nInstalling missing packages...")
        
        # Install missing packages
        for package in missing_packages:
            if package == 'serial':
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyserial'])
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies are installed")

def main():
    print("🌱 Smart Agriculture Demo Startup")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    print("\n🚀 Starting ESP32 USB Serial Reader...")
    print("📡 Backend will run on http://localhost:5000")
    print("📊 Live data endpoint: http://localhost:5000/api/live-data")
    print("\n🔄 Next steps:")
    print("   1. Connect ESP32 via USB")
    print("   2. Start dashboard: npm run dev (on port 3000)")
    print("   3. Open http://localhost:3000")
    print("\n" + "=" * 50)
    
    try:
        # Start the USB serial reader
        subprocess.run([sys.executable, 'usb_serial_reader.py'])
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == '__main__':
    main()