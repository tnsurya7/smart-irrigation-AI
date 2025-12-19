#!/usr/bin/env python3
"""
WebSocket Server for Smart Agriculture System
Receives sensor data and broadcasts to connected clients
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import uvicorn
import pandas as pd
import os
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CSV file for real sensor data
CSV_FILE = "arimax_real_sensor_data.csv"
BACKEND_URL = "http://localhost:8000"

app = FastAPI(title="Smart Agriculture WebSocket Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_to_csv(sensor_data: Dict[str, Any]):
    """Save ESP32 sensor data to arimax_real_sensor_data.csv"""
    try:
        # Only save if data is from ESP32
        if sensor_data.get("source") != "esp32":
            return
        
        # Prepare data row
        timestamp = datetime.now().isoformat()
        row_data = {
            "timestamp": timestamp,
            "soil_moisture": sensor_data.get("soil", 0),
            "temperature": sensor_data.get("temperature", 0),
            "humidity": sensor_data.get("humidity", 0),
            "rain_pct": (sensor_data.get("rain_raw", 4095) / 4095.0) * 100,
            "light_pct": sensor_data.get("light_percent", 0),
            "flow": sensor_data.get("flow", 0),
            "pump_status": sensor_data.get("pump", 0),
            "mode": sensor_data.get("mode", "auto"),
            "rain_detected": sensor_data.get("rain_detected", False)
        }
        
        # Create DataFrame
        df_new = pd.DataFrame([row_data])
        
        # Append to CSV
        if os.path.exists(CSV_FILE):
            df_new.to_csv(CSV_FILE, mode='a', header=False, index=False)
        else:
            df_new.to_csv(CSV_FILE, index=False)
        
        logger.info(f"💾 Saved ESP32 data to {CSV_FILE}")
        
        # Check if we should trigger retraining (daily - every 100 new rows)
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            total_rows = len(df)
            
            # Trigger retraining every 100 new data points (approximately daily)
            # ESP32 sends data every 5-10 minutes, so 100 points ≈ 8-16 hours
            if total_rows % 100 == 0 and total_rows > 7000:  # Only retrain after initial dataset
                trigger_auto_retrain()
                logger.info(f"🔄 Auto-retrain triggered at {total_rows} total rows")
                
    except Exception as e:
        logger.error(f"❌ Error saving to CSV: {e}")

def trigger_auto_retrain():
    """Trigger automatic model retraining"""
    try:
        response = requests.post(f"{BACKEND_URL}/train", timeout=5)
        if response.status_code == 200:
            logger.info("🔄 Auto-retraining triggered successfully")
        else:
            logger.warning(f"⚠️ Auto-retrain failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Auto-retrain error: {e}")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.latest_data: Dict[str, Any] = {}
        self.data_count = 0
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ Client connected. Total connections: {len(self.active_connections)}")
        
        # Send latest data to new client
        if self.latest_data:
            try:
                await websocket.send_text(json.dumps(self.latest_data))
                logger.info("📤 Sent latest data to new client")
            except Exception as e:
                logger.error(f"❌ Error sending latest data: {e}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: str, exclude_sender: WebSocket = None):
        """Broadcast message to all connected clients except sender"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            # Skip the sender to prevent echo loop
            if connection == exclude_sender:
                continue
                
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def update_latest_data(self, data: Dict[str, Any]):
        """Update latest sensor data and save to CSV"""
        self.latest_data = data
        self.data_count += 1
        
        # Save ESP32 data to CSV
        save_to_csv(data)
        
        logger.info(f"📊 Updated latest data (#{self.data_count}): {data}")

# Global connection manager
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for sensor data"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive data from USB bridge or other sources
            data = await websocket.receive_text()
            logger.info(f"📡 Received: {data}")
            
            try:
                # Parse JSON data
                sensor_data = json.loads(data)
                
                # Add server timestamp
                sensor_data['server_timestamp'] = datetime.now().isoformat()
                
                # Update latest data
                manager.update_latest_data(sensor_data)
                
                # Broadcast to all other clients (exclude sender to prevent echo loop)
                await manager.broadcast(json.dumps(sensor_data), exclude_sender=websocket)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON received: {e}")
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint specifically for dashboard clients"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and listen for any messages from dashboard
            message = await websocket.receive_text()
            logger.info(f"📱 Dashboard message: {message}")
            
            # Echo back or handle dashboard-specific commands
            if message == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ Dashboard WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Smart Agriculture WebSocket Server",
        "endpoints": {
            "websocket": "/ws",
            "dashboard": "/dashboard",
            "status": "/status"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
def get_status():
    """Get server status"""
    return {
        "status": "running",
        "active_connections": len(manager.active_connections),
        "latest_data": manager.latest_data,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/simulate-data")
async def simulate_sensor_data():
    """Simulate sensor data for testing"""
    import random
    
    simulated_data = {
        "soil": round(random.uniform(20, 80), 1),
        "temp": round(random.uniform(20, 35), 1),
        "humidity": round(random.uniform(40, 90), 1),
        "rain": random.randint(0, 1000),
        "light": random.randint(100, 2000),
        "flow": round(random.uniform(0, 10), 1),
        "pump": random.choice([0, 1]),
        "mode": random.choice(["auto", "manual"]),
        "timestamp": datetime.now().isoformat()
    }
    
    # Update latest data and broadcast
    manager.update_latest_data(simulated_data)
    await manager.broadcast(json.dumps(simulated_data))
    
    return {"message": "Simulated data sent", "data": simulated_data}

if __name__ == "__main__":
    print("🌱 Smart Agriculture WebSocket Server")
    print("=" * 50)
    print("🔗 WebSocket Endpoints:")
    print("   • ws://localhost:8080/ws (USB Bridge)")
    print("   • ws://localhost:8080/dashboard (Dashboard)")
    print("📡 HTTP Endpoints:")
    print("   • http://localhost:8080/ (Status)")
    print("   • http://localhost:8080/status (Detailed Status)")
    print("   • http://localhost:8080/simulate-data (Test Data)")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    uvicorn.run("websocket_server:app", host="0.0.0.0", port=8080, reload=False)