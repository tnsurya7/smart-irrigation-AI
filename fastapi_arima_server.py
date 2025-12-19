"""
fastapi_arima_server.py

Comprehensive FastAPI server for Smart Agriculture:
- trains ARIMA and ARIMAX models from CSV
- serves /predict, /model-report, /train-model, /health
- allows CSV upload (POST /upload-data)
- saves artifacts to disk
- CORS enabled for frontend
"""

import os
import json
import joblib
import warnings
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults
import pmdarima as pm
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

warnings.filterwarnings("ignore")

# -----------------------
# Config / artifact paths
# -----------------------
DATA_CSV = "soil_moisture_training.csv"     # main CSV used for training
MODEL_META = "model_meta.joblib"            # meta: orders & exog cols
ARIMA_PICKLE = "arima_result.pickle"        # statsmodels ARIMA result (univariate)
ARIMAX_PICKLE = "arimax_result.pickle"      # statsmodels ARIMAX result (if trained)
REPORT_JSON = "model_report.json"           # report with metrics
MIN_ROWS_TO_TRAIN = 20

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(title="ARIMA/ARIMAX Prediction Server")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cached model artifacts
_model_meta = {}
_arimax_res = None
_arima_res = None

# -----------------------
# Pydantic models
# -----------------------
class SensorRow(BaseModel):
    timestamp: Optional[str] = None
    soil: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[float] = None
    rain: Optional[float] = None
    flow: Optional[float] = None

class PredictRequest(BaseModel):
    recent_rows: List[SensorRow]
    steps: Optional[int] = 1

class SimplePredictRequest(BaseModel):
    soil: float
    temperature: float
    humidity: float
    rain: float
    light: float

# -----------------------
# Utility: load & save models
# -----------------------
def _load_artifacts():
    global _model_meta, _arimax_res, _arima_res
    _model_meta = {}
    _arimax_res = None
    _arima_res = None

    if Path(MODEL_META).exists():
        _model_meta = joblib.load(MODEL_META)
    if Path(ARIMAX_PICKLE).exists():
        try:
            _arimax_res = SARIMAXResults.load(ARIMAX_PICKLE)
        except Exception as e:
            print("Failed to load ARIMAX result:", e)
            _arimax_res = None
    if Path(ARIMA_PICKLE).exists():
        try:
            _arima_res = SARIMAXResults.load(ARIMA_PICKLE)
        except Exception as e:
            print("Failed to load ARIMA result:", e)
            _arima_res = None

# call at startup
_load_artifacts()

# -----------------------
# Data preparation helper
# -----------------------
def prepare_df_from_csv(path: str):
    df = pd.read_csv(path, parse_dates=["timestamp"], infer_datetime_format=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Convert raw ADC to percent for soil, rain, light if present
    if "soil" in df.columns:
        df["soil_pct"] = df["soil"].astype(float) / 4095.0 * 100.0
    if "rain" in df.columns:
        df["rain_pct"] = df["rain"].astype(float) / 4095.0 * 100.0
    if "light" in df.columns:
        df["light_pct"] = df["light"].astype(float) / 4095.0 * 100.0

    # drop rows missing target
    df = df.dropna(subset=["soil_pct"]).reset_index(drop=True)
    return df

# -----------------------
# Training function
# -----------------------
def train_models(csv_path: str = DATA_CSV,
                 test_frac: float = 0.2,
                 max_p: int = 5,
                 max_q: int = 5,
                 stepwise: bool = True,
                 silent: bool = False):
    """
    Train ARIMA (univariate) and ARIMAX (with exogenous) if exog present.
    Saves artifacts to disk and returns a report dict.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found.")

    df = prepare_df_from_csv(str(csv_path))
    n = len(df)
    if n < MIN_ROWS_TO_TRAIN:
        raise ValueError(f"Not enough rows to train (found {n}, need at least {MIN_ROWS_TO_TRAIN}).")

    # Identify possible exogenous columns from the dataset
    exog_candidates = [c for c in ["temperature", "humidity", "rain_pct", "light_pct", "flow"] if c in df.columns]

    y = df["soil_pct"].astype(float)
    X = df[exog_candidates].astype(float) if exog_candidates else None

    # Train/test split (time-based)
    n_test = max(int(len(df) * test_frac), 3)
    train_y, test_y = y[:-n_test], y[-n_test:]
    train_X, test_X = (X[:-n_test], X[-n_test:]) if X is not None else (None, None)

    if not silent:
        print(f"Training rows: {len(train_y)}, Testing rows: {len(test_y)}, Exog: {exog_candidates}")

    # -----------------
    # ARIMA (univariate) baseline
    # -----------------
    arima_auto = pm.auto_arima(
        train_y,
        start_p=0, start_q=0,
        max_p=max_p, max_q=max_q,
        d=None,
        seasonal=False,
        stepwise=stepwise,
        suppress_warnings=True,
        error_action="ignore",
        trace=not silent
    )
    arima_order = arima_auto.order
    if not silent:
        print("Selected ARIMA order:", arima_order)

    arima_model = SARIMAX(train_y, order=arima_order, enforce_stationarity=False, enforce_invertibility=False)
    arima_res = arima_model.fit(disp=False)

    arima_forecast = arima_res.get_forecast(steps=len(test_y))
    arima_pred = arima_forecast.predicted_mean
    arima_rmse = float(np.sqrt(mean_squared_error(test_y, arima_pred)))
    arima_mape = float(mean_absolute_percentage_error(test_y, arima_pred))

    if not silent:
        print(f"ARIMA RMSE={arima_rmse:.4f}, MAPE={arima_mape:.4%}")

    # -----------------
    # ARIMAX (with exogenous) if exog exists
    # -----------------
    arimax_res = None
    arimax_order = None
    arimax_rmse = None
    arimax_mape = None

    if X is not None and len(exog_candidates) > 0:
        arimax_auto = pm.auto_arima(
            train_y,
            exogenous=train_X,
            start_p=0, start_q=0,
            max_p=max_p, max_q=max_q,
            d=None,
            seasonal=False,
            stepwise=stepwise,
            suppress_warnings=True,
            error_action="ignore",
            trace=not silent
        )
        arimax_order = arimax_auto.order
        if not silent:
            print("Selected ARIMAX order:", arimax_order)

        arimax_model = SARIMAX(
            train_y,
            exog=train_X,
            order=arimax_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        arimax_res = arimax_model.fit(disp=False)

        arimax_forecast = arimax_res.get_forecast(steps=len(test_y), exog=test_X)
        arimax_pred = arimax_forecast.predicted_mean
        arimax_rmse = float(np.sqrt(mean_squared_error(test_y, arimax_pred)))
        arimax_mape = float(mean_absolute_percentage_error(test_y, arimax_pred))

        if not silent:
            print(f"ARIMAX RMSE={arimax_rmse:.4f}, MAPE={arimax_mape:.4%}")
    else:
        if not silent:
            print("No exogenous variables found: Skipping ARIMAX training.")

    # -----------------
    # Save artifacts
    # -----------------
    # save univariate ARIMA result
    try:
        arima_res.save(ARIMA_PICKLE)
    except Exception as e:
        print("Warning: failed to save ARIMA result:", e)

    # save ARIMAX result if available
    if arimax_res is not None:
        try:
            arimax_res.save(ARIMAX_PICKLE)
        except Exception as e:
            print("Warning: failed to save ARIMAX result:", e)

    meta = {
        "arima_order": arima_order,
        "arimax_order": arimax_order,
        "exog_cols": exog_candidates,
        "rows": len(df)
    }
    joblib.dump(meta, MODEL_META)

    report = {
        "rows": len(df),
        "train_rows": len(train_y),
        "test_rows": len(test_y),
        "exog_cols": exog_candidates,
        "arima_order": arima_order,
        "arima_rmse": arima_rmse,
        "arima_mape": arima_mape,
        "arimax_order": arimax_order,
        "arimax_rmse": arimax_rmse,
        "arimax_mape": arimax_mape
    }
    with open(REPORT_JSON, "w") as fh:
        json.dump(report, fh, indent=2)

    # reload to global
    _load_artifacts()
    return report

# -----------------------
# Endpoint: health
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bool(_arimax_res or _arima_res)}

# -----------------------
# Endpoint: model report
# -----------------------
@app.get("/model-report")
def model_report():
    if Path(REPORT_JSON).exists():
        with open(REPORT_JSON, "r") as fh:
            report = json.load(fh)
            
            # Add best_model field for frontend
            arima_rmse = report.get("arima_rmse", 0)
            arimax_rmse = report.get("arimax_rmse", 0)
            
            if arimax_rmse and arima_rmse:
                report["best_model"] = "ARIMAX" if arimax_rmse < arima_rmse else "ARIMA"
            else:
                report["best_model"] = "ARIMA" if arima_rmse else "None"
            
            return report
    else:
        return {
            "error": "No report found. Train model first.",
            "arima_rmse": 0,
            "arimax_rmse": 0,
            "arima_mape": 0,
            "arimax_mape": 0,
            "best_model": "None"
        }

# -----------------------
# Endpoint: predict
# -----------------------
@app.post("/predict")
def predict(req: PredictRequest):
    global _arimax_res, _arima_res, _model_meta
    rows = [r.dict() for r in req.recent_rows]
    if len(rows) < 3:
        raise HTTPException(status_code=400, detail="Provide at least 3 recent rows (time-ordered).")

    df = pd.DataFrame(rows)
    # prepare columns same as training
    if "soil" in df.columns:
        df["soil_pct"] = df["soil"].astype(float) / 4095.0 * 100.0
    if "rain" in df.columns:
        df["rain_pct"] = df["rain"].astype(float) / 4095.0 * 100.0
    if "light" in df.columns:
        df["light_pct"] = df["light"].astype(float) / 4095.0 * 100.0

    exog_cols = _model_meta.get("exog_cols", [])
    exog = None
    if exog_cols and set(exog_cols).issubset(df.columns):
        exog = df[exog_cols].astype(float)

    steps = max(int(req.steps or 1), 1)

    # prefer ARIMAX if available
    if _arimax_res is not None and exog is not None:
        # prepare forecast exog: use last exog repeated for `steps` (simple approach)
        last_exog = exog.tail(1).values
        forecast_exog = pd.DataFrame(np.repeat(last_exog, steps, axis=0), columns=exog_cols)
        try:
            pred = _arimax_res.get_forecast(steps=steps, exog=forecast_exog)
            yhat = pred.predicted_mean
            conf = pred.conf_int(alpha=0.05)
            out = []
            for i in range(steps):
                out.append({
                    "step": i+1,
                    "soil_pct_pred": float(yhat.iloc[i]),
                    "ci_lower": float(conf.iloc[i, 0]),
                    "ci_upper": float(conf.iloc[i, 1])
                })
            return {"model": "ARIMAX", "forecast": out}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ARIMAX forecast failed: {e}")

    # fallback to ARIMA if ARIMAX not available
    if _arima_res is not None:
        try:
            pred = _arima_res.get_forecast(steps=steps)
            yhat = pred.predicted_mean
            conf = pred.conf_int(alpha=0.05)
            out = []
            for i in range(steps):
                out.append({
                    "step": i+1,
                    "soil_pct_pred": float(yhat.iloc[i]),
                    "ci_lower": float(conf.iloc[i, 0]),
                    "ci_upper": float(conf.iloc[i, 1])
                })
            return {"model": "ARIMA", "forecast": out}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ARIMA forecast failed: {e}")

    raise HTTPException(status_code=500, detail="No trained model available. Run /retrain or train manually.")

# -----------------------
# Endpoint: train-model (alias for retrain)
# -----------------------
def _background_retrain(csv_path: str):
    try:
        print("Retraining started in background...")
        report = train_models(csv_path=csv_path, silent=True)
        print("Retraining finished:", report)
    except Exception as e:
        print("Retrain failed:", e)

@app.post("/train-model")
@app.post("/retrain")
def retrain(background_tasks: BackgroundTasks, csv_path: str = DATA_CSV):
    # start background task
    background_tasks.add_task(_background_retrain, csv_path)
    return {"status": "training_started", "csv": csv_path, "message": "Model training in progress"}

# -----------------------
# Endpoint: simple predict (single sensor reading)
# -----------------------
@app.post("/predict-simple")
def predict_simple(data: SimplePredictRequest):
    """
    Predict next-step soil moisture from single sensor reading
    Input: {soil, temperature, humidity, rain, light}
    Output: {predicted_soil: float}
    """
    global _arimax_res, _arima_res, _model_meta
    
    if not _arimax_res and not _arima_res:
        raise HTTPException(status_code=500, detail="No trained model available. Train first.")
    
    try:
        # Convert to percentage
        soil_pct = (data.soil / 4095.0 * 100.0) if data.soil > 100 else data.soil
        rain_pct = (data.rain / 4095.0 * 100.0) if data.rain > 100 else data.rain
        light_pct = (data.light / 4095.0 * 100.0) if data.light > 100 else data.light
        
        exog_cols = _model_meta.get("exog_cols", [])
        
        # Prefer ARIMAX if available
        if _arimax_res and exog_cols:
            exog_data = []
            for col in exog_cols:
                if col == "temperature":
                    exog_data.append(data.temperature)
                elif col == "humidity":
                    exog_data.append(data.humidity)
                elif col == "rain_pct":
                    exog_data.append(rain_pct)
                elif col == "light_pct":
                    exog_data.append(light_pct)
                else:
                    exog_data.append(0)
            
            exog_df = pd.DataFrame([exog_data], columns=exog_cols)
            pred = _arimax_res.get_forecast(steps=1, exog=exog_df)
            predicted_soil = float(pred.predicted_mean[0])
        elif _arima_res:
            pred = _arima_res.get_forecast(steps=1)
            predicted_soil = float(pred.predicted_mean[0])
        else:
            raise HTTPException(status_code=500, detail="No model available")
        
        # Clamp to valid range
        predicted_soil = max(0, min(100, predicted_soil))
        
        return {"predicted_soil": round(predicted_soil, 2)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# -----------------------
# Endpoint: upload CSV
# -----------------------
@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...), append: bool = True):
    """
    Upload a CSV (same format as sensor_data.csv).
    If append=True (default), append to existing DATA_CSV; otherwise overwrite.
    """
    content = await file.read()
    tmp = Path("upload_tmp.csv")
    tmp.write_bytes(content)
    # validate simple CSV: must have timestamp and soil
    try:
        df_new = pd.read_csv(tmp, parse_dates=["timestamp"])
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    if "soil" not in df_new.columns:
        tmp.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="CSV must include 'soil' column.")

    # Append or overwrite
    if Path(DATA_CSV).exists() and append:
        df_existing = pd.read_csv(DATA_CSV, parse_dates=["timestamp"])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(DATA_CSV, index=False)
    else:
        df_new.to_csv(DATA_CSV, index=False)

    tmp.unlink(missing_ok=True)
    return {"status": "ok", "rows_added": len(df_new)}

# -----------------------
# Run via uvicorn
# -----------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI ARIMA/ARIMAX server...")
    uvicorn.run("fastapi_arima_server:app", host="0.0.0.0", port=8001, reload=False)