# sample_data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_rows(n=1000, start_dt=None):
    if start_dt is None:
        start_dt = datetime.now() - timedelta(seconds=n)
    rows = []
    soil = 2000
    for i in range(n):
        ts = (start_dt + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S")
        # random walk soil
        soil += np.random.randint(-20, 20)
        soil = max(200, min(3800, soil))
        temp = 25 + np.random.randn() * 1.2
        hum = 60 + np.random.randn() * 3
        light = int(np.random.uniform(200, 2000))
        rain = int(0 if np.random.rand() > 0.995 else np.random.uniform(0, 1000))
        flow = max(0, np.random.randn() * 0.2 + 0.5)
        rows.append({
            "timestamp": ts,
            "soil": int(soil),
            "temperature": float(round(temp,2)),
            "humidity": float(round(hum,2)),
            "light": int(light),
            "rain": int(rain),
            "flow": float(round(flow,3))
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_rows(600)
    df.to_csv("sensor_data.csv", index=False)
    print("Saved sensor_data.csv with", len(df), "rows")