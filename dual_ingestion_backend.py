#!/usr/bin/env python3
"""
Smart Agriculture Dual Data Ingestion Backend
Supports both WiFi (ESP32 WebSocket) and USB (Arduino UNO Serial) with automatic fallback
"""

import asyncio
import websockets
import serial
import json
import csv
import os
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
WEBSOCKET_PORT = 8080
USB_PORT = "/dev/cu.usbserial-140"  # Update as needed
USB_BAUD_RATE = 115200
WIFI_TIMEOUT = 3  # seconds
CSV_WIFI = "wifi_live_sensor.csv"
CSV_USB = "usb_live_sensor.csv"

class DualDataIngestion:
    def __init__(self):
        self.active_source = "WIFI"  # Default to WiFi
        self.status = "PRIMARY"
        self.last_wifi_data = 0
        self.wifi_clients = set()
        self.dashboard_clients = set()
        self.latest_data = None
        self.usb_serial = None
        self.usb_thread = None
        self.usb_running = False
        
        # Initialize CSV files
        self.init_csv_files()
        
    def init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        headers = ['timestamp', 'soil', 'temperature', 'humidity', 'rain', 'pump', 'light', 'flow', 'total', 'source']
        
        for csv_file in [CSV_WIFI, CSV_USB]:
            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                logger.info(f"Created CSV file: {csv_file}")
    
    def log_data_to_csv(self, data, source):
        """Log sensor data to appropriate CSV file"""
        try:
            timestamp = datetime.now().isoformat()
            csv_file = CSV_WIFI if source == "WIFI" else CSV_USB
            
            row = [
                timestamp,
                data.get('soil', 0),
                data.get('temperature', 0),
                data.get('humidity', 0),
                data.get('rain', 0),
                data.get('pump', 0),
                data.get('light', 0),
                data.get('flow', 0),
                data.get('total', 0),
                source
            ]
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
                
            logger.info(f"📊 Logged to {csv_file}: {source} data")
            
        except Exception as e:
            logger.error(f"CSV logging error: {e}")
    
    def switch_source(self, new_source, reason=""):
        """Switch data source and log the change"""
        if self.active_source != new_source:
            old_source = self.active_source
            self.active_source = new_source
            self.status = "PRIMARY" if new_source == "WIFI" else "FALLBACK"
            
            logger.warning(f"🔄 SOURCE SWITCH: {old_source} → {new_source} ({reason})")
            print(f"🔄 SOURCE SWITCH: {old_source} → {new_source} ({reason})")
    
    def process_sensor_data(self, data, source):
        """Process and distribute sensor data"""
        try:
            # Validate data format
            required_fields = ['soil', 'temperature', 'humidity', 'rain', 'pump', 'light']
            if not all(field in data for field in required_fields):
                logger.warning(f"Invalid data format from {source}: {data}")
                return
            
            # Update source timing
            if source == "WIFI":
                self.last_wifi_data = time.time()
                self.switch_source("WIFI", "WiFi data received")
            
            # Store latest data
            self.latest_data = {**data, 'source': source, 'timestamp': time.time()}
            
            # Log to CSV
            self.log_data_to_csv(data, source)
            
            # Broadcast to dashboard clients
            asyncio.create_task(self.broadcast_to_dashboard(data))
            
            logger.info(f"📡 {source} Data: Soil={data.get('soil')}%, Temp={data.get('temperature')}°C, Pump={'ON' if data.get('pump') else 'OFF'}")
            
        except Exception as e:
            logger.error(f"Error processing {source} data: {e}")
    
    async def broadcast_to_dashboard(self, data):
        """Broadcast data to all connected dashboard clients"""
        if self.dashboard_clients:
            message = json.dumps(data)
            disconnected = set()
            
            for client in self.dashboard_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.dashboard_clients -= disconnected
    
    def start_usb_monitoring(self):
        """Start USB serial monitoring in background thread"""
        def usb_monitor():
            while self.usb_running:
                try:
                    if not self.usb_serial:
                        self.usb_serial = serial.Serial(USB_PORT, USB_BAUD_RATE, timeout=1)
                        logger.info(f"✅ USB Serial connected: {USB_PORT}")
                    
                    line = self.usb_serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            data = json.loads(line)
                            
                            # Check if we should use USB data (WiFi timeout)
                            if time.time() - self.last_wifi_data > WIFI_TIMEOUT:
                                self.switch_source("USB", f"WiFi timeout ({WIFI_TIMEOUT}s)")
                                self.process_sensor_data(data, "USB")
                            
                        except json.JSONDecodeError:
                            pass  # Ignore invalid JSON
                            
                except serial.SerialException as e:
                    if self.usb_serial:
                        self.usb_serial.close()
                        self.usb_serial = None
                    time.sleep(2)  # Wait before retry
                except Exception as e:
                    logger.error(f"USB monitoring error: {e}")
                    time.sleep(1)
        
        self.usb_running = True
        self.usb_thread = threading.Thread(target=usb_monitor, daemon=True)
        self.usb_thread.start()
        logger.info("🔌 USB monitoring started")
    
    def stop_usb_monitoring(self):
        """Stop USB monitoring"""
        self.usb_running = False
        if self.usb_serial:
            self.usb_serial.close()
        logger.info("🔌 USB monitoring stopped")
    
    def get_source_status(self):
        """Get current source status"""
        wifi_age = time.time() - self.last_wifi_data if self.last_wifi_data else float('inf')
        
        return {
            "active_source": self.active_source,
            "status": self.status,
            "wifi_last_seen": wifi_age,
            "wifi_connected": wifi_age < WIFI_TIMEOUT,
            "usb_connected": self.usb_serial is not None,
            "latest_data_age": time.time() - self.latest_data['timestamp'] if self.latest_data else None
        }

# Global instance
data_ingestion = DualDataIngestion()

# FastAPI app
app = FastAPI(title="Smart Agriculture Dual Ingestion Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/source-status")
async def get_source_status():
    """Get current data source status"""
    return data_ingestion.get_source_status()

@app.get("/api/latest-data")
async def get_latest_data():
    """Get latest sensor data"""
    if data_ingestion.latest_data:
        return data_ingestion.latest_data
    return {"error": "No data available"}

# WebSocket endpoints
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for dashboard connections"""
    await websocket.accept()
    data_ingestion.dashboard_clients.add(websocket)
    logger.info(f"📱 Dashboard connected. Total clients: {len(data_ingestion.dashboard_clients)}")
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                
                # Check if this is sensor data from ESP32
                if all(field in data for field in ['soil', 'temperature', 'humidity']):
                    data_ingestion.process_sensor_data(data, "WIFI")
                    
            except json.JSONDecodeError:
                pass
                
    except Exception as e:
        logger.info(f"📱 Dashboard disconnected: {e}")
    finally:
        data_ingestion.dashboard_clients.discard(websocket)

@app.websocket("/wifi")
async def wifi_endpoint(websocket: WebSocket):
    """WebSocket endpoint specifically for ESP32 WiFi connections"""
    await websocket.accept()
    data_ingestion.wifi_clients.add(websocket)
    logger.info(f"📡 ESP32 WiFi connected. Total WiFi clients: {len(data_ingestion.wifi_clients)}")
    
    try:
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                data_ingestion.process_sensor_data(data, "WIFI")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from WiFi client: {message}")
                
    except Exception as e:
        logger.info(f"📡 ESP32 WiFi disconnected: {e}")
    finally:
        data_ingestion.wifi_clients.discard(websocket)

@app.on_event("startup")
async def startup_event():
    """Start background services"""
    logger.info("🚀 Starting Smart Agriculture Dual Ingestion Backend")
    data_ingestion.start_usb_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    logger.info("🛑 Shutting down backend")
    data_ingestion.stop_usb_monitoring()

if __name__ == "__main__":
    import uvicorn
    
    print("🌱 Smart Agriculture Dual Data Ingestion Backend")
    print("=" * 60)
    print(f"📡 WebSocket Server: ws://localhost:{WEBSOCKET_PORT}/ws")
    print(f"📡 ESP32 WiFi Endpoint: ws://localhost:{WEBSOCKET_PORT}/wifi")
    print(f"🔌 USB Serial Port: {USB_PORT}")
    print(f"⏱️  WiFi Timeout: {WIFI_TIMEOUT} seconds")
    print(f"📊 WiFi CSV: {CSV_WIFI}")
    print(f"📊 USB CSV: {CSV_USB}")
    print(f"🌐 API: http://localhost:{WEBSOCKET_PORT}/api/source-status")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=WEBSOCKET_PORT)