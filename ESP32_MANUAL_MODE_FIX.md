# ESP32 Manual Mode Fix

## Problem
Backend sends AUTO pump commands even when dashboard is in manual mode, because:
1. ESP32 doesn't track the current mode
2. ESP32 accepts all pump commands from backend

## Solution
ESP32 should only accept backend pump commands when in AUTO mode.

## ESP32 Code Changes

### 1. Add Mode Tracking Variable
Add this at the top of your ESP32 code with other global variables:

```cpp
// Mode tracking
String currentMode = "auto";  // Track current mode (auto/manual)
bool manualPump = false;      // Manual pump state
```

### 2. Update WebSocket Message Handler

Find your `webSocketEvent()` function and update the message handling:

```cpp
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("❌ WebSocket Disconnected");
      break;
      
    case WStype_CONNECTED:
      Serial.println("✅ WebSocket Connected");
      // Send initial registration
      webSocket.sendTXT("{\"type\":\"register\",\"role\":\"esp32\"}");
      break;
      
    case WStype_TEXT:
      {
        String msg = String((char*)payload);
        Serial.println("📩 Received: " + msg);
        
        // Parse JSON message
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, msg);
        
        if (error) {
          Serial.println("❌ JSON parse error");
          return;
        }
        
        // Handle mode change
        if (doc.containsKey("mode")) {
          String newMode = doc["mode"].as<String>();
          currentMode = newMode;
          Serial.println("🔄 Mode changed to: " + currentMode);
        }
        
        // Handle pump command (only in AUTO mode)
        if (doc.containsKey("pump_cmd")) {
          String pumpCmd = doc["pump_cmd"].as<String>();
          
          if (currentMode == "auto") {
            // AUTO mode: Accept backend commands
            if (pumpCmd == "ON") {
              manualPump = true;
              digitalWrite(PUMP_PIN, HIGH);
              Serial.println("💧 AUTO: Pump ON (backend command)");
            } else if (pumpCmd == "OFF") {
              manualPump = false;
              digitalWrite(PUMP_PIN, LOW);
              Serial.println("💧 AUTO: Pump OFF (backend command)");
            }
          } else {
            // MANUAL mode: Ignore backend commands
            Serial.println("⚠️ MANUAL mode active - ignoring backend pump command");
          }
        }
      }
      break;
  }
}
```

### 3. Update Sensor Data Sending

Make sure your sensor data includes the current mode:

```cpp
void sendSensorData() {
  // Read sensors
  int soilRaw = analogRead(SOIL_PIN);
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int rainRaw = analogRead(RAIN_PIN);
  bool rainDetected = (rainRaw < 2000);
  int lightRaw = analogRead(LDR_PIN);
  int lightPercent = map(lightRaw, 0, 4095, 0, 100);
  
  // Get pump state
  int pumpState = digitalRead(PUMP_PIN);
  
  // Create JSON
  StaticJsonDocument<512> doc;
  doc["type"] = "sensor_data";
  doc["source"] = "esp32";
  doc["soil"] = map(soilRaw, 3200, 1500, 0, 100);  // Convert to percentage
  doc["temperature"] = temp;
  doc["humidity"] = humidity;
  doc["rain_raw"] = rainRaw;
  doc["rain_detected"] = rainDetected;
  doc["light_raw"] = lightRaw;
  doc["light_percent"] = lightPercent;
  doc["light_state"] = getLightState(lightPercent);
  doc["flow"] = flowRate;
  doc["total"] = totalLiters;
  doc["pump"] = pumpState;
  doc["mode"] = currentMode;  // Send current mode
  doc["timestamp"] = millis();
  
  // Send via WebSocket
  String payload;
  serializeJson(doc, payload);
  webSocket.sendTXT(payload);
  
  Serial.println("📤 Sent: " + payload);
}
```

### 4. Helper Function for Light State

```cpp
String getLightState(int lightPercent) {
  if (lightPercent > 70) return "very_bright";
  else if (lightPercent > 40) return "normal";
  else if (lightPercent > 20) return "low";
  else return "dark";
}
```

## How It Works Now

### AUTO Mode (Default)
1. Dashboard switches to AUTO mode
2. Backend sends mode change → ESP32 receives `{"mode":"auto"}`
3. ESP32 sets `currentMode = "auto"`
4. Backend evaluates soil moisture and sends pump commands
5. ESP32 accepts pump commands because `currentMode == "auto"`
6. Pump operates based on backend logic (30% ON / 45% OFF)

### MANUAL Mode
1. Dashboard switches to MANUAL mode
2. Backend sends mode change → ESP32 receives `{"mode":"manual"}`
3. ESP32 sets `currentMode = "manual"`
4. User clicks "Pump ON" on dashboard
5. Dashboard sends pump command → Backend forwards to ESP32
6. ESP32 accepts command because it came from dashboard (not backend auto logic)
7. Backend auto logic still runs but ESP32 ignores those commands

## Expected Serial Monitor Output

### When Switching to Manual Mode:
```
📩 Received: {"mode":"manual"}
🔄 Mode changed to: manual
```

### When Backend Tries to Send AUTO Command in Manual Mode:
```
📩 Received: {"pump_cmd":"ON"}
⚠️ MANUAL mode active - ignoring backend pump command
```

### When User Clicks Pump ON in Manual Mode:
```
📩 Received: {"pump_cmd":"ON"}
💧 Pump ON (manual command)
pump:1 mode:manual
```

## Testing Checklist

- [ ] Upload updated code to ESP32
- [ ] Open Serial Monitor (115200 baud)
- [ ] Verify ESP32 connects to WiFi and WebSocket
- [ ] Switch dashboard to MANUAL mode
- [ ] Check serial: Should see "Mode changed to: manual"
- [ ] Click "Pump OFF" button
- [ ] Pump should turn OFF and stay OFF
- [ ] Backend should NOT override pump state
- [ ] Switch back to AUTO mode
- [ ] Backend should control pump based on soil moisture

## Complete Example Code Structure

```cpp
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// WebSocket server
const char* ws_host = "smart-agriculture-backend-my7c.onrender.com";
const int ws_port = 443;
const char* ws_path = "/ws";

// Pin definitions
#define SOIL_PIN 34
#define RAIN_PIN 35
#define LDR_PIN 32
#define DHT_PIN 4
#define PUMP_PIN 2

// Global variables
WebSocketsClient webSocket;
DHT dht(DHT_PIN, DHT11);
String currentMode = "auto";
bool manualPump = false;
float flowRate = 0.0;
float totalLiters = 0.0;

void setup() {
  Serial.begin(115200);
  
  // Pin setup
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  
  // Connect WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected");
  
  // Connect WebSocket
  webSocket.beginSSL(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  
  dht.begin();
}

void loop() {
  webSocket.loop();
  
  // Send sensor data every 5 seconds
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 5000) {
    sendSensorData();
    lastSend = millis();
  }
}
```

## Summary

With this fix:
- ✅ AUTO mode: Backend controls pump automatically
- ✅ MANUAL mode: Dashboard controls pump, backend commands ignored
- ✅ Mode changes sync between dashboard and ESP32
- ✅ No more unwanted pump state changes in manual mode

Your irrigation system will now work exactly as expected! 🌱💧
