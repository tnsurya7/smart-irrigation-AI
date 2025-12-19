import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import warnings
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import json
from datetime import datetime

warnings.filterwarnings('ignore')

def check_stationarity(timeseries):
    """Check if time series is stationary using Augmented Dickey-Fuller test"""
    result = adfuller(timeseries)
    print('ADF Statistic:', result[0])
    print('p-value:', result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value}')
    
    if result[1] <= 0.05:
        print("Series is stationary")
        return True
    else:
        print("Series is not stationary")
        return False

def find_best_arima_params(data, max_p=5, max_d=2, max_q=5):
    """Find best ARIMA parameters using AIC"""
    best_aic = float('inf')
    best_params = None
    
    print("Searching for best ARIMA parameters...")
    
    for p in range(max_p + 1):
        for d in range(max_d + 1):
            for q in range(max_q + 1):
                try:
                    model = ARIMA(data, order=(p, d, q))
                    fitted_model = model.fit()
                    aic = fitted_model.aic
                    
                    if aic < best_aic:
                        best_aic = aic
                        best_params = (p, d, q)
                        
                    print(f"ARIMA({p},{d},{q}) - AIC: {aic:.2f}")
                    
                except:
                    continue
    
    print(f"\nBest ARIMA parameters: {best_params} with AIC: {best_aic:.2f}")
    return best_params

def train_arima_model():
    """Train ARIMA model on soil moisture data"""
    
    # Load data
    print("Loading soil moisture data...")
    df = pd.read_csv('soil_moisture_arima.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    print(f"Data loaded: {len(df)} rows")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"Soil moisture range: {df['soil_moisture'].min():.2f}% to {df['soil_moisture'].max():.2f}%")
    
    # Prepare time series
    ts = df['soil_moisture']
    
    # Check stationarity
    print("\nChecking stationarity...")
    is_stationary = check_stationarity(ts)
    
    # Split data for training and testing (80-20 split)
    train_size = int(len(ts) * 0.8)
    train_data = ts[:train_size]
    test_data = ts[train_size:]
    
    print(f"\nTraining data: {len(train_data)} points")
    print(f"Testing data: {len(test_data)} points")
    
    # Find best parameters
    best_params = find_best_arima_params(train_data)
    
    # Train final model with best parameters
    print(f"\nTraining ARIMA{best_params} model...")
    model = ARIMA(train_data, order=best_params)
    fitted_model = model.fit()
    
    # Print model summary
    print("\nModel Summary:")
    print(fitted_model.summary())
    
    # Make predictions on test set
    print("\nMaking predictions on test set...")
    predictions = fitted_model.forecast(steps=len(test_data))
    
    # Calculate metrics
    mse = mean_squared_error(test_data, predictions)
    rmse = np.sqrt(mse)
    mape = mean_absolute_percentage_error(test_data, predictions)
    accuracy = 100 - (mape * 100)
    
    print(f"\nModel Performance:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAPE: {mape:.4f}")
    print(f"Accuracy: {accuracy:.2f}%")
    
    # Save model
    print("\nSaving model...")
    joblib.dump(fitted_model, 'arima_model.joblib')
    
    # Save model metadata
    metadata = {
        'model_type': 'ARIMA',
        'parameters': {
            'p': best_params[0],
            'd': best_params[1], 
            'q': best_params[2]
        },
        'training_data_size': len(train_data),
        'test_data_size': len(test_data),
        'metrics': {
            'mse': float(mse),
            'rmse': float(rmse),
            'mape': float(mape),
            'accuracy': float(accuracy)
        },
        'trained_on': datetime.now().isoformat(),
        'data_file': 'soil_moisture_arima.csv',
        'data_range': {
            'start': str(df.index.min()),
            'end': str(df.index.max())
        }
    }
    
    with open('arima_model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Original time series
    plt.subplot(2, 2, 1)
    plt.plot(ts.index, ts.values, label='Original Data', alpha=0.7)
    plt.axvline(x=ts.index[train_size], color='red', linestyle='--', label='Train/Test Split')
    plt.title('Soil Moisture Time Series')
    plt.xlabel('Date')
    plt.ylabel('Soil Moisture (%)')
    plt.legend()
    plt.xticks(rotation=45)
    
    # Plot 2: Predictions vs Actual
    plt.subplot(2, 2, 2)
    test_dates = test_data.index
    plt.plot(test_dates, test_data.values, label='Actual', marker='o', markersize=3)
    plt.plot(test_dates, predictions, label='Predicted', marker='s', markersize=3)
    plt.title('ARIMA Predictions vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Soil Moisture (%)')
    plt.legend()
    plt.xticks(rotation=45)
    
    # Plot 3: Residuals
    plt.subplot(2, 2, 3)
    residuals = test_data.values - predictions
    plt.plot(test_dates, residuals, marker='o', markersize=3)
    plt.axhline(y=0, color='red', linestyle='--')
    plt.title('Prediction Residuals')
    plt.xlabel('Date')
    plt.ylabel('Residual')
    plt.xticks(rotation=45)
    
    # Plot 4: Model diagnostics
    plt.subplot(2, 2, 4)
    plt.hist(residuals, bins=20, alpha=0.7, edgecolor='black')
    plt.title('Residuals Distribution')
    plt.xlabel('Residual Value')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('arima_model_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Make future predictions
    print("\nMaking future predictions...")
    future_steps = 24  # Predict next 24 time points
    future_predictions = fitted_model.forecast(steps=future_steps)
    
    # Create future timestamps
    last_timestamp = df.index[-1]
    freq = pd.infer_freq(df.index)
    if freq is None:
        # Calculate average time difference
        time_diff = (df.index[-1] - df.index[-2])
        future_timestamps = pd.date_range(
            start=last_timestamp + time_diff,
            periods=future_steps,
            freq=time_diff
        )
    else:
        future_timestamps = pd.date_range(
            start=last_timestamp,
            periods=future_steps + 1,
            freq=freq
        )[1:]
    
    # Save future predictions
    future_df = pd.DataFrame({
        'timestamp': future_timestamps,
        'predicted_soil_moisture': future_predictions
    })
    future_df.to_csv('arima_future_predictions.csv', index=False)
    
    print(f"Future predictions saved to 'arima_future_predictions.csv'")
    print(f"Next prediction: {future_predictions.iloc[0]:.2f}%")
    
    return fitted_model, metadata

if __name__ == "__main__":
    print("=== ARIMA Model Training ===")
    model, metadata = train_arima_model()
    print("\n=== Training Complete ===")
    print("Files created:")
    print("- arima_model.joblib (trained model)")
    print("- arima_model_metadata.json (model info)")
    print("- arima_model_analysis.png (visualizations)")
    print("- arima_future_predictions.csv (future predictions)")