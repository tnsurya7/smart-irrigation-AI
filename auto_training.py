import csv
import os
import pandas as pd
from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from train_arimax import train_arimax_model
from train_arima import train_arima_model

DATA_DIR = "data"
ARIMA_FILE = f"{DATA_DIR}/arima_data.csv"
ARIMAX_FILE = f"{DATA_DIR}/arimax_data.csv"

os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.start()

# -------------------------------
# SAVE LIVE SENSOR DATA
# -------------------------------
def save_realtime_data(sensor: dict):
    df_row = pd.DataFrame([sensor])

    # Save for ARIMAX training (multivariate)
    if not os.path.exists(ARIMAX_FILE):
        df_row.to_csv(ARIMAX_FILE, index=False)
    else:
        df_row.to_csv(ARIMAX_FILE, mode="a", header=False, index=False)

    # Save for ARIMA training (soil moisture only)
    soil_only = {"timestamp": sensor["timestamp"], "soil_pct": sensor["soil_pct"]}
    if not os.path.exists(ARIMA_FILE):
        pd.DataFrame([soil_only]).to_csv(ARIMA_FILE, index=False)
    else:
        pd.DataFrame([soil_only]).to_csv(ARIMA_FILE, mode="a", header=False, index=False)


# -------------------------------
# AUTO TRAIN ARIMA (every 12 hrs)
# -------------------------------
def auto_train_arima():
    if os.path.exists(ARIMA_FILE):
        print("⏳ Training ARIMA…")
        train_arima_model(ARIMA_FILE)
        print("✅ ARIMA model retrained!")


# -------------------------------
# AUTO TRAIN ARIMAX (nightly)
# -------------------------------
def auto_train_arimax():
    if os.path.exists(ARIMAX_FILE):
        df = pd.read_csv(ARIMAX_FILE)

        if len(df) >= 200:
            print("⏳ Training ARIMAX with real IOT data…")
            train_arimax_model(ARIMAX_FILE)
            print("✅ ARIMAX model retrained!")
        else:
            print("⚠️ Not enough real data for ARIMAX training")


# -------------------------------
# SCHEDULERS
# -------------------------------
scheduler.add_job(auto_train_arima, "interval", hours=12)
scheduler.add_job(auto_train_arimax, "cron", hour=2, minute=0)

# -------------------------------
# ENDPOINT FOR LIVE DATA RECEIVE
# -------------------------------
@app.post("/live-data")
async def incoming_sensor_data(sensor: dict):
    """
    Called by server.cjs when ESP32 sends sensor data.
    """
    sensor["timestamp"] = datetime.now()

    # Convert soil raw 0–4095 → %
    sensor["soil_pct"] = round((sensor["soil"] / 4095) * 100, 2)
    sensor["rain_pct"] = round((sensor["rain"] / 4095) * 100, 2)
    sensor["light_pct"] = round((sensor["light"] / 4095) * 100, 2)

    save_realtime_data(sensor)
    return {"status": "saved"}