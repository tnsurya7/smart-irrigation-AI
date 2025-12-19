#!/usr/bin/env python3
"""
USB Port Detection Utility for Smart Agriculture System
Helps find the correct USB serial port for your Arduino/ESP32
"""

import serial.tools.list_ports
import serial
import time

def list_all_ports():
    """List all available serial ports"""
    print("🔍 Scanning for USB Serial Ports...")
    print("=" * 50)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found")
        return []
    
    usb_ports = []
    
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Manufacturer: {port.manufacturer or 'Unknown'}")
        print(f"   VID:PID: {port.vid:04X}:{port.pid:04X}" if port.vid and port.pid else "   VID:PID: Unknown")
        
        # Check if it's likely a USB device
        if any(keyword in port.device.lower() for keyword in ['usbmodem', 'ttyusb', 'ttyacm', 'com']):
            usb_ports.append(port.device)
            print(f"   ✅ Likely USB device")
        
        print()
    
    return usb_ports

def test_port(port_name, baud_rate=115200):
    """Test if a port can be opened and read data"""
    print(f"🧪 Testing port: {port_name}")
    
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=2)
        print(f"✅ Port opened successfully")
        
        print("📡 Listening for data (10 seconds)...")
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"📥 Received: {line}")
                    data_received = True
            time.sleep(0.1)
        
        ser.close()
        
        if data_received:
            print(f"✅ Port {port_name} is receiving data!")
            return True
        else:
            print(f"⚠️ Port {port_name} opened but no data received")
            return False
            
    except Exception as e:
        print(f"❌ Error testing port {port_name}: {e}")
        return False

def main():
    """Main function"""
    print("🌱 Smart Agriculture USB Port Detector")
    print("=" * 50)
    
    # List all ports
    usb_ports = list_all_ports()
    
    if not usb_ports:
        print("❌ No USB serial devices found")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure your Arduino/ESP32 is connected via USB")
        print("   2. Check if drivers are installed")
        print("   3. Try a different USB cable")
        print("   4. Check Device Manager (Windows) or System Report (Mac)")
        return
    
    print(f"🎯 Found {len(usb_ports)} potential USB device(s)")
    print("=" * 50)
    
    # Test each USB port
    working_ports = []
    
    for port in usb_ports:
        if test_port(port):
            working_ports.append(port)
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if working_ports:
        print(f"✅ Working ports with data: {len(working_ports)}")
        for port in working_ports:
            print(f"   • {port}")
        
        print(f"\n🔧 Update your usb_to_ws.py file:")
        print(f'   SERIAL_PORT = "{working_ports[0]}"')
        
    else:
        print("⚠️ No ports are receiving data")
        print("\n💡 Possible issues:")
        print("   1. Arduino/ESP32 not sending data")
        print("   2. Wrong baud rate (try 9600, 57600, or 115200)")
        print("   3. Device not programmed yet")
        print("   4. USB cable is power-only (no data)")
    
    if usb_ports:
        print(f"\n📋 All detected USB ports:")
        for port in usb_ports:
            print(f"   • {port}")

if __name__ == "__main__":
    main()