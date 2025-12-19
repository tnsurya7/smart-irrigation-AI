#!/usr/bin/env python3
"""
USB Data Simulator for Smart Agriculture System
Simulates Arduino/ESP32 sensor data for testing without hardware
"""

import asyncio
import websockets
import json
import random
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WS_URL = "ws://localhost:8080/ws"

class SensorSimulator:
    def __init__(self):
        self.soil_moisture = 45.0
        self.temperature = 25.0
        self.humidity = 60.0
        self.rain_sensor = 800
        self.light_sensor = 1200
        self.flow_rate = 0.0
        self.pump_status = 0
        self.mode = "auto"
        
    def generate_realistic_data(self):
        """Generate realistic sensor data with natural variations"""
        
        # Soil moisture (20-80%) - slowly changing
        self.soil_moisture += random.uniform(-2, 2)
        self.soil_moisture = max(20, min(80, self.soil_moisture))
        
        # Temperature (18-35°C) - daily cycle simulation
        hour = datetime.now().hour
        base_temp = 22 + 8 * abs(12 - hour) / 12  # Peak at noon
        self.temperature = base_temp + random.uniform(-2, 2)
        
        # Humidity (30-90%) - inverse relationship with temperature
        base_humidity = 90 - (self.temperature - 18) * 2
        self.humidity = base_humidity + random.uniform(-10, 10)
        self.humidity = max(30, min(90, self.humidity))
        
        # Rain sensor (0-1023, lower = more rain)
        self.rain_sensor += random.uniform(-50, 50)
        self.rain_sensor = max(0, min(1023, self.rain_sensor))
        
        # Light sensor (0-2000, higher = more light)
        if 6 <= hour <= 18:  # Daytime
            self.light_sensor = random.uniform(800, 2000)
        else:  # Nighttime
            self.light_sensor = random.uniform(0, 200)
        
        # Flow rate (0-10 L/min) - only when pump is on
        if self.pump_status == 1:
            self.flow_rate = random.uniform(2, 8)
        else:
            self.flow_rate = 0
        
        # Pump logic (auto mode)
        if self.mode == "auto":
            if self.soil_moisture < 30:
                self.pump_status = 1
            elif self.soil_moisture > 70:
                self.pump_status = 0
            # Rain safety
            if self.rain_sensor < 300:  # Rain detected
                self.pump_status = 0
        
        return {
            "soil": round(self.soil_moisture, 1),
            "temp": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "rain": int(self.rain_sensor),
            "light": int(self.light_sensor),
            "flow": round(self.flow_rate, 1),
            "pump": self.pump_status,
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }

async def simulate_usb_data():
    """Simulate USB sensor data and send to WebSocket"""
    simulator = SensorSimulator()
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            logger.info(f"✅ Connected to WebSocket: {WS_URL}")
            
            while True:
                # Generate sensor data
                data = simulator.generate_realistic_data()
                
                # Convert to Arduino-like serial format
                serial_format = f"soil={data['soil']},temp={data['temp']},humidity={data['humidity']},rain={data['rain']},light={data['light']},flow={data['flow']},pump={data['pump']},mode={data['mode']}"
                
                logger.info(f"📤 Simulated USB: {serial_format}")
                
                # Send as JSON to WebSocket
                await websocket.send(json.dumps(data))
                
                # Wait before next reading (simulate 2-second intervals)
                await asyncio.sleep(2)
                
    except KeyboardInterrupt:
        logger.info("🛑 Simulation stopped by user")
    except Exception as e:
        logger.error(f"❌ Simulation error: {e}")

async def main():
    """Main function with retry logic"""
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            await simulate_usb_data()
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"❌ Connection failed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                logger.info(f"🔄 Retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                logger.error("❌ Max retries reached. Make sure WebSocket server is running.")

if __name__ == "__main__":
    print("🌱 Smart Agriculture USB Data Simulator")
    print("=" * 50)
    print(f"🎯 Target WebSocket: {WS_URL}")
    print("📊 Simulating realistic sensor data:")
    print("   • Soil Moisture: 20-80% (slow changes)")
    print("   • Temperature: 18-35°C (daily cycle)")
    print("   • Humidity: 30-90% (inverse to temp)")
    print("   • Rain Sensor: 0-1023 (random)")
    print("   • Light Sensor: 0-2000 (day/night cycle)")
    print("   • Flow Rate: 0-10 L/min (when pump on)")
    print("   • Pump: Auto logic based on soil & rain")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    asyncio.run(main())