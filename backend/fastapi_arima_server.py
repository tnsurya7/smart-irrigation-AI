"""
FastAPI ARIMA/ARIMAX Server for Smart Agriculture
Provides model training, prediction, and performance comparison
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import joblib
import json
import os
from pathlib import Path
from datetime import datetime

# Time series models
import pmdarima as pm
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

app = FastAPI(title="Smart Agriculture ARIMA/ARIMAX API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

TRAINING_DATA = DATA_DIR / "training_data.csv"
ARIMA_MODEL = MODELS_DIR / "arima_model.pkl"
ARIMAX_MODEL = MODELS_DIR / "arimax_model.pkl"
MODEL_REPORT = MODELS_DIR / "model_report.json"

# Global model storage
global_arima = None
global_arimax = None
global_report = {}

# Pydantic models
class SensorInput(BaseModel):
    soil: float
    temperature: float
    humidity: float
    rain: float
    light: float

class PredictionResponse(BaseModel):
    predicted_soil: float
    model_used: str

class ModelReport(BaseModel):
    arima_rmse: float
    arimax_rmse: float
    arima_mape: float
    arimax_mape: float
    best_model: str
    trained_at: str

def load_models():
    """Load trained models from disk"""
    global global_arima, global_arimax, global_report
    
    if ARIMA_MODEL.exists():
        global_arima = SARIMAXResults.load(str(ARIMA_MODEL))
    
    if ARIMAX_MODEL.exists():
        global_arimax = SARIMAXResults.load(str(ARIMAX_MODEL))
    
    if MODEL_REPORT.exists():
        with open(MODEL_REPORT, 'r') as f:
            global_report = json.load(f)

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    load_models()
    print("✅ FastAPI ARIMA/ARIMAX Server Started")
    print(f"   ARIMA Model: {'✓' if global_arima else '✗'}")
    print(f"   ARIMAX Model: {'✓' if global_arimax else '✗'}")

@app.get("/")
def root():
    return {
        "service": "Smart Agriculture ARIMA/ARIMAX API",
        "version": "1.0",
        "endpoints": [
            "/upload-data",
            "/train-model",
            "/model-report",
            "/predict",
            "/health"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "arima_loaded": global_arima is not None,
        "arimax_loaded": global_arimax is not None,
        "training_data_exists": TRAINING_DATA.exists()
    }

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload CSV training data
    Expected columns: timestamp, soil, temperature, humidity, rain, light
    """
    try:
        contents = await file.read()
        
        # Save to training data file
        with open(TRAINING_DATA, 'wb') as f:
            f.write(contents)
        
        # Validate CSV
        df = pd.read_csv(TRAINING_DATA)
        required_cols = ['soil', 'temperature', 'humidity', 'rain', 'light']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            raise HTTPException(400, f"Missing columns: {missing}")
        
        return {
            "status": "success",
            "message": f"Uploaded {len(df)} rows",
            "columns": list(df.columns),
            "rows": len(df)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/train-model")
async def train_model(background_tasks: BackgroundTasks):
    """
    Train ARIMA and ARIMAX models
    ARIMA: univariate (soil moisture only)
    ARIMAX: multivariate (soil + temp, humidity, rain, light)
    """
    if not TRAINING_DATA.exists():
        raise HTTPException(400, "No training data. Upload CSV first.")
    
    def train_worker():
        global global_arima, global_arimax, global_report
        
        try:
            # Load data
            df = pd.read_csv(TRAINING_DATA)
            
            # Convert soil from ADC to percentage if needed
            if df['soil'].max() > 100:
                df['soil_pct'] = 100 - (df['soil'] / 4095) * 100
            else:
                df['soil_pct'] = df['soil']
            
            # Convert rain and light to percentage
            if 'rain' in df.columns and df['rain'].max() > 100:
                df['rain_pct'] = (df['rain'] / 4095) * 100
            else:
                df['rain_pct'] = df.get('rain', 0)
            
            if 'light' in df.columns and df['light'].max() > 100:
                df['light_pct'] = (df['light'] / 4095) * 100
            else:
                df['light_pct'] = df.get('light', 0)
            
            # Prepare data
            y = df['soil_pct'].values
            X = df[['temperature', 'humidity', 'rain_pct', 'light_pct']].values
            
            # Train-test split (80-20)
            split_idx = int(len(y) * 0.8)
            y_train, y_test = y[:split_idx], y[split_idx:]
            X_train, X_test = X[:split_idx], X[split_idx:]
            
            print(f"Training with {len(y_train)} samples, testing with {len(y_test)} samples")
            
            # --- ARIMA (univariate) ---
            print("Training ARIMA model...")
            arima_auto = pm.auto_arima(
                y_train,
                start_p=0, start_q=0,
                max_p=5, max_q=5,
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=False
            )
            
            arima_order = arima_auto.order
            print(f"Selected ARIMA order: {arima_order}")
            
            # Fit ARIMA with statsmodels
            arima_model = SARIMAX(y_train, order=arima_order, enforce_stationarity=False, enforce_invertibility=False)
            arima_result = arima_model.fit(disp=False)
            
            # Predict
            arima_pred = arima_result.get_forecast(steps=len(y_test)).predicted_mean
            arima_rmse = float(np.sqrt(mean_squared_error(y_test, arima_pred)))
            arima_mape = float(mean_absolute_percentage_error(y_test, arima_pred))
            
            print(f"ARIMA - RMSE: {arima_rmse:.4f}, MAPE: {arima_mape:.4f}")
            
            # --- ARIMAX (with exogenous) ---
            print("Training ARIMAX model...")
            arimax_auto = pm.auto_arima(
                y_train,
                exogenous=X_train,
                start_p=0, start_q=0,
                max_p=5, max_q=5,
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=False
            )
            
            arimax_order = arimax_auto.order
            print(f"Selected ARIMAX order: {arimax_order}")
            
            # Fit ARIMAX with statsmodels
            arimax_model = SARIMAX(y_train, exog=X_train, order=arimax_order, enforce_stationarity=False, enforce_invertibility=False)
            arimax_result = arimax_model.fit(disp=False)
            
            # Predict
            arimax_pred = arimax_result.get_forecast(steps=len(y_test), exog=X_test).predicted_mean
            arimax_rmse = float(np.sqrt(mean_squared_error(y_test, arimax_pred)))
            arimax_mape = float(mean_absolute_percentage_error(y_test, arimax_pred))
            
            print(f"ARIMAX - RMSE: {arimax_rmse:.4f}, MAPE: {arimax_mape:.4f}")
            
            # Determine best model
            best_model = "ARIMAX" if arimax_rmse < arima_rmse else "ARIMA"
            
            # Save models
            arima_result.save(str(ARIMA_MODEL))
            arimax_result.save(str(ARIMAX_MODEL))
            
            # Save report
            report = {
                "arima_rmse": arima_rmse,
                "arimax_rmse": arimax_rmse,
                "arima_mape": arima_mape,
                "arimax_mape": arimax_mape,
                "best_model": best_model,
                "trained_at": datetime.now().isoformat(),
                "arima_order": arima_order,
                "arimax_order": arimax_order,
                "train_samples": len(y_train),
                "test_samples": len(y_test)
            }
            
            with open(MODEL_REPORT, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Load into global
            global_arima = arima_result
            global_arimax = arimax_result
            global_report = report
            
            print("✅ Training complete!")
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            raise
    
    background_tasks.add_task(train_worker)
    return {"status": "training_started", "message": "Model training in progress"}

@app.get("/model-report")
def get_model_report():
    """
    Get accuracy comparison between ARIMA and ARIMAX
    """
    if not MODEL_REPORT.exists():
        return {
            "arima_rmse": 0,
            "arimax_rmse": 0,
            "arima_mape": 0,
            "arimax_mape": 0,
            "best_model": "None",
            "trained_at": None,
            "error": "No trained models available"
        }
    
    with open(MODEL_REPORT, 'r') as f:
        report = json.load(f)
    
    return report

@app.post("/predict")
def predict_soil(data: SensorInput):
    """
    Predict next-step soil moisture
    Uses ARIMAX if available (better accuracy), otherwise ARIMA
    """
    if global_arimax is None and global_arima is None:
        raise HTTPException(500, "No trained models available. Train models first.")
    
    try:
        # Prepare exogenous data
        rain_pct = (data.rain / 4095) * 100 if data.rain > 100 else data.rain
        light_pct = (data.light / 4095) * 100 if data.light > 100 else data.light
        
        exog = np.array([[data.temperature, data.humidity, rain_pct, light_pct]])
        
        # Use ARIMAX if available (preferred)
        if global_arimax is not None:
            pred = global_arimax.get_forecast(steps=1, exog=exog)
            predicted_soil = float(pred.predicted_mean[0])
            model_used = "ARIMAX"
        else:
            pred = global_arima.get_forecast(steps=1)
            predicted_soil = float(pred.predicted_mean[0])
            model_used = "ARIMA"
        
        # Clamp to valid range
        predicted_soil = max(0, min(100, predicted_soil))
        
        return {
            "predicted_soil": round(predicted_soil, 2),
            "model_used": model_used
        }
    
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

@app.get("/predict-sequence")
def predict_sequence(steps: int = 10):
    """
    Predict next N steps of soil moisture
    """
    if global_arimax is None and global_arima is None:
        raise HTTPException(500, "No trained models available")
    
    try:
        steps = min(max(steps, 1), 50)  # Limit to 1-50 steps
        
        if global_arimax is not None:
            # For sequence prediction, we need to provide exog for each step
            # Use last known values (simplified approach)
            pred = global_arimax.get_forecast(steps=steps)
            predictions = pred.predicted_mean.tolist()
            model_used = "ARIMAX"
        else:
            pred = global_arima.get_forecast(steps=steps)
            predictions = pred.predicted_mean.tolist()
            model_used = "ARIMA"
        
        return {
            "steps": steps,
            "predictions": [round(p, 2) for p in predictions],
            "model_used": model_used
        }
    
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
