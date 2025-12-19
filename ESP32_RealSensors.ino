#include <WiFi.h>
#include <WebSocketsClient.h>
#include <DHT.h>

WebSocketsClient webSocket;

// 🔹 WIFI CREDENTIALS
const char* ssid = "iPhone 15";
const char* password = "surya000";

// 🔹 WEBSOCKET SERVER (MAC IP)
const char* ws_host = "192.0.0.2";   // Your Mac IP
const uint16_t ws_port = 8000;        // UNIFIED PORT
const char* ws_path = "/ws";          // Same WebSocket path

// 🔹 SENSOR PINS
#define DHT_PIN 4          // DHT22 temperature & humidity sensor
#define SOIL_PIN A0        // Soil moisture sensor (analog)
#define RAIN_PIN 2         // Rain sensor (digital)
#define LIGHT_PIN A3       // LDR light sensor (analog)
#define PUMP_PIN 5         // Pump relay control
#define FLOW_PIN 3         // Flow sensor (digital interrupt)

// 🔹 SENSOR OBJECTS
DHT dht(DHT_PIN, DHT22);

// 🔹 VARIABLES
unsigned long lastSend = 0;
volatile int flowPulses = 0;
float totalLiters = 0;
int pumpState = 0;  // 0 = OFF, 1 = ON

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      Serial.println("✅ WebSocket connected");
      break;
    case WStype_DISCONNECTED:
      Serial.println("❌ WebSocket disconnected");
      break;
    case WStype_TEXT:
      Serial.print("📩 Server says: ");
      Serial.println((char*)payload);
      
      // Handle pump control commands from dashboard
      String message = String((char*)payload);
      if (message.indexOf("\"cmd\":\"pump\"") > -1) {
        if (message.indexOf("\"value\":\"ON\"") > -1) {
          digitalWrite(PUMP_PIN, HIGH);
          pumpState = 1;
          Serial.println("🚿 Pump turned ON");
        } else if (message.indexOf("\"value\":\"OFF\"") > -1) {
          digitalWrite(PUMP_PIN, LOW);
          pumpState = 0;
          Serial.println("🚿 Pump turned OFF");
        }
      }
      break;
  }
}

// Flow sensor interrupt
void IRAM_ATTR flowInterrupt() {
  flowPulses++;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize sensors
  dht.begin();
  pinMode(RAIN_PIN, INPUT_PULLUP);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FLOW_PIN, INPUT_PULLUP);
  
  // Attach flow sensor interrupt
  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), flowInterrupt, FALLING);
  
  // Initialize pump to OFF
  digitalWrite(PUMP_PIN, LOW);
  pumpState = 0;
  
  Serial.println("\n🔌 Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n✅ WiFi Connected");
  Serial.print("📡 ESP32 IP: ");
  Serial.println(WiFi.localIP());
  
  // WebSocket setup
  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(3000);
  
  Serial.println("🌱 Smart Agriculture ESP32 - Real Sensors Ready!");
}

void loop() {
  webSocket.loop();
  
  // Send real sensor data every 2 seconds
  if (millis() - lastSend > 2000) {
    lastSend = millis();
    
    // 🔹 READ REAL SENSORS
    
    // Temperature & Humidity (DHT22)
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    // Soil Moisture (0-1023 analog, convert to percentage)
    int soilRaw = analogRead(SOIL_PIN);
    int soilPercent = map(soilRaw, 1023, 0, 0, 100);  // Dry=1023→0%, Wet=0→100%
    soilPercent = constrain(soilPercent, 0, 100);
    
    // Rain Sensor (digital: LOW=rain, HIGH=no rain)
    int rainDetected = digitalRead(RAIN_PIN) == LOW ? 1 : 0;
    
    // Light Sensor (LDR: 0-1023)
    int lightLevel = analogRead(LIGHT_PIN);
    
    // Flow Rate Calculation (pulses per second to L/min)
    float flowRate = (flowPulses * 60.0) / (2.0 * 7.5);  // 7.5 pulses per liter
    totalLiters += flowRate / 30.0;  // Add to total (2 sec intervals)
    flowPulses = 0;  // Reset pulse counter
    
    // 🔹 VALIDATE SENSOR READINGS
    if (isnan(temperature)) temperature = 0.0;
    if (isnan(humidity)) humidity = 0.0;
    
    // 🔹 CREATE JSON WITH REAL DATA
    String json = "{";
    json += "\"source\":\"esp32_wifi\",";
    json += "\"soil\":" + String(soilPercent) + ",";
    json += "\"temperature\":" + String(temperature, 1) + ",";
    json += "\"humidity\":" + String(humidity, 1) + ",";
    json += "\"rain\":" + String(rainDetected) + ",";
    json += "\"pump\":" + String(pumpState) + ",";
    json += "\"light\":" + String(lightLevel) + ",";
    json += "\"flow\":" + String(flowRate, 2) + ",";
    json += "\"total\":" + String(totalLiters, 2);
    json += "}";
    
    // Send to WebSocket server
    webSocket.sendTXT(json);
    
    // 🔹 SERIAL OUTPUT FOR DEBUGGING
    Serial.print("📤 Sent: ");
    Serial.println(json);
    Serial.println("🔍 Raw Values:");
    Serial.println("   Soil Raw: " + String(soilRaw) + " → " + String(soilPercent) + "%");
    Serial.println("   Temp: " + String(temperature) + "°C");
    Serial.println("   Humidity: " + String(humidity) + "%");
    Serial.println("   Rain: " + String(rainDetected) + " (0=clear, 1=rain)");
    Serial.println("   Light: " + String(lightLevel) + " lux");
    Serial.println("   Flow: " + String(flowRate) + " L/min");
    Serial.println("   Pump: " + String(pumpState) + " (0=OFF, 1=ON)");
    Serial.println("---");
  }
}