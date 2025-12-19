#!/usr/bin/env python3
"""
Create 7000 rows of realistic sensor data efficiently
"""
import csv
from datetime import datetime, timedelta
import math
import random

def create_7000_rows():
    """Create 7000 rows of realistic sensor data"""
    
    # Start from 30 days ago
    start_time = datetime.now() - timedelta(days=30)
    
    # Open CSV file for writing
    with open('arimax_real_sensor_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'soil_moisture', 'temperature', 'humidity', 
                     'rain_pct', 'light_pct', 'flow', 'pump_status', 'mode', 'rain_detected']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Generate 7000 rows
        for i in range(7000):
            # Calculate current time (6-minute intervals)
            current_time = start_time + timedelta(minutes=6*i)
            hour = current_time.hour
            day = current_time.day
            
            # Soil moisture (0-80%) - realistic agricultural range
            base_soil = 25 + 20 * math.sin(2 * math.pi * i / (24 * 10))  # Daily cycle
            soil_noise = random.uniform(-5, 5)
            
            # Irrigation events
            irrigation_chance = 0.08 if base_soil < 20 else 0.02
            pump_on = 1 if random.random() < irrigation_chance else 0
            
            if pump_on:
                base_soil += random.uniform(15, 30)  # Irrigation boost
            
            soil_moisture = max(0, min(80, base_soil + soil_noise))
            
            # Temperature (18-38°C) - realistic range
            base_temp = 28 + 8 * math.sin(2 * math.pi * (hour - 6) / 24)
            seasonal = 3 * math.sin(2 * math.pi * day / 30)
            temp_noise = random.uniform(-1.5, 1.5)
            temperature = max(18, min(38, base_temp + seasonal + temp_noise))
            
            # Humidity (25-95%) - inverse to temperature
            base_humidity = 75 - 25 * math.sin(2 * math.pi * (hour - 6) / 24)
            humidity_noise = random.uniform(-8, 8)
            humidity = max(25, min(95, base_humidity + humidity_noise))
            
            # Rain patterns
            rain_chance = 0.12 if 13 <= hour <= 17 else 0.03
            is_raining = random.random() < rain_chance
            
            if is_raining:
                rain_pct = random.uniform(55, 95)
                humidity = min(95, humidity + random.uniform(5, 15))
            else:
                rain_pct = random.uniform(0, 30)
            
            # Light patterns (0-100%)
            if 6 <= hour <= 18:  # Day
                light_pct = random.uniform(70, 100)
            elif 5 <= hour < 6 or 18 < hour <= 20:  # Twilight
                light_pct = random.uniform(25, 70)
            else:  # Night
                light_pct = random.uniform(0, 30)
            
            # Flow rate
            flow = random.uniform(2.0, 5.0) if pump_on else 0.0
            
            # Mode
            mode = "manual" if random.random() < 0.03 else "auto"
            
            # Write row
            writer.writerow({
                'timestamp': current_time.isoformat() + 'Z',
                'soil_moisture': round(soil_moisture, 1),
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'rain_pct': round(rain_pct, 1),
                'light_pct': round(light_pct, 1),
                'flow': round(flow, 2),
                'pump_status': pump_on,
                'mode': mode,
                'rain_detected': is_raining
            })
    
    print(f"✅ Created arimax_real_sensor_data.csv with 7000 rows")
    print(f"📅 Time range: 30 days of data (6-minute intervals)")
    print(f"🌱 Realistic agricultural sensor patterns included")

if __name__ == "__main__":
    create_7000_rows()