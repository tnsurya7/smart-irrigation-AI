// server.js
// npm init -y
// npm i ws
// run: node server.js

const WebSocket = require('ws');
const fetch = require('node-fetch'); // You may need: npm install node-fetch@2

const PORT = 8080;
const FASTAPI_URL = 'http://localhost:8000';
const wss = new WebSocket.Server({ port: PORT }, () => {
  console.log('WS server running ws://0.0.0.0:' + PORT);
});

let espSocket = null;
const dashboards = new Set();

// Store last pump command to prevent spam
let lastPumpCommand = null;

// Function to log sensor data to FastAPI backend
async function logSensorData(sensorData) {
  try {
    // Add timestamp if not present
    if (!sensorData.timestamp) {
      sensorData.timestamp = new Date().toISOString();
    }
    
    // Convert ESP32 format to backend format
    const logData = {
      timestamp: sensorData.timestamp,
      soil_pct: sensorData.soil_pct || 0,
      temperature: sensorData.temperature || 0,
      humidity: sensorData.humidity || 0,
      rain_raw: sensorData.rain_raw || 1023,
      ldr_raw: sensorData.ldr_raw || 500,
      flow_lmin: sensorData.flow_lmin || 0,
      total_l: sensorData.total_l || 0,
      pump: sensorData.pump || 0,
      mode: sensorData.mode || 'AUTO'
    };
    
    const response = await fetch(`${FASTAPI_URL}/log-sensor-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(logData)
    });
    
    if (response.ok) {
      console.log('📊 Sensor data logged to backend');
    } else {
      console.log('⚠️  Failed to log sensor data:', response.status);
    }
  } catch (error) {
    console.log('⚠️  Error logging sensor data:', error.message);
  }
}

wss.on('connection', (ws, req) => {
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (data) => {
    let text = data.toString();
    // try parse
    let msg = null;
    try { msg = JSON.parse(text); } catch (e) { /* ignore */ }

    // registration
    if (msg && msg.type === 'register') {
      if (msg.role === 'esp') {
        console.log('ESP registered:', msg.id || 'esp');
        espSocket = ws;
        ws.role = 'esp';
        ws.id = msg.id || 'esp1';
        ws.send(JSON.stringify({ type: 'ack', role: 'esp' }));
        return;
      } else if (msg.role === 'dashboard') {
        ws.role = 'dashboard';
        ws.id = msg.id || ('dash-' + (Math.random()*1000|0));
        dashboards.add(ws);
        console.log('Dashboard connected:', ws.id);
        ws.send(JSON.stringify({ type: 'ack', role: 'dashboard' }));
        return;
      }
    }

    // If message from ESP -> broadcast to dashboards and log data
    if (ws.role === 'esp') {
      // Log sensor data to backend for future retraining
      if (msg && msg.type === 'sensors') {
        logSensorData(msg);
      }
      
      // forward raw sensor JSON to all dashboards
      dashboards.forEach(d => {
        if (d.readyState === WebSocket.OPEN) d.send(text);
      });
      return;
    }

    // If message from dashboard: handle commands
    if (ws.role === 'dashboard') {
      // expect e.g. {"type":"cmd","cmd":"pump","value":"ON"}
      if (msg && msg.type === 'cmd' && msg.cmd === 'pump') {
        // Check if this is a duplicate command
        if (msg.value !== lastPumpCommand) {
          console.log('Pump command changed:', msg.value);
          lastPumpCommand = msg.value;
          
          // Forward to ESP only if command changed
          if (espSocket && espSocket.readyState === WebSocket.OPEN) {
            espSocket.send(JSON.stringify(msg));
          } else {
            ws.send(JSON.stringify({ type: 'error', message: 'ESP not connected' }));
          }
        } else {
          console.log('⚠️  Ignored duplicate pump command:', msg.value);
        }
      }
      return;
    }

    // unknown client: if JSON has type:sensors treat as ESP otherwise ignore
    if (msg && msg.type === 'sensors') {
      // assume this was ESP (no register)
      espSocket = ws;
      ws.role = 'esp';
    }
  });

  ws.on('close', () => {
    if (ws.role === 'esp') {
      console.log('ESP disconnected');
      if (espSocket === ws) espSocket = null;
    } else if (ws.role === 'dashboard') {
      dashboards.delete(ws);
      console.log('Dashboard disconnected');
    }
  });
});

// heartbeat
setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);