# ESP32 USB Bridge Setup

This bridge allows ESP32 connected via USB to send real sensor data to both the web dashboard and mobile app through the same backend.

## Quick Setup

### 1. Install Dependencies
```bash
chmod +x setup_usb_bridge.sh
./setup_usb_bridge.sh
```

### 2. Connect ESP32
- Connect ESP32 to computer via USB cable
- Make sure ESP32 is sending JSON data to Serial at 115200 baud

### 3. Run Bridge
```bash
node usb_esp32_bridge.js
```

### 4. Expected Output
```
🌱 ESP32 USB → Backend Bridge
==================================================
✅ ESP32 port detected: /dev/ttyUSB0
📡 Connecting to ESP32 on /dev/ttyUSB0 at 115200 baud...
✅ ESP32 USB connection established
📊 Waiting for ESP32 data...
📡 ESP32 Data #1: temp: 28.5°C, humidity: 62%, soil: 45%, pump: OFF, mode: auto
✅ Data sent to backend (2 clients notified)
```

## How It Works

1. **ESP32** sends JSON via USB Serial:
   ```json
   {
     "source": "esp32",
     "soil": 45,
     "temperature": 28.5,
     "humidity": 62,
     "pump": 0,
     "mode": "auto"
   }
   ```

2. **USB Bridge** forwards to backend:
   ```
   POST https://smart-agriculture-backend-my7c.onrender.com/demo/esp32
   ```

3. **Backend** broadcasts to all connected clients:
   - Web Dashboard ✅
   - Mobile App ✅
   - Any other WebSocket clients ✅

## Testing

Test the backend endpoint:
```bash
python3 test_usb_bridge.py
```

## Troubleshooting

### ESP32 Not Detected
```bash
# List available ports
ls /dev/tty*

# Set specific port
ESP32_PORT=/dev/ttyUSB0 node usb_esp32_bridge.js
```

### Backend Connection Issues
- Check internet connection
- Render backend might be sleeping (first request takes ~30 seconds)
- Check ESP32 is sending valid JSON

### Dashboard Not Updating
- Open browser console to see WebSocket messages
- Make sure dashboard is connected to the same backend
- Check WebSocket URL in environment variables

## Data Flow

```
ESP32 (USB) → Node.js Bridge → Render Backend → WebSocket → Dashboard & Mobile
```

Both web and mobile apps will show the same real-time ESP32 data seamlessly!