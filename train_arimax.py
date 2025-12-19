# train_arimax.py
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
import warnings
warnings.filterwarnings("ignore")

# modeling
import pmdarima as pm
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Output artifacts
MODEL_META = "arimax_metadata.joblib"
STATSRESULT_FILE = "statsmodel_result.pickle"
REPORT_JSON = "model_report.json"

def load_and_prepare(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Handle soil_moisture column (already in percentage format in training CSV)
    if "soil_moisture" in df.columns:
        df["soil_pct"] = df["soil_moisture"].astype(float)
    elif "soil" in df.columns:
        # For real-time ESP32 data (ADC format), convert to percentage
        df["soil_pct"] = df["soil"].astype(float) / 4095.0 * 100.0
    
    # rain_pct and light_pct are already in percentage in training CSV
    # Only convert if they're in ADC format (for ESP32 data)
    if "rain" in df.columns and "rain_pct" not in df.columns:
        df["rain_pct"] = df["rain"].astype(float) / 4095.0 * 100.0
    if "light" in df.columns and "light_pct" not in df.columns:
        df["light_pct"] = df["light"].astype(float) / 4095.0 * 100.0

    # drop rows missing target
    df = df.dropna(subset=["soil_pct"]).reset_index(drop=True)
    return df

def train_and_save(
    csv_path: str = "soil_moisture_training.csv",
    test_frac: float = 0.2,
    max_p: int = 5,
    max_q: int = 5,
    seasonal: bool = False,
    stepwise: bool = True,
    silent: bool = False
):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found. Generate or place your CSV at this path.")

    df = load_and_prepare(str(csv_path))
    if len(df) < 20:
        raise ValueError("Need more rows to train (>= 20).")

    # Choose exogenous columns if present
    exog_candidates = []
    for c in ["temperature", "humidity", "rain_pct", "light_pct", "flow"]:
        if c in df.columns:
            exog_candidates.append(c)

    # Target
    y = df["soil_pct"].astype(float)
    X = df[exog_candidates].astype(float) if exog_candidates else None

    n_test = max(int(len(df) * test_frac), 3)
    train_y, test_y = y[:-n_test], y[-n_test:]
    train_X, test_X = (X[:-n_test], X[-n_test:]) if X is not None else (None, None)

    if not silent:
        print(f"Rows total={len(df)}, train={len(train_y)}, test={len(test_y)}, exog_cols={exog_candidates}")

    # --- ARIMA baseline (univariate) ---
    # Use pmdarima to auto-select order for univariate ARIMA on train set
    if not silent:
        print("Auto-selecting order for ARIMA (univariate)...")
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

    # Fit ARIMA (statsmodels) on train
    arima_model = sm.tsa.SARIMAX(train_y, order=arima_order, enforce_stationarity=False, enforce_invertibility=False)
    arima_res = arima_model.fit(disp=False)

    # Forecast with ARIMA
    arima_forecast = arima_res.get_forecast(steps=len(test_y))
    arima_pred = arima_forecast.predicted_mean
    arima_rmse = float(np.sqrt(mean_squared_error(test_y, arima_pred)))
    arima_mape = float(mean_absolute_percentage_error(test_y, arima_pred))

    if not silent:
        print(f"ARIMA test RMSE={arima_rmse:.4f}, MAPE={arima_mape:.4%}")

    # --- ARIMAX (exogenous) if exog present ---
    if X is not None and exog_candidates:
        if not silent:
            print("Auto-selecting ARIMAX order (with exog)...")
        # pmdarima can choose order using exogenous
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

        # Fit final SARIMAX via statsmodels with exog
        arimax_model = sm.tsa.SARIMAX(
            train_y,
            exog=train_X,
            order=arimax_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        arimax_res = arimax_model.fit(disp=False)

        # Forecast on test
        arimax_forecast = arimax_res.get_forecast(steps=len(test_y), exog=test_X)
        arimax_pred = arimax_forecast.predicted_mean
        arimax_rmse = float(np.sqrt(mean_squared_error(test_y, arimax_pred)))
        arimax_mape = float(mean_absolute_percentage_error(test_y, arimax_pred))

        if not silent:
            print(f"ARIMAX test RMSE={arimax_rmse:.4f}, MAPE={arimax_mape:.4%}")
    else:
        if not silent:
            print("No exogenous variables found — skipping ARIMAX.")
        arimax_res = None
        arimax_order = None
        arimax_rmse = None
        arimax_mape = None

    # Save artifacts
    # Save statsmodels result objects using their save() method
    # Save ARIMA (univariate) as baseline file
    arima_res.save("arima_result.pickle")
    meta = {
        "arima_order": arima_order,
        "exog_cols": exog_candidates,
        "arimax_order": arimax_order,
    }
    joblib.dump(meta, MODEL_META)
    if arimax_res is not None:
        arimax_res.save(STATSRESULT_FILE)

    # Save report JSON
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

    if not silent:
        print("Training complete. Artifacts saved:")
        print(" -", MODEL_META)
        print(" -", "arima_result.pickle")
        if arimax_res is not None:
            print(" -", STATSRESULT_FILE)
        print(" -", REPORT_JSON)

    return report

if __name__ == "__main__":
    # CLI usage
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="soil_moisture_training.csv")
    args = parser.parse_args()
    r = train_and_save(csv_path=args.csv, silent=False)
    print("Report:", r)