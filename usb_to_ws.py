import serial
import asyncio
import websockets
import json
import csv
import os
from datetime import datetime

SERIAL_PORT = "/dev/cu.usbserial-140"  # Real Arduino USB port
BAUD_RATE = 115200
WS_URL = "ws://localhost:8080/ws"
CSV_FILE = "/Users/suryakumar/Desktop/smart-agriculture-dashboard/live_sensor_data.csv"

def log_to_csv(data):
    """Log sensor data to CSV file"""
    try:
        # Create CSV row with timestamp
        timestamp = datetime.now().isoformat() + 'Z'
        
        # Map Arduino data to CSV format
        csv_row = {
            'timestamp': timestamp,
            'soil_pct': data.get('soil', 0),
            'temperature': data.get('temperature', 0),
            'humidity': data.get('humidity', 0),
            'rain_raw': 800 if data.get('rain', 0) == 0 else 200,  # Convert boolean to raw
            'ldr_raw': data.get('light', 500),
            'flow_lmin': data.get('flow', 0.0),
            'total_l': data.get('total', 0.0),
            'pump': data.get('pump', 0),
            'mode': 'AUTO',
            'rain_forecast': '',
            'forecast_humidity': '',
            'forecast_temperature': ''
        }
        
        # Check if file exists, if not create with headers
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'soil_pct', 'temperature', 'humidity', 'rain_raw', 
                         'ldr_raw', 'flow_lmin', 'total_l', 'pump', 'mode', 
                         'rain_forecast', 'forecast_humidity', 'forecast_temperature']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(csv_row)
            print(f"📊 Logged to CSV: {csv_row['timestamp']}")
            
    except Exception as e:
        print(f"❌ CSV logging error: {e}")

async def usb_to_ws():
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print("✅ Arduino USB connected")
            
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=10) as ws:
                print("✅ WebSocket connected")
                
                while True:
                    line = ser.readline().decode(errors="ignore").strip()
                    if not line:
                        continue
                    
                    try:
                        # Arduino sends JSON: {"soil":65,"temperature":30.7,"humidity":49.8,"rain":0,"pump":0,"light":1138,"flow":1.2,"total":56.0}
                        data = json.loads(line)
                        
                        # Send to WebSocket
                        await ws.send(json.dumps(data))
                        print("📤 Sent real data:", data)
                        
                        # Log to CSV file
                        log_to_csv(data)
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parse Error: {e}")
                        print(f"❌ Raw line: '{line}'")
                    except websockets.exceptions.ConnectionClosed:
                        print("🔄 WebSocket connection closed, reconnecting...")
                        break
                    except Exception as e:
                        print(f"❌ Other error: {e}")
                        
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("🔄 Retrying in 3 seconds...")
            await asyncio.sleep(3)

asyncio.run(usb_to_ws())