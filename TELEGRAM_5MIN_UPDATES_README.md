# 5-Minute Telegram Updates System

## Overview
Automated Telegram updates every 5 minutes with **STRICT REAL DATA ONLY** policy for Smart Agriculture monitoring.

## 🎯 Key Features

### ✅ Real Data Policy
- **ESP32 Online**: Shows live sensor values
- **ESP32 Offline**: Shows "OFFLINE" status, no fake values
- **Weather**: Always from OpenWeather API
- **Transparency**: All data sources clearly labeled

### ⏰ Update Schedule
- **Frequency**: Every 5 minutes
- **Scheduler**: APScheduler (Render compatible)
- **Timezone**: IST (Asia/Kolkata)
- **Job Name**: `telegram_farm_update`

### 📡 ESP32 Online Detection
- **Threshold**: 120 seconds (2 minutes)
- **Tracking**: Last heartbeat timestamp
- **Sources**: WebSocket + API endpoints
- **Status**: Online/Offline with last seen time

## 📱 Message Format

```
📈 SMART AGRICULTURE UPDATE (5-Min)

🌤️ Weather (OpenWeather)
• Location: Erode
• Temperature: 29°C
• Humidity: 68%
• Condition: Clear Sky
• Rain Probability: 15%

📡 Live Sensors:
• Status: 🟢 ONLINE / 🔴 OFFLINE
• Soil Moisture: 45.2% (if online)
• Temperature: 28.5°C (if online)
• Humidity: 72.0% (if online)
• Light: 68.0% (normal) (if online)
• Rain Detected: ☀️ No (if online)

📊 System Status
• Pump: 🔴 OFF
• Mode: AUTO
• Water Used: 125.5 L
• ARIMAX: 🟢 ACTIVE

🌧️ RAIN ALERT (if rain probability > 60%)
• High rain probability: 75%
• Recommendation: Skip irrigation

📡 Data Sources:
• Weather: OpenWeather API
• Sensors: ESP32 (online/offline)
• Prediction: ARIMAX

⏰ Report Time: 14:30:15 IST
```

## 🔧 Technical Implementation

### Files Structure
```
backend/
├── telegram_5min_updates.py     # Main system
├── production_backend.py        # Integration
└── telegram_bot.py             # Manual commands

test_5min_telegram_updates.py    # Comprehensive tests
test_message_format.py           # Format validation
```

### Environment Variables Required
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OPENWEATHER_API_KEY=your_weather_key
```

### Integration Points
1. **Sensor Data Endpoint**: `/sensor-data` - Registers ESP32 heartbeat
2. **WebSocket**: `/ws` - Registers ESP32 heartbeat on sensor_data messages
3. **Startup Event**: Auto-starts 5-minute scheduler
4. **Status Endpoint**: `/api/esp32-status` - Debug ESP32 status

## 🚨 Strict Rules Enforced

### ❌ NEVER Show When ESP32 Offline:
- Soil moisture values
- Temperature values  
- Humidity values
- Light values
- Rain sensor values

### ✅ ALWAYS Show:
- ESP32 online/offline status
- Last ESP32 update time
- OpenWeather API data
- Pump status and mode
- Data source transparency

### 🌧️ Rain Alert Triggers:
- OpenWeather rain probability > 60%
- Clear recommendation to skip irrigation
- No reliance on offline ESP32 rain sensor

## 🧪 Testing

### Run Format Tests
```bash
python3 test_message_format.py
```

### Run Comprehensive Tests (requires dependencies)
```bash
python3 test_5min_telegram_updates.py
```

### Manual Testing
1. Check ESP32 status: `GET /api/esp32-status`
2. Send sensor data: `POST /sensor-data`
3. Monitor Telegram for updates

## 📊 Monitoring & Debugging

### Logs to Watch
```
✅ 5-minute Telegram update system started successfully
📱 Updates every 5 minutes with real data only
📡 ESP32 online tracking: 120 second threshold
🌤️ Weather from OpenWeather API
ESP32 heartbeat registered for 5-min updates
✅ 5-minute farm update sent successfully
```

### Status Checks
- **ESP32 Status**: `/api/esp32-status`
- **Health Check**: `/health/detailed`
- **Telegram Logs**: Check for successful message sends

## 🚀 Deployment

### Render Deployment
1. Push to GitHub main branch
2. Render auto-deploys backend
3. 5-minute updates start automatically
4. Check logs for successful startup

### Environment Setup
All credentials configured in Render environment variables (not in code).

## 🎯 Expected Results

### When ESP32 Online:
- Real sensor values displayed
- Status shows "🟢 ONLINE"
- Full farm monitoring data

### When ESP32 Offline:
- Status shows "🔴 OFFLINE"
- Last seen timestamp
- "Sensor Values: Not available"
- Weather data still available

### Rain Alerts:
- Triggered at >60% rain probability
- Clear irrigation recommendations
- Based on OpenWeather forecast

## 🔒 Security & Reliability

- **No Hardcoded Credentials**: All from environment variables
- **Error Handling**: Graceful failures, system continues
- **Rate Limiting**: 5-minute intervals prevent spam
- **Data Validation**: Strict online/offline checks
- **Transparency**: Always show data sources

## 📈 Success Metrics

✅ **Accuracy**: Only real data shown  
✅ **Transparency**: Data sources always labeled  
✅ **Reliability**: Updates every 5 minutes  
✅ **Honesty**: ESP32 offline status clear  
✅ **Usefulness**: Weather always available  

This system provides farmers with accurate, real-time updates while maintaining complete transparency about data sources and system status.