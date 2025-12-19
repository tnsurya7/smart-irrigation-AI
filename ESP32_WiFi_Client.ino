/*
ESP32 WiFi WebSocket Client for Smart Agriculture
Receives JSON data from Arduino UNO via UART and sends to backend via WebSocket
*/

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "Karan";
const char* password = "karan000";

// WebSocket Configuration
const char* ws_host = "192.168.233.157";  // Your backend server IP
const uint16_t ws_port = 8080;
const char* ws_path = "/wifi";  // Dedicated WiFi endpoint

WebSocketsClient webSocket;

// UART Communication with Arduino UNO
#define UART_BAUD 9600
#define RX_PIN 16  // ESP32 RX pin (connect to Arduino TX)
#define TX_PIN 17  // ESP32 TX pin (connect to Arduino RX)

// Status LEDs (optional)
#define WIFI_LED 2
#define WS_LED 4

// Connection status
bool wifiConnected = false;
bool wsConnected = false;
unsigned long lastHeartbeat = 0;
unsigned long lastDataSent = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(UART_BAUD, SERIAL_8N1, RX_PIN, TX_PIN);
  
  // Initialize LEDs
  pinMode(WIFI_LED, OUTPUT);
  pinMode(WS_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);
  digitalWrite(WS_LED, LOW);
  
  Serial.println("🚀 ESP32 Smart Agriculture WiFi Client Starting...");
  
  // Connect to WiFi
  connectWiFi();
  
  // Initialize WebSocket
  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  webSocket.enableHeartbeat(15000, 3000, 2);
  
  Serial.println("✅ ESP32 initialization complete");
}

void loop() {
  webSocket.loop();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED && wifiConnected) {
    wifiConnected = false;
    digitalWrite(WIFI_LED, LOW);
    Serial.println("❌ WiFi disconnected");
    connectWiFi();
  }
  
  // Read data from Arduino UNO
  if (Serial2.available()) {
    String jsonData = Serial2.readStringUntil('\n');
    jsonData.trim();
    
    if (jsonData.startsWith("{") && jsonData.endsWith("}")) {
      processArduinoData(jsonData);
    }
  }
  
  // Send heartbeat every 30 seconds
  if (millis() - lastHeartbeat > 30000) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }
  
  delay(100);
}

void connectWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    digitalWrite(WIFI_LED, HIGH);
    Serial.println();
    Serial.print("✅ WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed");
  }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      wsConnected = false;
      digitalWrite(WS_LED, LOW);
      Serial.println("❌ WebSocket Disconnected");
      break;
      
    case WStype_CONNECTED:
      wsConnected = true;
      digitalWrite(WS_LED, HIGH);
      Serial.printf("✅ WebSocket Connected to: %s\n", payload);
      
      // Send connection info
      DynamicJsonDocument doc(200);
      doc["type"] = "esp32_connected";
      doc["ip"] = WiFi.localIP().toString();
      doc["timestamp"] = millis();
      
      String message;
      serializeJson(doc, message);
      webSocket.sendTXT(message);
      break;
      
    case WStype_TEXT:
      Serial.printf("📨 Received: %s\n", payload);
      break;
      
    case WStype_ERROR:
      Serial.printf("❌ WebSocket Error: %s\n", payload);
      break;
      
    default:
      break;
  }
}

void processArduinoData(String jsonData) {
  // Parse JSON to validate
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, jsonData);
  
  if (error) {
    Serial.print("❌ JSON Parse Error: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Validate required fields
  if (!doc.containsKey("soil") || !doc.containsKey("temperature") || !doc.containsKey("humidity")) {
    Serial.println("❌ Missing required sensor fields");
    return;
  }
  
  // Add ESP32 metadata
  doc["esp32_timestamp"] = millis();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["source"] = "ESP32_WIFI";
  
  // Send to backend if WebSocket is connected
  if (wsConnected) {
    String message;
    serializeJson(doc, message);
    
    if (webSocket.sendTXT(message)) {
      lastDataSent = millis();
      Serial.println("📤 Sent to backend: " + message);
      
      // Blink WS LED to indicate data transmission
      digitalWrite(WS_LED, LOW);
      delay(50);
      digitalWrite(WS_LED, HIGH);
    } else {
      Serial.println("❌ Failed to send data");
    }
  } else {
    Serial.println("⚠️ WebSocket not connected, data queued");
  }
}

void sendHeartbeat() {
  if (wsConnected) {
    DynamicJsonDocument doc(200);
    doc["type"] = "heartbeat";
    doc["uptime"] = millis();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["last_data_sent"] = lastDataSent;
    
    String message;
    serializeJson(doc, message);
    webSocket.sendTXT(message);
    
    Serial.println("💓 Heartbeat sent");
  }
}