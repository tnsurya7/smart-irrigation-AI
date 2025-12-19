#!/usr/bin/env python3
"""
Initialize arimax_real_sensor_data.csv with proper headers
"""
import pandas as pd
import os
from datetime import datetime

CSV_FILE = "arimax_real_sensor_data.csv"

def initialize_csv():
    """Create CSV file with proper headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        # Create empty CSV with headers
        headers = [
            "timestamp",
            "soil_moisture", 
            "temperature",
            "humidity",
            "rain_pct",
            "light_pct", 
            "flow",
            "pump_status",
            "mode",
            "rain_detected"
        ]
        
        df = pd.DataFrame(columns=headers)
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Created {CSV_FILE} with headers")
    else:
        # Check current row count
        df = pd.read_csv(CSV_FILE)
        print(f"📊 {CSV_FILE} exists with {len(df)} rows")

if __name__ == "__main__":
    initialize_csv()