import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pmdarima.arima import auto_arima

# -----------------------------
# 1. Load Dataset
# -----------------------------
# CSV should have columns: ['date','soil_moisture','rainfall','temperature','humidity']
df = pd.read_csv("soil_moisture_data.csv", parse_dates=['date'], index_col='date')

print("First 5 rows of dataset:")
print(df.head())
print("\nMissing values:\n", df.isnull().sum())

# Fill missing values if any
df = df.fillna(method='ffill')

# Target variable
y = df['soil_moisture']

# Exogenous variables
X = df[['rainfall', 'temperature', 'humidity']]

# -----------------------------
# 2. Train-Test Split
# -----------------------------
train_size = int(len(df) * 0.8)
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]

print(f"\nTrain size: {len(y_train)}, Test size: {len(y_test)}")

# -----------------------------
# 3. Auto ARIMA to select (p,d,q)
# -----------------------------
print("\nRunning auto_arima to select best parameters...")
auto_model = auto_arima(
    y_train, 
    exogenous=X_train,
    seasonal=False,
    stepwise=True,
    trace=True,
    suppress_warnings=True,
    error_action="ignore",
    max_order=10
)

print("\nBest ARIMA order found:", auto_model.order)

# -----------------------------
# 4. Fit ARIMAX Model
# -----------------------------
model = SARIMAX(
    y_train,
    exog=X_train,
    order=auto_model.order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

results = model.fit(disp=False)
print(results.summary())

# -----------------------------
# 5. Forecast
# -----------------------------
forecast = results.get_forecast(steps=len(y_test), exog=X_test)
y_pred = forecast.predicted_mean
conf_int = forecast.conf_int()

# -----------------------------
# 6. Evaluation Metrics
# -----------------------------
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nEvaluation Results:")
print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")

# -----------------------------
# 7. Plots
# -----------------------------
plt.figure(figsize=(12,6))
plt.plot(y_train.index, y_train, label="Train Soil Moisture", color="blue")
plt.plot(y_test.index, y_test, label="Actual Soil Moisture", color="black")
plt.plot(y_test.index, y_pred, label="Predicted Soil Moisture", color="red")
plt.fill_between(y_test.index,
                 conf_int.iloc[:,0],
                 conf_int.iloc[:,1],
                 color='pink', alpha=0.3)
plt.xlabel("Date")
plt.ylabel("Soil Moisture")
plt.title("ARIMAX Soil Moisture Forecast")
plt.legend()
plt.show()

# -----------------------------
# 8. Residual Diagnostics
# -----------------------------
residuals = y_train - results.fittedvalues

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.plot(residuals, label="Residuals")
plt.axhline(0, linestyle="--", color="red")
plt.legend()

plt.subplot(1,2,2)
sns.histplot(residuals, kde=True, bins=20)
plt.title("Residual Distribution")
plt.show()

# -----------------------------
# 9. Model Diagnostics
# -----------------------------
results.plot_diagnostics(figsize=(12,8))
plt.show()