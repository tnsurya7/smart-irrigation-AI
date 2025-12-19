"""
Production WebSocket Server for Smart Agriculture Dashboard
Handles ESP32 connections, dashboard clients, and real-time data streaming
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional
from pathlib import Path

import websockets
from websockets.server import WebSocketServerProtocol
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from supabase import create_client, Client
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables validation
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
WS_HOST = os.getenv('WS_HOST', '0.0.0.0')
WS_PORT = int(os.getenv('WS_PORT', 8080))
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# FastAPI app for WebSocket
app = FastAPI(
    title="Smart Agriculture WebSocket Server",
    description="Production WebSocket server for real-time data streaming",
    version="1.0.0"
)

# CORS middleware
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    logger.warning("ALLOWED_ORIGINS not set - allowing all origins (development only)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if os.getenv('NODE_ENV') != 'production' else ["smart-agriculture-websocket.render.com"]
)

# Connection management
class ConnectionManager:
    def __init__(self):
        self.esp32_connections: Dict[str, WebSocket] = {}
        self.dashboard_connections: Set[WebSocket] = set()
        self.latest_sensor_data: Optional[Dict[str, Any]] = None
        self.connection_count = 0
        
    async def connect_esp32(self, websocket: WebSocket, device_id: str):
        """Connect ESP32 device"""
        await websocket.accept()
        self.esp32_connections[device_id] = websocket
        self.connection_count += 1
        
        logger.info(f"ESP32 connected: {device_id} (Total connections: {self.connection_count})")
        
        # Update system status
        await self.update_system_status("esp32", "online", f"ESP32 {device_id} connected")
        
    async def connect_dashboard(self, websocket: WebSocket):
        """Connect dashboard client"""
        await websocket.accept()
        self.dashboard_connections.add(websocket)
        self.connection_count += 1
        
        logger.info(f"Dashboard connected (Total connections: {self.connection_count})")
        
        # Send latest data if available
        if self.latest_sensor_data:
            try:
                await websocket.send_text(json.dumps(self.latest_sensor_data))
            except Exception as e:
                logger.error(f"Error sending latest data to new dashboard: {e}")
    
    async def disconnect_esp32(self, device_id: str):
        """Disconnect ESP32 device"""
        if device_id in self.esp32_connections:
            del self.esp32_connections[device_id]
            self.connection_count -= 1
            
            logger.info(f"ESP32 disconnected: {device_id} (Total connections: {self.connection_count})")
            
            # Update system status
            await self.update_system_status("esp32", "offline", f"ESP32 {device_id} disconnected")
    
    async def disconnect_dashboard(self, websocket: WebSocket):
        """Disconnect dashboard client"""
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
            self.connection_count -= 1
            
            logger.info(f"Dashboard disconnected (Total connections: {self.connection_count})")
    
    async def broadcast_to_dashboards(self, message: Dict[str, Any]):
        """Broadcast message to all connected dashboards"""
        if not self.dashboard_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.dashboard_connections:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to dashboard: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            await self.disconnect_dashboard(websocket)
    
    async def send_to_esp32(self, device_id: str, message: Dict[str, Any]):
        """Send message to specific ESP32 device"""
        if device_id not in self.esp32_connections:
            raise ValueError(f"ESP32 {device_id} not connected")
        
        try:
            websocket = self.esp32_connections[device_id]
            await websocket.send_text(json.dumps(message))
            logger.info(f"Message sent to ESP32 {device_id}: {message}")
        except Exception as e:
            logger.error(f"Error sending to ESP32 {device_id}: {e}")
            await self.disconnect_esp32(device_id)
            raise
    
    async def process_sensor_data(self, data: Dict[str, Any]):
        """Process and store sensor data from ESP32"""
        try:
            # Validate required fields
            required_fields = ['soil', 'temperature', 'humidity', 'pump', 'mode']
            if not all(field in data for field in required_fields):
                logger.error(f"Missing required fields in sensor data: {data}")
                return
            
            # Normalize data format
            normalized_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "soil_moisture": float(data.get('soil', 0)),
                "temperature": float(data.get('temperature', 0)),
                "humidity": float(data.get('humidity', 0)),
                "rain_raw": int(data.get('rain_raw', 4095)),
                "rain_detected": bool(data.get('rain_detected', False)),
                "light_raw": int(data.get('light_raw', 500)),
                "light_percent": float(data.get('light_percent', 50)),
                "light_state": data.get('light_state', 'normal'),
                "flow_rate": float(data.get('flow', 0)),
                "total_liters": float(data.get('total', 0)),
                "pump_status": int(data.get('pump', 0)),
                "mode": str(data.get('mode', 'AUTO')).upper(),
                "rain_expected": bool(data.get('rain_expected', False)),
                "source": "esp32"
            }
            
            # Store in Supabase
            result = supabase.table('sensor_data').insert(normalized_data).execute()
            
            if result.data:
                logger.info(f"Sensor data stored: Soil {normalized_data['soil_moisture']}%, Temp {normalized_data['temperature']}°C")
                
                # Update latest data
                self.latest_sensor_data = {
                    **normalized_data,
                    "source": "esp32",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Broadcast to dashboards
                await self.broadcast_to_dashboards(self.latest_sensor_data)
                
                # Check for irrigation events
                await self.check_irrigation_events(normalized_data)
                
            else:
                logger.error("Failed to store sensor data in database")
                
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
    
    async def check_irrigation_events(self, data: Dict[str, Any]):
        """Check and log irrigation events"""
        try:
            pump_status = data.get('pump_status', 0)
            mode = data.get('mode', 'AUTO')
            soil_moisture = data.get('soil_moisture', 0)
            
            # Determine event type based on pump status change
            # This is simplified - in production, you'd track state changes
            if pump_status == 1:
                event_type = "auto_start" if mode == "AUTO" else "manual_start"
                trigger_reason = f"Soil moisture: {soil_moisture}%" if mode == "AUTO" else "Manual activation"
                
                # Log irrigation event
                supabase.table('irrigation_events').insert({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "trigger_reason": trigger_reason,
                    "soil_moisture_before": soil_moisture,
                    "mode": mode
                }).execute()
                
                logger.info(f"Irrigation event logged: {event_type} - {trigger_reason}")
                
        except Exception as e:
            logger.error(f"Error checking irrigation events: {e}")
    
    async def update_system_status(self, component: str, status: str, message: str = None):
        """Update system status in database"""
        try:
            supabase.table('system_status').insert({
                "timestamp": datetime.utcnow().isoformat(),
                "component": component,
                "status": status,
                "message": message
            }).execute()
        except Exception as e:
            logger.error(f"Error updating system status: {e}")

# Global connection manager
manager = ConnectionManager()

# WebSocket endpoints
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for all connections"""
    client_type = None
    device_id = None
    
    try:
        # Accept connection initially
        await websocket.accept()
        
        # Wait for identification message
        data = await websocket.receive_text()
        message = json.loads(data)
        
        client_type = message.get('type', 'unknown')
        
        if client_type == 'esp32':
            device_id = message.get('device_id', 'esp32_default')
            await manager.connect_esp32(websocket, device_id)
            
        elif client_type == 'dashboard':
            await manager.connect_dashboard(websocket)
            
        else:
            logger.warning(f"Unknown client type: {client_type}")
            await websocket.close(code=4000, reason="Unknown client type")
            return
        
        # Handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if client_type == 'esp32':
                    # Process sensor data from ESP32
                    if message.get('source') == 'esp32':
                        await manager.process_sensor_data(message)
                    
                elif client_type == 'dashboard':
                    # Handle dashboard commands
                    await handle_dashboard_command(message, device_id or 'esp32_default')
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Cleanup on disconnect
        if client_type == 'esp32' and device_id:
            await manager.disconnect_esp32(device_id)
        elif client_type == 'dashboard':
            await manager.disconnect_dashboard(websocket)

async def handle_dashboard_command(message: Dict[str, Any], esp32_device_id: str):
    """Handle commands from dashboard to ESP32"""
    try:
        command_type = message.get('type')
        
        if command_type == 'pump_command':
            # Send pump command to ESP32
            pump_cmd = {
                "pump_cmd": message.get('command', 'OFF')
            }
            await manager.send_to_esp32(esp32_device_id, pump_cmd)
            
        elif command_type == 'mode_change':
            # Send mode change to ESP32
            mode_cmd = {
                "mode": message.get('mode', 'auto').lower()
            }
            await manager.send_to_esp32(esp32_device_id, mode_cmd)
            
        elif command_type == 'rain_forecast':
            # Send rain forecast to ESP32
            rain_cmd = {
                "rain_expected": message.get('rain_expected', False)
            }
            await manager.send_to_esp32(esp32_device_id, rain_cmd)
            
        else:
            logger.warning(f"Unknown dashboard command: {command_type}")
            
    except Exception as e:
        logger.error(f"Error handling dashboard command: {e}")

# HTTP endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "connections": {
            "esp32": len(manager.esp32_connections),
            "dashboard": len(manager.dashboard_connections),
            "total": manager.connection_count
        },
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get current WebSocket server status"""
    return {
        "connections": {
            "esp32_devices": list(manager.esp32_connections.keys()),
            "dashboard_clients": len(manager.dashboard_connections),
            "total_connections": manager.connection_count
        },
        "latest_data": manager.latest_sensor_data,
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize WebSocket server on startup"""
    logger.info("Smart Agriculture WebSocket Server starting up...")
    
    # Update system status
    await manager.update_system_status("websocket", "online", "WebSocket server started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Smart Agriculture WebSocket Server shutting down...")
    
    # Update system status
    await manager.update_system_status("websocket", "offline", "WebSocket server shutdown")

# Run server
if __name__ == "__main__":
    # SSL configuration for production
    ssl_context = None
    if SSL_CERT_PATH and SSL_KEY_PATH and os.path.exists(SSL_CERT_PATH) and os.path.exists(SSL_KEY_PATH):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)
        logger.info("SSL enabled for WebSocket server")
    
    uvicorn.run(
        "production_websocket:app",
        host=WS_HOST,
        port=WS_PORT,
        ssl_keyfile=SSL_KEY_PATH if ssl_context else None,
        ssl_certfile=SSL_CERT_PATH if ssl_context else None,
        reload=False,
        access_log=True,
        log_level="info"
    )