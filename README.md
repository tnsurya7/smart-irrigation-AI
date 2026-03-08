# 🌱 Smart Irrigation AI - Agriculture Dashboard

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/tnsurya7/smart-irrigation-AI)
[![React](https://img.shields.io/badge/React-19.2.3-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-orange.svg)](https://supabase.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

## 🚀 Production-Ready Smart Agriculture Dashboard

A comprehensive IoT-based smart irrigation system with AI-powered predictions, real-time monitoring, and automated control. Built for production deployment with modern cloud infrastructure.

---

## 📊 **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │     BACKEND      │    │    DATABASE     │
│   (Vercel)      │◄──►│    (Render)      │◄──►│   (Supabase)    │
│                 │    │                  │    │                 │
│ • React + TS    │    │ • FastAPI        │    │ • PostgreSQL    │
│ • Real-time UI  │    │ • WebSocket      │    │ • Real-time     │
│ • PWA Ready     │    │ • Auto-scaling   │    │ • Row Security  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐            │
         │              │   INTEGRATIONS   │            │
         │              │                  │            │
         └──────────────►│ • ESP32 Device  │◄───────────┘
                        │ • OpenWeather   │
                        │ • Telegram Bot  │
                        │ • n8n Webhook   │
                        └──────────────────┘
```

---

## ✨ **Key Features**

### 🌡️ **Real-time Monitoring**
- **ESP32 Integration**: Live sensor data (soil moisture, temperature, humidity, light, rain)
- **WebSocket Streaming**: Real-time dashboard updates
- **Offline Mode**: Graceful handling when ESP32 disconnected
- **Historical Data**: 30-day trend analysis with interactive charts

### 🤖 **AI-Powered Predictions**
- **ARIMA Model**: Time series forecasting (82.5% accuracy)
- **ARIMAX Model**: Enhanced predictions with external factors (94.6% accuracy)
- **Auto-retraining**: Daily model updates with new sensor data
- **Performance Metrics**: Real-time accuracy, RMSE, and MAPE tracking

### 💧 **Smart Irrigation Control**
- **Automated Irrigation**: AI-driven watering decisions
- **Manual Override**: Remote pump control via dashboard
- **Weather Integration**: Rain detection and forecast-based scheduling
- **Water Usage Tracking**: Flow rate and total consumption monitoring

### 📱 **Telegram Bot Integration**
- **Daily Reports**: Weather (7 AM) and dashboard summaries (6 PM)
- **Interactive Commands**: Weather, dashboard, pump control
- **Rain Alerts**: Automatic notifications for weather changes
- **Remote Control**: Pump on/off commands via Telegram

### 🌤️ **Weather Intelligence**
- **OpenWeather API**: Live weather data for Erode, Tamil Nadu
- **Rain Forecasting**: 24-hour precipitation probability
- **Weather-based Decisions**: Automatic irrigation adjustments
- **Climate Monitoring**: Temperature, humidity, and atmospheric pressure

---

## 🛠️ **Tech Stack**

### **Frontend**
- **React 19** + **TypeScript** + **Vite**
- **Tailwind CSS** for responsive design
- **Recharts** for data visualization
- **WebSocket** for real-time updates
- **PWA** capabilities for mobile use

### **Backend**
- **FastAPI** for high-performance API
- **WebSocket** for real-time communication
- **Supabase** PostgreSQL database
- **Pydantic** for data validation
- **Uvicorn** ASGI server

### **AI & Data Science**
- **ARIMA/ARIMAX** time series models
- **Statsmodels** for statistical analysis
- **Scikit-learn** for model evaluation
- **Pandas** for data processing
- **NumPy** for numerical computations

### **Infrastructure**
- **Vercel** for frontend hosting
- **Render** for backend services
- **Supabase** for database and real-time features
- **GitHub Actions** for CI/CD (optional)

### **External Integrations**
- **ESP32** microcontroller for sensors
- **OpenWeather API** for weather data
- **Telegram Bot API** for notifications
- **n8n** for workflow automation

---

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm
- Python 3.11+
- Supabase account
- OpenWeather API key
- Telegram bot token

### **1. Clone Repository**
```bash
git clone https://github.com/tnsurya7/smart-irrigation-AI.git
cd smart-irrigation-AI
```

### **2. Environment Setup**
```bash
# Copy environment template
cp .env.example .env.local

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### **3. Configure Environment Variables**
Update `.env.local` with your credentials:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8080/ws
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_OPENWEATHER_API_KEY=your-openweather-key
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
```

### **4. Database Setup**
1. Create Supabase project
2. Run SQL schema: `database/supabase-schema.sql`
3. Configure Row Level Security

### **5. Run Development Servers**
```bash
# Frontend (Terminal 1)
npm run dev

# Backend API (Terminal 2)
cd backend && python production_backend.py

# WebSocket Server (Terminal 3)
cd backend && python production_websocket.py

# Telegram Bot (Terminal 4)
python telegram_bot_simple.py
```

### **6. Access Dashboard**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8080/ws

---

## 📦 **Production Deployment**

### **Automated Deployment**
The project includes complete production deployment configurations:

- **Frontend**: Deploy to Vercel with `vercel.json`
- **Backend**: Deploy to Render with `render.yaml`
- **Database**: Supabase with production schema
- **Monitoring**: Health checks and logging

### **Deployment Guide**
Follow the comprehensive deployment guide: [`PRODUCTION_DEPLOYMENT.md`](./PRODUCTION_DEPLOYMENT.md)

### **Security Checklist**
Review security requirements: [`SECURITY_CHECKLIST.md`](./SECURITY_CHECKLIST.md)

---

## 📊 **Dashboard Features**

### **Real-time Monitoring Cards**
- 🌡️ **Temperature**: Current temperature with status indicators
- 💨 **Humidity**: Atmospheric humidity levels
- 💧 **Soil Moisture**: Real-time soil moisture percentage
- ☀️ **Light Sensor**: Ambient light levels and day/night detection
- 🌧️ **Rain Sensor**: Precipitation detection and raw values

### **Control Panel**
- 🚿 **Irrigation Control**: Auto/manual mode switching
- 🔄 **Pump Status**: Real-time pump operation status
- 💦 **Flow Monitoring**: Water flow rate and total consumption
- ⚙️ **System Settings**: Mode configuration and scheduling

### **Analytics Dashboard**
- 📈 **Historical Trends**: 1-day, 7-day, 30-day data visualization
- 🎯 **Model Performance**: ARIMA vs ARIMAX accuracy comparison
- 📊 **Irrigation Events**: Automated and manual irrigation history
- 🌦️ **Weather Correlation**: Weather impact on irrigation decisions

### **External Weather Panel**
- 🌤️ **Current Weather**: Live data from OpenWeather API
- 🌧️ **Rain Forecast**: 24-hour precipitation probability
- 📍 **Location**: Erode, Tamil Nadu weather monitoring
- ⏰ **Updates**: Real-time weather data refresh

---

## 🤖 **ESP32 Integration**

### **Sensor Configuration**
```cpp
// ESP32 sensor pins
#define SOIL_MOISTURE_PIN A0
#define TEMPERATURE_PIN 2
#define HUMIDITY_PIN 3
#define RAIN_SENSOR_PIN A1
#define LIGHT_SENSOR_PIN A2
#define PUMP_RELAY_PIN 4
#define FLOW_SENSOR_PIN 5
```

### **WebSocket Protocol**
```json
{
  "source": "esp32",
  "soil": 65.5,
  "temperature": 28.3,
  "humidity": 72.1,
  "rain_raw": 3800,
  "rain_detected": false,
  "light_raw": 450,
  "light_percent": 75.2,
  "light_state": "normal",
  "flow": 2.5,
  "total": 125.8,
  "pump": 1,
  "mode": "auto",
  "rain_expected": false
}
```

### **Commands from Dashboard**
```json
// Pump control
{"pump_cmd": "ON"}
{"pump_cmd": "OFF"}

// Mode change
{"mode": "auto"}
{"mode": "manual"}

// Rain forecast
{"rain_expected": true}
```

---

## 📱 **Telegram Bot Commands**

### **Interactive Commands**
- `/start` - Initialize bot and show welcome message
- `weather` - Get current weather report for Erode
- `dashboard` - View real-time sensor data and system status
- `pump on` - Turn irrigation pump ON remotely
- `pump off` - Turn irrigation pump OFF remotely
- `help` - Show all available commands

### **Automated Reports**
- **07:00 AM**: Daily weather report with rain alerts
- **06:00 PM**: Daily dashboard summary with sensor data

### **Sample Bot Responses**
```
🌤️ Weather Report - Erode, Tamil Nadu

🌡️ Temperature: 28.3°C
💨 Humidity: 72%
🌧️ Rain Probability: 15%
☁️ Condition: Clear Sky
💨 Wind Speed: 2.1 m/s

🌧️ Rain Alert: ✅ No Rain Expected
```

---

## 🔧 **API Endpoints**

### **Sensor Data**
- `GET /sensor-data/latest` - Get latest sensor readings
- `POST /sensor-data` - Store new sensor data
- `GET /sensor-data/range` - Get data for date range

### **Model Metrics**
- `GET /model-metrics` - Get ARIMA/ARIMAX performance
- `POST /model-metrics` - Update model performance

### **Weather Data**
- `GET /weather` - Get current weather from OpenWeather API

### **System Status**
- `GET /health` - Health check endpoint
- `GET /system-status` - Get system component status
- `POST /system-status` - Update component status

### **Irrigation Events**
- `GET /irrigation-events` - Get irrigation history
- `POST /irrigation-events` - Log irrigation event

---

## 📈 **Performance Metrics**

### **AI Model Accuracy**
- **ARIMA Model**: 82.5% accuracy, 3.45 RMSE, 17.5% MAPE
- **ARIMAX Model**: 94.6% accuracy, 1.78 RMSE, 5.4% MAPE
- **Training Data**: 7,000+ sensor readings
- **Retraining**: Automatic daily updates

### **System Performance**
- **Response Time**: < 200ms API responses
- **WebSocket Latency**: < 50ms real-time updates
- **Uptime**: 99.9% availability target
- **Data Retention**: 30 days sensor data, 90 days events

### **Resource Usage**
- **Database**: Optimized queries with indexes
- **Memory**: Efficient data structures and caching
- **Network**: Compressed WebSocket messages
- **Storage**: Automated cleanup of old data

---

## 🛡️ **Security Features**

### **Data Protection**
- ✅ Environment variables for all secrets
- ✅ HTTPS/WSS encryption in production
- ✅ Database Row Level Security (RLS)
- ✅ Input validation and sanitization
- ✅ No hardcoded credentials

### **Network Security**
- ✅ CORS restrictions to specific domains
- ✅ Rate limiting on API endpoints
- ✅ WebSocket authentication
- ✅ Trusted host middleware
- ✅ Security headers implementation

### **Authentication**
- ✅ Admin authentication for dashboard
- ✅ API key validation for external services
- ✅ Session management
- ✅ Secure logout functionality

---

## 📚 **Documentation**

- **[Production Deployment Guide](./PRODUCTION_DEPLOYMENT.md)** - Complete deployment instructions
- **[Security Checklist](./SECURITY_CHECKLIST.md)** - Security requirements and best practices
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation
- **[Database Schema](./database/supabase-schema.sql)** - Complete database structure

---

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### **Code Standards**
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **Python**: PEP 8 style guide
- **Testing**: Unit tests for critical functions

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 **Team**

**Final Year Project 2025-2026**  
**Department of Computer Science and Engineering**

- **MONIKA M** - Frontend Development & UI/UX Design
- **SURYA KUMAR M** - Backend Development & AI Models  
- **KARAN M** - Hardware Integration & ESP32 Programming

**Project Guide**: [Mr.V.Gopinath]  
**Institution**: [KSR Institute for Engineering and Technology]

---

## 🙏 **Acknowledgments**

- **OpenWeather API** for weather data services
- **Supabase** for database and real-time features
- **Vercel** and **Render** for hosting infrastructure
- **React** and **FastAPI** communities for excellent frameworks
- **ESP32** community for hardware integration resources

---

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=tnsurya7/smart-irrigation-AI&type=Date)](https://star-history.com/#tnsurya7/smart-irrigation-AI&Date)

---


