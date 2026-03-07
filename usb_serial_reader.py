#!/usr/bin/env python3
"""
ESP32 USB Serial Reader for Demo
Reads JSON data from ESP32 via USB and serves it via REST API
Matches existing dashboard data structure exactly
"""

import serial
import serial.tools.list_ports
import json
import time
import threading
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESP32SerialReader:
    def __init__(self):
        self.serial_port = None
        # DEMO: Force correct ESP32 port (no auto-scan for stability)
        self.esp32_port = "/dev/cu.usbserial-0001"  # Silicon Labs ESP32
        self.last_data = {
            # Match existing dashboard data structure exactly
            "soil": 0,
            "temperature": 0.0,
            "humidity": 0,
            "rainRaw": 4095,
            "rainDetected": False,
            "ldr": 0,
            "lightPercent": 0,
            "lightStatus": "Normal Light",
            "flow": 0,
            "totalLiters": 0,
            "pump": 0,
            "mode": "auto",
            "rainExpected": False,
            "device_status": "offline",
            "timestamp": datetime.now().isoformat()
        }
        self.running = False
        self.read_thread = None
        
    def find_esp32_port(self):
        """Auto-detect ESP32 USB port"""
        logger.info("🔍 Scanning for ESP32 USB ports...")
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            logger.info(f"   Found: {port.device} - {port.manufacturer or 'Unknown'}")
            
            # Look for common ESP32 identifiers
            if port.manufacturer and any(keyword in port.manufacturer.lower() for keyword in 
                ['silicon labs', 'espressif', 'cp210', 'ch340', 'ftdi']):
                logger.info(f"✅ ESP32 port detected: {port.device}")
                return port.device
                
            # Also check device names
            if any(keyword in port.device.lower() for keyword in 
                ['ttyusb', 'ttyacm', 'cu.usbserial', 'com']):
                logger.info(f"✅ Potential ESP32 port: {port.device}")
                return port.device
        
        # If no specific match, use first available port
        if ports:
            logger.warning(f"⚠️ No ESP32 detected, using first port: {ports[0].device}")
            return ports[0].device
            
        logger.error("❌ No serial ports found")
        return None
    
    def get_light_status(self, light_raw):
        """Convert light raw value to status (matching existing logic)"""
        if light_raw < 300:
            return "Bright Sunlight"
        elif light_raw > 800:
            return "Dark / Night"
        else:
            return "Normal Light"
    
    def connect(self):
        """Connect to ESP32 via USB"""
        try:
            logger.info(f"📡 Connecting to ESP32 on {self.esp32_port} at 115200 baud...")
            
            self.serial_port = serial.Serial(
                port=self.esp32_port,
                baudrate=115200,
                timeout=1,
                write_timeout=1
            )
            
            # Wait for connection to stabilize and flush buffers
            time.sleep(2)
            self.serial_port.flushInput()  # Clear input buffer
            self.serial_port.flushOutput()  # Clear output buffer
            
            logger.info("✅ ESP32 USB connection established")
            self.last_data["device_status"] = "online"
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ESP32: {e}")
            self.last_data["device_status"] = "offline"
            return False
    
    def read_data(self):
        """Read JSON data from ESP32 serial port"""
        while self.running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    logger.warning("📡 Serial port not available, attempting reconnection...")
                    if not self.connect():
                        time.sleep(5)
                        continue
                
                # Read line from serial
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    
                    if not line:
                        continue
                        
                    # Skip non-JSON lines (debug messages)
                    if not line.startswith('{'):
                        logger.debug(f"📝 ESP32 Debug: {line}")
                        continue
                    
                    # Parse JSON
                    try:
                        esp32_data = json.loads(line)
                        
                        # Validate ESP32 data structure
                        if esp32_data.get('source') != 'esp32':
                            continue
                            
                        # Convert ESP32 data to dashboard format (EXACT MATCH)
                        light_raw = esp32_data.get('light_raw', 0)
                        
                        self.last_data.update({
                            # Match useSmartFarmData structure exactly
                            "soil": esp32_data.get('soil', 0),
                            "temperature": float(esp32_data.get('temperature', 0)),
                            "humidity": esp32_data.get('humidity', 0),
                            "rainRaw": esp32_data.get('rain_raw', 4095),
                            "rainDetected": esp32_data.get('rain_detected', False),
                            "ldr": light_raw,
                            "lightPercent": esp32_data.get('light_percent', 0),
                            "lightStatus": self.get_light_status(light_raw),
                            "flow": esp32_data.get('flow', 0),
                            "totalLiters": esp32_data.get('total', 0),
                            "pump": esp32_data.get('pump', 0),
                            "mode": esp32_data.get('mode', 'auto'),
                            "rainExpected": esp32_data.get('rain_expected', False),
                            "device_status": "online",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        logger.info(f"📊 ESP32 Data: Temp {self.last_data['temperature']}°C, "
                                  f"Humidity {self.last_data['humidity']}%, "
                                  f"Soil {self.last_data['soil']}%, "
                                  f"Pump {'ON' if self.last_data['pump'] else 'OFF'}")
                        
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Invalid JSON from ESP32: {line}")
                        continue
                        
                else:
                    time.sleep(0.1)  # Small delay to prevent CPU spinning
                    
            except serial.SerialException as e:
                logger.error(f"❌ Serial error: {e}")
                self.last_data["device_status"] = "offline"
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                time.sleep(1)
    
    def start(self):
        """Start reading data in background thread"""
        if self.running:
            return
            
        logger.info("🚀 Starting ESP32 Serial Reader...")
        self.running = True
        
        # Try initial connection
        self.connect()
        
        # Start reading thread
        self.read_thread = threading.Thread(target=self.read_data, daemon=True)
        self.read_thread.start()
        
        logger.info("✅ ESP32 Serial Reader started")
    
    def stop(self):
        """Stop reading data"""
        logger.info("🛑 Stopping ESP32 Serial Reader...")
        self.running = False
        
        if self.read_thread:
            self.read_thread.join(timeout=2)
            
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            
        logger.info("👋 ESP32 Serial Reader stopped")
    
    def send_command(self, command):
        """Send command to ESP32 via USB"""
        try:
            if self.serial_port and self.serial_port.is_open:
                command_str = f"{command}\n"
                self.serial_port.write(command_str.encode('utf-8'))
                logger.info(f"📤 USB Command sent: {command}")
                return True
            else:
                logger.warning("📤 Cannot send command - ESP32 not connected")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to send command: {e}")
            return False

    def get_live_data(self):
        """Get latest ESP32 data in dashboard format"""
        return self.last_data.copy()

# Flask API
app = Flask(__name__)
CORS(app)  # Enable CORS for localhost:3000

# Global serial reader instance
esp32_reader = ESP32SerialReader()

@app.route('/api/live-data')
def get_live_data():
    """REST API endpoint for live ESP32 data - matches dashboard structure"""
    return jsonify(esp32_reader.get_live_data())

@app.route('/api/status')
def get_status():
    """API status endpoint"""
    return jsonify({
        "api_status": "online",
        "esp32_status": esp32_reader.last_data["device_status"],
        "last_update": esp32_reader.last_data["timestamp"],
        "uptime": time.time()
    })

# USB Command Endpoints
@app.route('/api/pump/on', methods=['POST'])
def pump_on():
    """Turn pump ON via USB command"""
    success = esp32_reader.send_command("PUMP_ON")
    return jsonify({
        "status": "success" if success else "failed",
        "message": "Pump ON command sent" if success else "Failed to send command",
        "command": "PUMP_ON"
    })

@app.route('/api/pump/off', methods=['POST'])
def pump_off():
    """Turn pump OFF via USB command"""
    success = esp32_reader.send_command("PUMP_OFF")
    return jsonify({
        "status": "success" if success else "failed",
        "message": "Pump OFF command sent" if success else "Failed to send command",
        "command": "PUMP_OFF"
    })

@app.route('/api/pump/auto', methods=['POST'])
def pump_auto():
    """Enable AUTO mode via USB command"""
    success = esp32_reader.send_command("AUTO")
    return jsonify({
        "status": "success" if success else "failed",
        "message": "Auto mode enabled" if success else "Failed to send command",
        "command": "AUTO"
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "ESP32 USB Serial Reader",
        "status": "running",
        "endpoints": ["/api/live-data", "/api/status"],
        "note": "For demo: ESP32 → USB → Backend → Dashboard (localhost:3000)"
    })

if __name__ == '__main__':
    try:
        # Start ESP32 reader
        esp32_reader.start()
        
        # Start Flask API
        logger.info("🌐 Starting Flask API on http://localhost:5002")
        logger.info("📊 Live data endpoint: http://localhost:5002/api/live-data")
        logger.info("🔄 Dashboard should poll this endpoint every 2 seconds")
        logger.info("🎯 For demo: ESP32 → USB → Backend → Dashboard (localhost:3000)")
        
        app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    finally:
        esp32_reader.stop()