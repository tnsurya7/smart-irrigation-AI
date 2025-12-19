#include <ESP8266WiFi.h>
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

// ---------- WIFI ----------
const char* ssid = "Karan";
const char* password = "karan000";

// ---------- WEBSOCKET ----------
const char* ws_host = "192.168.233.157";   // Your server IP
const uint16_t ws_port = 8080;
const char* ws_path = "/ws";

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
    Serial.println("✅ WebSocket Connected to Dashboard");
  }
  if (type == WStype_DISCONNECTED) {
    Serial.println("❌ WebSocket Disconnected");
  }
  if (type == WStype_TEXT) {
    Serial.printf("📨 Received: %s\n", payload);
  }
}

void setup() {
  Serial.begin(9600);   // Communication with Arduino UNO
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("✅ WiFi Connected! IP: ");
  Serial.println(WiFi.localIP());
  
  // Connect to WebSocket server
  webSocket.begin(ws_host, ws_port, ws_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);  // Auto-reconnect every 5 seconds
}

void loop() {
  webSocket.loop();
  
  // Read JSON from Arduino UNO
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (data.startsWith("{") && data.endsWith("}")) {
      // Send real sensor data to dashboard
      webSocket.sendTXT(data);
      Serial.println("📤 Sent to Dashboard: " + data);
    }
  }
  
  delay(100);  // Small delay for stability
}