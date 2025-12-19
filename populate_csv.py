#!/usr/bin/env python3
"""
Populate arimax_real_sensor_data.csv with real sensor data from live_sensor_data.csv
"""
import pandas as pd
import os
from datetime import datetime

def populate_arimax_csv():
    """Convert live sensor data to ARIMAX format"""
    
    # Read the live sensor data
    if not os.path.exists('live_sensor_data.csv'):
        print("❌ live_sensor_data.csv not found")
        return
    
    try:
        # Read live data
        df_live = pd.read_csv('live_sensor_data.csv')
        print(f"📊 Found {len(df_live)} rows in live_sensor_data.csv")
        
        # Take every 10th row to get a good sample (about 500 rows)
        df_sample = df_live.iloc[::10].copy()
        
        # Convert to ARIMAX format
        df_arimax = pd.DataFrame()
        df_arimax['timestamp'] = df_sample['timestamp']
        df_arimax['soil_moisture'] = df_sample['soil_pct']
        df_arimax['temperature'] = df_sample['temperature']
        df_arimax['humidity'] = df_sample['humidity']
        
        # Convert rain_raw to percentage (0-4095 -> 0-100%)
        df_arimax['rain_pct'] = (df_sample['rain_raw'] / 4095.0) * 100
        
        # Convert ldr_raw to percentage (0-1023 -> 0-100%)
        df_arimax['light_pct'] = (df_sample['ldr_raw'] / 1023.0) * 100
        
        df_arimax['flow'] = df_sample['flow_lmin']
        df_arimax['pump_status'] = df_sample['pump']
        df_arimax['mode'] = df_sample['mode'].str.lower()
        
        # Rain detected if rain_raw < 500 (wet sensor)
        df_arimax['rain_detected'] = df_sample['rain_raw'] < 500
        
        # Save to arimax_real_sensor_data.csv
        df_arimax.to_csv('arimax_real_sensor_data.csv', index=False)
        
        print(f"✅ Successfully populated arimax_real_sensor_data.csv with {len(df_arimax)} rows")
        print(f"📈 Data range:")
        print(f"   Soil Moisture: {df_arimax['soil_moisture'].min():.1f}% - {df_arimax['soil_moisture'].max():.1f}%")
        print(f"   Temperature: {df_arimax['temperature'].min():.1f}°C - {df_arimax['temperature'].max():.1f}°C")
        print(f"   Humidity: {df_arimax['humidity'].min():.1f}% - {df_arimax['humidity'].max():.1f}%")
        print(f"   Rain Events: {df_arimax['rain_detected'].sum()} detected")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")

if __name__ == "__main__":
    populate_arimax_csv()