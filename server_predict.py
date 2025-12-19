# server_predict.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import joblib
import statsmodels.api as sm
import pandas as pd
import numpy as np
import json
import os
import threading
from train_arimax import train_and_save, REPORT_JSON, MODEL_META, STATSRESULT_FILE

app = FastAPI(title="ARIMAX Prediction API")

# Models / files
REPORT_JSON_PATH = REPORT_JSON
MODEL_META_PATH = MODEL_META
STATSRESULT_PATH = STATSRESULT_FILE

# Pydantic schema for sensor row
class SensorRow(BaseModel):
    timestamp: Optional[str]
    soil: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[float] = None
    rain: Optional[float] = None
    flow: Optional[float] = None

class PredictRequest(BaseModel):
    recent_rows: List[SensorRow]
    steps: Optional[int] = 1

global_meta = {}
global_arimax_res = None

def load_model():
    global global_meta, global_arimax_res
    if os.path.exists(MODEL_META_PATH):
        global_meta = joblib.load(MODEL_META_PATH)
    else:
        global_meta = {}

    if os.path.exists(STATSRESULT_PATH):
        # load statsmodels results object
        global_arimax_res = sm.tsa.SARIMAXResults.load(STATSRESULT_PATH)
    else:
        global_arimax_res = None

@app.on_event("startup")
def startup_event():
    load_model()

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bool(global_arimax_res)}

@app.get("/model-report")
def model_report():
    if os.path.exists(REPORT_JSON_PATH):
        with open(REPORT_JSON_PATH, "r") as fh:
            return json.load(fh)
    else:
        return {"error": "No report found. Run training first."}

@app.post("/predict")
def predict(req: PredictRequest):
    # Validate recent rows
    rows = [r.dict() for r in req.recent_rows]
    if len(rows) < 3:
        raise HTTPException(400, "Provide at least 3 recent rows (time-ordered).")

    df = pd.DataFrame(rows)
    # compute soil_pct and exog as training
    if "soil" in df.columns:
        df["soil_pct"] = df["soil"].astype(float) / 4095.0 * 100.0
    if "rain" in df.columns:
        df["rain_pct"] = df["rain"].astype(float) / 4095.0 * 100.0
    if "light" in df.columns:
        df["light_pct"] = df["light"].astype(float) / 4095.0 * 100.0

    exog_cols = global_meta.get("exog_cols", [])
    exog = df[exog_cols].astype(float) if exog_cols and set(exog_cols).issubset(df.columns) else None

    if global_arimax_res is None:
        raise HTTPException(500, "ARIMAX model not loaded. Train first or run /retrain.")

    steps = max(int(req.steps or 1), 1)
    try:
        # For forecasting use the last row's exog repeated if necessary
        if exog is not None and len(exog) >= 1:
            # prepare forecast exog for `steps` by taking last exog value (simple approach)
            last_exog = exog.tail(1).values
            forecast_exog = pd.DataFrame(np.repeat(last_exog, steps, axis=0), columns=exog_cols)
            pred = global_arimax_res.get_forecast(steps=steps, exog=forecast_exog)
        else:
            pred = global_arimax_res.get_forecast(steps=steps)

        yhat = pred.predicted_mean
        conf = pred.conf_int(alpha=0.05)
        results = []
        for i in range(steps):
            results.append({
                "step": i+1,
                "soil_pct_pred": float(yhat.iloc[i]),
                "ci_lower": float(conf.iloc[i,0]),
                "ci_upper": float(conf.iloc[i,1])
            })
        return {"forecast": results}
    except Exception as e:
        raise HTTPException(500, str(e))

# retrain in background
def retrain_worker(csv_path="soil_moisture_training.csv"):
    try:
        report = train_and_save(csv_path=csv_path, silent=True)
        load_model()  # reload artifacts
        return report
    except Exception as e:
        print("Retrain failed:", e)
        return {"error": str(e)}

@app.post("/retrain")
def retrain(background_tasks: BackgroundTasks, csv_path: str = "soil_moisture_training.csv"):
    background_tasks.add_task(retrain_worker, csv_path)
    return {"status": "retraining", "csv": csv_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
    