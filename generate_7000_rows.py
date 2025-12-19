#!/usr/bin/env python3
"""
Generate 7000 rows of realistic sensor data for arimax_real_sensor_data.csv
Based on actual sensor patterns from live data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_realistic_sensor_data():
    """Generate 7000 rows of realistic sensor data"""
    
    # Start from 30 days ago to simulate historical data
    start_time = datetime.now() - timedelta(days=30)
    
    # Generate timestamps (every 6 minutes for 30 days = ~7200 readings)
    timestamps = []
    current_time = start_time
    
    for i in range(7000):
        timestamps.append(current_time.isoformat() + 'Z')
        # Add 6 minutes between readings (realistic ESP32 interval)
        current_time += timedelta(minutes=6)
    
    # Generate realistic sensor patterns
    data = []
    
    for i, timestamp in enumerate(timestamps):
        # Time-based patterns
        hour = (start_time + timedelta(minutes=6*i)).hour
        day_of_month = (start_time + timedelta(minutes=6*i)).day
        
        # Soil moisture patterns (0-100%)
        # Lower during day, higher at night, with irrigation cycles
        base_soil = 15 + 25 * np.sin(2 * np.pi * i / (24 * 10))  # Daily cycle
        soil_noise = random.uniform(-8, 8)
        
        # Irrigation events (pump on) increase soil moisture
        irrigation_chance = 0.05 if base_soil < 20 else 0.01
        pump_on = 1 if random.random() < irrigation_chance else 0
        
        if pump_on:
            base_soil += random.uniform(10, 25)  # Irrigation boost
        
        soil_moisture = max(0, min(100, base_soil + soil_noise))
        
        # Temperature patterns (20-35°C)
        # Higher during day, lower at night, seasonal variation
        base_temp = 27 + 6 * np.sin(2 * np.pi * (hour - 6) / 24)  # Daily cycle
        seasonal_temp = 2 * np.sin(2 * np.pi * day_of_month / 30)  # Monthly variation
        temp_noise = random.uniform(-2, 2)
        temperature = max(20, min(35, base_temp + seasonal_temp + temp_noise))
        
        # Humidity patterns (30-90%)
        # Inverse relationship with temperature, higher at night
        base_humidity = 70 - 20 * np.sin(2 * np.pi * (hour - 6) / 24)
        humidity_noise = random.uniform(-10, 10)
        humidity = max(30, min(90, base_humidity + humidity_noise))
        
        # Rain patterns (0-100%)
        # Random rain events, more likely during certain hours
        rain_chance = 0.15 if 14 <= hour <= 18 else 0.05  # Afternoon rain
        is_raining = random.random() < rain_chance
        
        if is_raining:
            rain_pct = random.uniform(60, 100)  # Heavy rain
            humidity += random.uniform(10, 20)  # Rain increases humidity
            humidity = min(90, humidity)
        else:
            rain_pct = random.uniform(0, 25)  # Dry sensor
        
        # Light patterns (0-100%)
        # High during day, low at night
        if 6 <= hour <= 18:  # Daytime
            light_pct = random.uniform(60, 100)
        elif 19 <= hour <= 21 or 5 <= hour <= 6:  # Twilight
            light_pct = random.uniform(20, 60)
        else:  # Night
            light_pct = random.uniform(0, 25)
        
        # Flow rate (0-5 L/min)
        # Only when pump is on
        flow = random.uniform(1.5, 4.5) if pump_on else 0.0
        
        # Mode (mostly auto)
        mode = "manual" if random.random() < 0.05 else "auto"
        
        # Rain detected (boolean)
        rain_detected = rain_pct > 50
        
        data.append({
            'timestamp': timestamp,
            'soil_moisture': round(soil_moisture, 1),
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'rain_pct': round(rain_pct, 1),
            'light_pct': round(light_pct, 1),
            'flow': round(flow, 2),
            'pump_status': pump_on,
            'mode': mode,
            'rain_detected': rain_detected
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('arimax_real_sensor_data.csv', index=False)
    
    # Print statistics
    print(f"✅ Generated {len(df)} rows of sensor data")
    print(f"📊 Data Statistics:")
    print(f"   Soil Moisture: {df['soil_moisture'].min():.1f}% - {df['soil_moisture'].max():.1f}%")
    print(f"   Temperature: {df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C")
    print(f"   Humidity: {df['humidity'].min():.1f}% - {df['humidity'].max():.1f}%")
    print(f"   Rain Events: {df['rain_detected'].sum()} detected")
    print(f"   Irrigation Events: {df['pump_status'].sum()} pump activations")
    print(f"   Time Range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    
    return df

if __name__ == "__main__":
    generate_realistic_sensor_data()