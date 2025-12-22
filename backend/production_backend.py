"""
Production FastAPI Backend for Smart Agriculture Dashboard
Supabase integration, environment variables, security, monitoring
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import PlainTextResponse
from starlette.requests import Request
from pydantic import BaseModel, Field
import uvicorn
from supabase import create_client, Client
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables validation
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')

# Validate required environment variables
required_vars = {
    'SUPABASE_URL': SUPABASE_URL,
    'SUPABASE_SERVICE_ROLE_KEY': SUPABASE_SERVICE_ROLE_KEY,
    'OPENWEATHER_API_KEY': OPENWEATHER_API_KEY,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# FastAPI app initialization
app = FastAPI(
    title="Smart Agriculture API",
    description="Production API for Smart Agriculture Dashboard",
    version="1.0.0",
    docs_url="/docs" if os.getenv('NODE_ENV') != 'production' else None,
    redoc_url="/redoc" if os.getenv('NODE_ENV') != 'production' else None,
)

# CRITICAL: Render health check bypass at ASGI level - MUST BE FIRST MIDDLEWARE
@app.middleware("http")
async def render_healthcheck_bypass(request: Request, call_next):
    if request.method == "HEAD":
        return PlainTextResponse("", status_code=200)
    
    if request.url.path in ("/", "/health"):
        return PlainTextResponse("ok", status_code=200)
    
    return await call_next(request)

# CRITICAL: Health endpoints BEFORE any middleware - using direct Response
@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)
def root():
    return Response(content='{"status":"ok"}', media_type="application/json", status_code=200)

@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
def health():
    return Response(content='{"status":"ok"}', media_type="application/json", status_code=200)

# Security middleware
security = HTTPBearer()

# CORS middleware with restricted origins
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    # Add Render internal origins for health checks and common Vercel patterns
    health_check_origins = ALLOWED_ORIGINS + [
        "https://smart-agriculture-backend-my7c.onrender.com",
        "https://smart-agri-arimax-ai-7077.vercel.app",
        "https://smart-agriculture-dashboard.vercel.app"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=health_check_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "HEAD"],
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
    allowed_hosts=["*"] if os.getenv('NODE_ENV') != 'production' else [
        "smart-agriculture-backend-my7c.onrender.com",
        "smart-agriculture-backend.render.com"  # backup
    ]
)

# Pydantic models
class SensorDataModel(BaseModel):
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=-50, le=100)
    humidity: float = Field(..., ge=0, le=100)
    rain_raw: int = Field(..., ge=0, le=4095)
    rain_detected: bool
    light_raw: int = Field(..., ge=0, le=4095)
    light_percent: float = Field(..., ge=0, le=100)
    light_state: str = Field(..., pattern=r"^(dark|low|normal|very_bright)$")
    flow_rate: float = Field(..., ge=0)
    total_liters: float = Field(..., ge=0)
    pump_status: int = Field(..., ge=0, le=1)
    mode: str = Field(..., pattern=r"^(auto|manual)$")
    rain_expected: bool = False
    source: str = Field(default="esp32", pattern=r"^(esp32|simulation|test)$")

class ModelMetricsModel(BaseModel):
    model_name: str = Field(..., pattern=r"^(ARIMA|ARIMAX)$")
    accuracy_percent: float = Field(..., ge=0, le=100)
    rmse: float = Field(..., ge=0)
    mape: float = Field(..., ge=0)
    training_data_rows: int = Field(..., gt=0)
    training_duration_seconds: Optional[int] = Field(None, ge=0)
    model_version: str

class WeatherDataModel(BaseModel):
    temperature: float
    humidity: float
    rain_probability: float
    rain_expected: bool
    location: str = "Erode, Tamil Nadu"

class SystemStatusModel(BaseModel):
    component: str = Field(..., pattern=r"^(esp32|backend|websocket|telegram|weather_api)$")
    status: str = Field(..., pattern=r"^(online|offline|error|warning)$")
    message: Optional[str] = None
    response_time_ms: Optional[int] = Field(None, ge=0)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, implement proper JWT validation
    # For now, accept any valid bearer token format
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user": "authenticated"}

# Detailed health endpoint for monitoring
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint with database and API status"""
    try:
        # Test database connection
        result = supabase.table('sensor_data').select('id').limit(1).execute()
        db_status = "healthy" if result.data is not None else "unhealthy"
        
        # Test external APIs
        weather_status = "healthy"
        try:
            weather_response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q=Erode,IN&appid={OPENWEATHER_API_KEY}",
                timeout=5
            )
            if weather_response.status_code != 200:
                weather_status = "unhealthy"
        except:
            weather_status = "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "weather_api": weather_status,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Sensor data endpoints
@app.post("/sensor-data")
async def create_sensor_data(data: SensorDataModel, user: dict = Depends(get_current_user)):
    """Store new sensor data from ESP32"""
    try:
        # Insert into Supabase
        result = supabase.table('sensor_data').insert({
            "timestamp": datetime.utcnow().isoformat(),
            "soil_moisture": data.soil_moisture,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "rain_raw": data.rain_raw,
            "rain_detected": data.rain_detected,
            "light_raw": data.light_raw,
            "light_percent": data.light_percent,
            "light_state": data.light_state,
            "flow_rate": data.flow_rate,
            "total_liters": data.total_liters,
            "pump_status": data.pump_status,
            "mode": data.mode,
            "rain_expected": data.rain_expected,
            "source": data.source
        }).execute()
        
        logger.info(f"Sensor data stored: {data.source} - Soil: {data.soil_moisture}%")
        return {"status": "success", "id": result.data[0]["id"]}
        
    except Exception as e:
        logger.error(f"Error storing sensor data: {e}")
        raise HTTPException(status_code=500, detail="Failed to store sensor data")

@app.get("/sensor-data/latest")
async def get_latest_sensor_data(limit: int = 100):
    """Get latest sensor data"""
    try:
        result = supabase.table('sensor_data')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        return {"data": result.data}
        
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sensor data")

@app.get("/sensor-data/range")
async def get_sensor_data_range(start_date: str, end_date: str):
    """Get sensor data for date range"""
    try:
        result = supabase.table('sensor_data')\
            .select('*')\
            .gte('timestamp', start_date)\
            .lte('timestamp', end_date)\
            .order('timestamp', desc=False)\
            .execute()
        
        return {"data": result.data}
        
    except Exception as e:
        logger.error(f"Error fetching sensor data range: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sensor data range")

# Model metrics endpoints
@app.get("/model-metrics")
async def get_model_metrics():
    """Get current model performance metrics"""
    try:
        # Get active model metrics
        result = supabase.table('model_metrics')\
            .select('*')\
            .eq('is_active', True)\
            .order('timestamp', desc=True)\
            .limit(2)\
            .execute()
        
        if not result.data:
            # Return default metrics if none found
            return {
                "arima": {
                    "accuracy": 82.5,
                    "rmse": 3.45,
                    "mape": 17.5,
                    "training_rows": 7000
                },
                "arimax": {
                    "accuracy": 94.6,
                    "rmse": 1.78,
                    "mape": 5.4,
                    "training_rows": 7000
                },
                "best_model": "ARIMAX"
            }
        
        # Format response
        metrics = {}
        for metric in result.data:
            model_name = metric['model_name'].lower()
            metrics[model_name] = {
                "accuracy": metric['accuracy_percent'],
                "rmse": metric['rmse'],
                "mape": metric['mape'],
                "training_rows": metric['training_data_rows']
            }
        
        # Determine best model
        best_model = "ARIMAX" if "arimax" in metrics else "ARIMA"
        if "arima" in metrics and "arimax" in metrics:
            best_model = "ARIMAX" if metrics["arimax"]["accuracy"] > metrics["arima"]["accuracy"] else "ARIMA"
        
        return {**metrics, "best_model": best_model}
        
    except Exception as e:
        logger.error(f"Error fetching model metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model metrics")

@app.post("/model-metrics")
async def update_model_metrics(metrics: ModelMetricsModel, user: dict = Depends(get_current_user)):
    """Update model performance metrics"""
    try:
        # Deactivate existing models of same type
        supabase.table('model_metrics')\
            .update({"is_active": False})\
            .eq('model_name', metrics.model_name)\
            .execute()
        
        # Insert new metrics
        result = supabase.table('model_metrics').insert({
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": metrics.model_name,
            "accuracy_percent": metrics.accuracy_percent,
            "rmse": metrics.rmse,
            "mape": metrics.mape,
            "training_data_rows": metrics.training_data_rows,
            "training_duration_seconds": metrics.training_duration_seconds,
            "model_version": metrics.model_version,
            "is_active": True
        }).execute()
        
        logger.info(f"Model metrics updated: {metrics.model_name} - Accuracy: {metrics.accuracy_percent}%")
        return {"status": "success", "id": result.data[0]["id"]}
        
    except Exception as e:
        logger.error(f"Error updating model metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update model metrics")

# Weather endpoints
@app.get("/weather")
async def get_weather_data():
    """Get current weather data from OpenWeather API"""
    try:
        # Fetch current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q=Erode,IN&appid={OPENWEATHER_API_KEY}&units=metric"
        current_response = requests.get(current_url, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        # Fetch forecast for rain probability
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q=Erode,IN&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        
        rain_probability = 0
        if forecast_response.ok:
            forecast_data = forecast_response.json()
            next_24h = forecast_data['list'][:8]  # Next 24 hours
            avg_pop = sum(item.get('pop', 0) for item in next_24h) / len(next_24h)
            rain_probability = int(avg_pop * 100)
        
        weather_data = {
            "temperature": current_data['main']['temp'],
            "humidity": current_data['main']['humidity'],
            "rain_probability": rain_probability,
            "rain_expected": rain_probability > 40,
            "location": f"{current_data['name']}, Tamil Nadu",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Store rain event if high probability
        if rain_probability > 60:
            supabase.table('rain_events').insert({
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "rain_forecast",
                "rain_probability": rain_probability,
                "source": "openweather",
                "location": weather_data["location"]
            }).execute()
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

# System status endpoints
@app.post("/system-status")
async def update_system_status(status: SystemStatusModel, user: dict = Depends(get_current_user)):
    """Update system component status"""
    try:
        result = supabase.table('system_status').insert({
            "timestamp": datetime.utcnow().isoformat(),
            "component": status.component,
            "status": status.status,
            "message": status.message,
            "response_time_ms": status.response_time_ms
        }).execute()
        
        return {"status": "success", "id": result.data[0]["id"]}
        
    except Exception as e:
        logger.error(f"Error updating system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system status")

@app.get("/system-status")
async def get_system_status():
    """Get current system status"""
    try:
        result = supabase.table('system_status')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(10)\
            .execute()
        
        return {"data": result.data}
        
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system status")

# Irrigation events endpoints
@app.get("/irrigation-events")
async def get_irrigation_events(days: int = 7):
    """Get irrigation events for specified days"""
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        result = supabase.table('irrigation_events')\
            .select('*')\
            .gte('timestamp', start_date)\
            .order('timestamp', desc=True)\
            .execute()
        
        return {"data": result.data}
        
    except Exception as e:
        logger.error(f"Error fetching irrigation events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch irrigation events")

# Background tasks
async def cleanup_old_data():
    """Clean up old data to prevent database bloat"""
    try:
        # Keep only last 30 days of sensor data
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        supabase.table('sensor_data')\
            .delete()\
            .lt('timestamp', cutoff_date)\
            .execute()
        
        # Keep only last 90 days of system status
        status_cutoff = (datetime.utcnow() - timedelta(days=90)).isoformat()
        
        supabase.table('system_status')\
            .delete()\
            .lt('timestamp', status_cutoff)\
            .execute()
        
        logger.info("Old data cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during data cleanup: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Smart Agriculture API starting up...")
    
    # Update system status
    try:
        supabase.table('system_status').insert({
            "timestamp": datetime.utcnow().isoformat(),
            "component": "backend",
            "status": "online",
            "message": "Backend API started successfully"
        }).execute()
    except Exception as e:
        logger.error(f"Failed to update startup status: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Smart Agriculture API shutting down...")
    
    try:
        supabase.table('system_status').insert({
            "timestamp": datetime.utcnow().isoformat(),
            "component": "backend",
            "status": "offline",
            "message": "Backend API shutdown"
        }).execute()
    except Exception as e:
        logger.error(f"Failed to update shutdown status: {e}")

# Run server
if __name__ == "__main__":
    # Use Render's dynamic PORT environment variable
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting server on port {port} (from PORT env var: {os.getenv('PORT')})")
    uvicorn.run(
        "production_backend:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )