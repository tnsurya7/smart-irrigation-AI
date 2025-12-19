# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start the Backend (Python ARIMAX API)

**macOS/Linux:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Windows:**
```bash
start_backend.bat
```

**Manual Start:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python sample_data_generator.py

# Train models
python train_arimax.py --csv sensor_data.csv

# Start backend
python backend.py
```

The backend will start at `http://localhost:8000`

### Step 2: Start the Frontend (React Dashboard)

In a new terminal:

```bash
npm install
npm run dev
```

The dashboard will start at `http://localhost:3000`

### Step 3: Connect ESP32 (Optional)

If you have an ESP32 with sensors:

1. Update the WebSocket URL in `hooks/useSmartFarmData.ts`:
   ```typescript
   const WS_URL = 'ws://YOUR_ESP32_IP:8080';
   ```

2. Ensure your ESP32 sends data in this format:
   ```json
   {
     "type": "sensors",
     "soil": 1300,
     "rain": 500,
     "light": 1600,
     "temperature": 29.3,
     "humidity": 60.2,
     "flowRate": 1.23,
     "totalLiters": 5.678,
     "pump": 1
   }
   ```

## 🎯 What You'll See

### Dashboard Features

1. **Connection Status** - 🟢 Connected / 🔴 Disconnected
2. **Auto Irrigation Status** - ON/OFF indicator
3. **Real-time Sensor Cards**:
   - Temperature (°C)
   - Humidity (%)
   - Soil Moisture (%) with color coding
   - Sunlight (lux)
   - Rain sensor status
4. **Irrigation Control Card**:
   - Manual Pump ON/OFF buttons
   - Auto irrigation toggle
   - Flow rate (L/min)
   - Total water consumed (L)
   - Runtime statistics
5. **Historical Charts** - Last 30 readings
6. **Forecast Card** - ARIMAX predictions for next 30 minutes
7. **Model Accuracy** - ARIMA vs ARIMAX comparison

### Auto Irrigation Logic

The system automatically controls the pump based on soil moisture:

- **Soil < 20%**: Pump turns ON (critical dry)
- **Soil > 70%**: Pump turns OFF (sufficiently wet)
- **Soil 50-60%**: 2-second watering cycle (maintenance)

You can override with manual controls or disable auto mode.

## 🔧 API Endpoints

Test the backend API:

```bash
# Check health
curl http://localhost:8000/health

# Get predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"steps": 6}'

# Get accuracy
curl http://localhost:8000/accuracy

# Retrain models
curl -X POST http://localhost:8000/train
```

## 📊 Model Training

The system uses two models:

1. **ARIMA** - Univariate (soil moisture only)
2. **ARIMAX** - Multivariate (soil + weather factors)

ARIMAX typically performs better because it considers:
- Temperature
- Humidity
- Rainfall
- Sunlight
- Water flow

To retrain with new data:
```bash
python train_arimax.py --csv data/history.csv
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is free: `lsof -i :8000` (macOS/Linux)

### Frontend won't connect to backend
- Ensure backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify `/health` endpoint: `curl http://localhost:8000/health`

### WebSocket not connecting
- Update `WS_URL` in `hooks/useSmartFarmData.ts`
- Check ESP32 IP address and port
- Ensure ESP32 WebSocket server is running
- Check network connectivity

### No predictions showing
- Train models first: `python train_arimax.py`
- Check backend logs for errors
- Verify data exists: `ls sensor_data.csv`
- Test API: `curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"steps":6}'`

## 📱 Mobile View

The dashboard is fully responsive and works on mobile devices. All charts and controls adapt to smaller screens.

## 🎨 Dark Mode

Toggle dark mode using the sun/moon icon in the header. The preference is saved automatically.

## 🔄 Data Flow

```
ESP32 Sensors → WebSocket → React Dashboard
                                ↓
                          Display + Alerts
                                ↓
                    Auto Irrigation Logic
                                ↓
                    WebSocket Command → ESP32 Pump

Historical Data → CSV → Python Backend
                            ↓
                    ARIMAX Training
                            ↓
                    Predictions → Dashboard
```

## 📈 Next Steps

1. Connect real ESP32 hardware
2. Collect real sensor data
3. Retrain models with actual data
4. Fine-tune irrigation thresholds
5. Add more sensors (pH, EC, etc.)
6. Implement data logging and analytics
7. Add mobile app notifications

## 💡 Tips

- Let the system collect data for a few days before retraining
- Monitor accuracy metrics to see model improvement
- Adjust auto irrigation thresholds based on your crops
- Use manual mode for testing and calibration
- Check alerts regularly for system health

Enjoy your Smart Agriculture Dashboard! 🌱
