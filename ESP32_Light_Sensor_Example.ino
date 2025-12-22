/*
ESP32 Light Sensor (LDR) Integration Example
Add this to your existing ESP32 code to send light sensor data
*/

// Pin definitions
#define LDR_PIN 34  // Analog pin for LDR (Light Dependent Resistor)

// Light sensor variables
int lightRaw = 0;
float lightPercent = 0.0;
String lightState = "dark";

void setup() {
  Serial.begin(115200);
  
  // Initialize LDR pin
  pinMode(LDR_PIN, INPUT);
  
  // Your existing setup code...
}

void readLightSensor() {
  // Read raw ADC value (0-4095 for ESP32)
  lightRaw = analogRead(LDR_PIN);
  
  // Convert to percentage (0-100%)
  lightPercent = map(lightRaw, 0, 4095, 0, 100);
  
  // Determine light state based on percentage
  if (lightPercent >= 80) {
    lightState = "very_bright";
  } else if (lightPercent >= 50) {
    lightState = "normal";
  } else if (lightPercent >= 20) {
    lightState = "low";
  } else {
    lightState = "dark";
  }
  
  // Debug output
  Serial.println("Light Sensor:");
  Serial.println("  Raw: " + String(lightRaw));
  Serial.println("  Percent: " + String(lightPercent) + "%");
  Serial.println("  State: " + lightState);
}

void sendSensorData() {
  // Read all sensors including light
  readSoilMoisture();    // Your existing function
  readTemperature();     // Your existing function
  readHumidity();        // Your existing function
  readRainSensor();      // Your existing function
  readFlowSensor();      // Your existing function
  readLightSensor();     // NEW: Read light sensor
  
  // Create JSON payload with light data
  String payload = "{";
  payload += "\"soil_moisture\":" + String(soilMoisture) + ",";
  payload += "\"temperature\":" + String(temperature) + ",";
  payload += "\"humidity\":" + String(humidity) + ",";
  payload += "\"rain_raw\":" + String(rainRaw) + ",";
  payload += "\"rain_detected\":" + String(rainDetected ? "true" : "false") + ",";
  payload += "\"light_raw\":" + String(lightRaw) + ",";           // NEW
  payload += "\"light_percent\":" + String(lightPercent) + ",";   // NEW
  payload += "\"light_state\":\"" + lightState + "\",";          // NEW
  payload += "\"flow_rate\":" + String(flowRate) + ",";
  payload += "\"total_liters\":" + String(totalLiters) + ",";
  payload += "\"pump_status\":" + String(pumpStatus) + ",";
  payload += "\"mode\":\"" + mode + "\",";
  payload += "\"rain_expected\":" + String(rainExpected ? "true" : "false") + ",";
  payload += "\"source\":\"esp32\"";
  payload += "}";
  
  // Send via WebSocket or HTTP
  if (webSocket.isConnected()) {
    webSocket.sendTXT(payload);
    Serial.println("Sent via WebSocket: " + payload);
  } else {
    // Fallback to HTTP POST
    sendHTTPData(payload);
  }
}

void loop() {
  // Your existing loop code...
  
  // Send sensor data every 30 seconds
  static unsigned long lastSensorRead = 0;
  if (millis() - lastSensorRead > 30000) {
    sendSensorData();
    lastSensorRead = millis();
  }
  
  // Your existing loop code...
}

/*
WIRING DIAGRAM FOR LDR:

ESP32 Pin 34 (ADC) -----> LDR -----> 3.3V
                     |
                     |
                   10kΩ Resistor
                     |
                    GND

This creates a voltage divider:
- Bright light: Low resistance, higher voltage
- Dark: High resistance, lower voltage
- ESP32 reads this voltage change as 0-4095 ADC value
*/