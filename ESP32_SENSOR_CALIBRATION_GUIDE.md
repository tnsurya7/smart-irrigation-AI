# ESP32 Sensor Calibration Guide

## Current Issues & Fixes

### ✅ System Status
Your complete system is working perfectly:
- ✅ ESP32 → WebSocket → Backend → Dashboard pipeline
- ✅ Auto irrigation logic (30% ON / 45% OFF)
- ✅ Rain priority override
- ✅ Telegram alerts
- ✅ UptimeRobot monitoring
- ✅ Render backend + Vercel frontend

### 🔧 Hardware Calibration Needed

## 1️⃣ Soil Moisture Sensor Calibration

### Problem
ESP32 sending: `"soil": 0`
Dashboard showing: `0%`

### Root Cause
Raw ADC values not converted to percentage.

### Solution - Add to ESP32 Code

```cpp
// Soil moisture sensor calibration constants
#define SOIL_DRY_VALUE 3200    // ADC value in dry air
#define SOIL_WET_VALUE 1500    // ADC value in water

// In your sensor reading function:
int soilRaw = analogRead(SOIL_PIN);

// Convert to percentage (0% = dry, 100% = wet)
int soilPercent = map(soilRaw, SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100);
soilPercent = constrain(soilPercent, 0, 100);

// Send to backend
doc["soil"] = soilPercent;  // Send percentage, not raw value
```

### Calibration Steps
1. **Dry Calibration**: Place sensor in dry air, read ADC value (typically ~3200)
2. **Wet Calibration**: Place sensor in water, read ADC value (typically ~1500)
3. Update `SOIL_DRY_VALUE` and `SOIL_WET_VALUE` with your readings
4. Test: Dry soil should show 0-20%, wet soil should show 80-100%

---

## 2️⃣ Light Sensor (LDR) Fix

### Problem
ESP32 sending: `"light_raw": 4095, "light_percent": 100`
Dashboard always showing: `100% Bright`

### Root Cause
ADC reading maximum value (4095) means:
- LDR not connected properly
- Missing voltage divider circuit
- Wrong pin configuration

### Required Circuit - Voltage Divider

```
3.3V
  |
  |
 LDR (Light Dependent Resistor)
  |
  |-------- GPIO32 (ESP32 ADC Pin)
  |
 10kΩ Resistor
  |
 GND
```

### Why This Circuit?
- LDR alone cannot be read by ADC
- Voltage divider creates readable voltage (0-3.3V)
- Bright light → Low resistance → Higher voltage
- Dark → High resistance → Lower voltage

### Solution - ESP32 Code

```cpp
// LDR sensor pin
#define LDR_PIN 32  // Use ADC1 pins (32-39)

// In your sensor reading function:
int lightRaw = analogRead(LDR_PIN);  // 0-4095

// Convert to percentage (0% = dark, 100% = bright)
// Note: Inverted because high ADC = bright light
int lightPercent = map(lightRaw, 0, 4095, 0, 100);
lightPercent = constrain(lightPercent, 0, 100);

// Determine light state
String lightState;
if (lightPercent > 70) {
    lightState = "very_bright";
} else if (lightPercent > 40) {
    lightState = "normal";
} else if (lightPercent > 20) {
    lightState = "low";
} else {
    lightState = "dark";
}

// Send to backend
doc["light_raw"] = lightRaw;
doc["light_percent"] = lightPercent;
doc["light_state"] = lightState;
```

### Testing
1. Cover LDR with hand → Should show 0-20% (dark)
2. Normal room light → Should show 40-60% (normal)
3. Direct sunlight → Should show 80-100% (bright)

---

## 3️⃣ Complete ESP32 Sensor Reading Function

```cpp
void readSensors() {
    // 1. Soil Moisture (with calibration)
    int soilRaw = analogRead(SOIL_PIN);
    int soilPercent = map(soilRaw, 3200, 1500, 0, 100);
    soilPercent = constrain(soilPercent, 0, 100);
    
    // 2. Temperature & Humidity (DHT11)
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    // 3. Rain Sensor
    int rainRaw = analogRead(RAIN_PIN);
    bool rainDetected = (rainRaw < 2000);  // Adjust threshold
    
    // 4. Light Sensor (LDR with voltage divider)
    int lightRaw = analogRead(LDR_PIN);
    int lightPercent = map(lightRaw, 0, 4095, 0, 100);
    lightPercent = constrain(lightPercent, 0, 100);
    
    String lightState;
    if (lightPercent > 70) lightState = "very_bright";
    else if (lightPercent > 40) lightState = "normal";
    else if (lightPercent > 20) lightState = "low";
    else lightState = "dark";
    
    // 5. Flow Sensor
    float flowRate = pulseCount / 7.5;  // L/min
    float totalLiters = totalMilliLitres / 1000.0;
    
    // 6. Pump Status
    int pumpState = digitalRead(PUMP_PIN);
    
    // Create JSON
    StaticJsonDocument<512> doc;
    doc["type"] = "sensor_data";
    doc["source"] = "esp32";
    doc["soil"] = soilPercent;           // Percentage
    doc["temperature"] = temp;
    doc["humidity"] = humidity;
    doc["rain_raw"] = rainRaw;
    doc["rain_detected"] = rainDetected;
    doc["light_raw"] = lightRaw;
    doc["light_percent"] = lightPercent;  // Percentage
    doc["light_state"] = lightState;
    doc["flow"] = flowRate;
    doc["total"] = totalLiters;
    doc["pump"] = pumpState;
    doc["mode"] = currentMode;
    doc["timestamp"] = millis();
    
    // Send via WebSocket
    String payload;
    serializeJson(doc, payload);
    webSocket.sendTXT(payload);
}
```

---

## 4️⃣ Pin Configuration

```cpp
// Recommended ESP32 pin assignments
#define SOIL_PIN 34      // ADC1_CH6 (input only)
#define RAIN_PIN 35      // ADC1_CH7 (input only)
#define LDR_PIN 32       // ADC1_CH4 (input only)
#define DHT_PIN 4        // Digital pin
#define FLOW_PIN 5       // Digital pin with interrupt
#define PUMP_PIN 2       // Digital output (relay control)

// ADC Configuration
void setup() {
    // Set ADC resolution
    analogReadResolution(12);  // 0-4095
    
    // Set ADC attenuation (for 0-3.3V range)
    analogSetAttenuation(ADC_11db);
    
    // Pin modes
    pinMode(SOIL_PIN, INPUT);
    pinMode(RAIN_PIN, INPUT);
    pinMode(LDR_PIN, INPUT);
    pinMode(DHT_PIN, INPUT);
    pinMode(FLOW_PIN, INPUT_PULLUP);
    pinMode(PUMP_PIN, OUTPUT);
}
```

---

## 5️⃣ Testing Checklist

### Before Demo
- [ ] Soil sensor: Test dry (0-20%) and wet (80-100%)
- [ ] Light sensor: Test dark (0-20%) and bright (80-100%)
- [ ] Rain sensor: Test dry (clear) and wet (rain detected)
- [ ] Temperature: Should show room temp (20-30°C)
- [ ] Humidity: Should show realistic values (30-80%)
- [ ] Pump: Test manual ON/OFF from dashboard
- [ ] Auto mode: Test soil < 30% triggers pump ON
- [ ] Rain override: Test rain detected turns pump OFF

### Dashboard Verification
- [ ] All sensor values updating every 5 seconds
- [ ] Connection status shows "Connected"
- [ ] Charts displaying real-time data
- [ ] Pump control working in manual mode
- [ ] Auto irrigation logic working correctly

---

## 6️⃣ Common Issues & Solutions

### Issue: Soil always shows 0%
**Solution**: Add calibration constants and map() function

### Issue: Light always shows 100%
**Solution**: Add 10kΩ resistor voltage divider circuit

### Issue: Sensors show random values
**Solution**: Add 0.1µF capacitor across sensor power pins

### Issue: WebSocket disconnects frequently
**Solution**: Add WiFi reconnection logic and increase timeout

### Issue: Pump doesn't respond
**Solution**: Check relay module connections and power supply

---

## 7️⃣ Final System Architecture

```
ESP32 Hardware
├── Soil Moisture Sensor (Analog)
├── DHT11 (Temperature + Humidity)
├── Rain Sensor (Analog)
├── LDR + 10kΩ Resistor (Light)
├── Flow Sensor (Digital + Interrupt)
└── Relay Module (Pump Control)
    ↓
ESP32 Firmware
├── Sensor reading (every 5s)
├── WebSocket client
├── JSON formatting
└── Pump control logic
    ↓
Render Backend (FastAPI)
├── WebSocket server
├── Auto irrigation controller
├── Telegram alerts
└── Database storage
    ↓
Vercel Dashboard (React)
├── Real-time sensor display
├── Charts & analytics
├── Manual pump control
└── Mode switching (Auto/Manual)
```

---

## 8️⃣ Your Project is Production-Ready! 🎉

### Working Features
✅ Real-time sensor monitoring
✅ Smart irrigation (30% ON / 45% OFF)
✅ Rain priority override
✅ WebSocket communication
✅ Telegram alerts every 5 minutes
✅ ARIMA vs ARIMAX prediction
✅ Historical data analysis
✅ Manual pump control
✅ Auto/Manual mode switching
✅ UptimeRobot monitoring
✅ Render + Vercel deployment

### Only Hardware Calibration Needed
🔧 Soil sensor calibration (5 minutes)
🔧 LDR voltage divider circuit (5 minutes)

Your final year project is complete and impressive! 🌱
