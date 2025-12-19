#!/usr/bin/env node
/**
 * Smart Agriculture Arduino WebSocket Bridge
 * Connects Arduino via USB serial to WebSocket for real-time dashboard
 */

const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

/* -------- CONFIGURATION -------- */
const SERIAL_PORT = process.env.ARDUINO_PORT || '/dev/tty.usbserial-140'; // Detected USB serial device
const BAUD_RATE = 115200;
const WEBSOCKET_PORT = 8080;
const LOG_FILE = 'arduino_data.log';

/* -------- GLOBAL VARIABLES -------- */
let serialPort = null;
let parser = null;
let latestData = null;
let connectedClients = 0;
let dataCount = 0;

console.log('🌱 Smart Agriculture Arduino WebSocket Bridge');
console.log('=' * 50);
console.log(`📡 Serial Port: ${SERIAL_PORT}`);
console.log(`🔗 WebSocket Port: ${WEBSOCKET_PORT}`);
console.log(`⚡ Baud Rate: ${BAUD_RATE}`);
console.log('=' * 50);

/* -------- AUTO-DETECT SERIAL PORT -------- */
async function detectArduinoPort() {
    try {
        const ports = await SerialPort.list();
        console.log('🔍 Available Serial Ports:');
        
        for (const port of ports) {
            console.log(`   • ${port.path} - ${port.manufacturer || 'Unknown'}`);
            
            // Look for Arduino-like devices
            if (port.manufacturer && 
                (port.manufacturer.toLowerCase().includes('arduino') ||
                 port.manufacturer.toLowerCase().includes('ch340') ||
                 port.manufacturer.toLowerCase().includes('ftdi') ||
                 port.path.includes('usbmodem') ||
                 port.path.includes('ttyUSB') ||
                 port.path.includes('ttyACM'))) {
                console.log(`✅ Found Arduino-like device: ${port.path}`);
                return port.path;
            }
        }
        
        console.log('⚠️ No Arduino detected, using default port');
        return SERIAL_PORT;
    } catch (error) {
        console.log('❌ Error detecting ports:', error.message);
        return SERIAL_PORT;
    }
}

/* -------- SERIAL PORT SETUP -------- */
async function setupSerial() {
    try {
        const detectedPort = await detectArduinoPort();
        
        serialPort = new SerialPort({
            path: detectedPort,
            baudRate: BAUD_RATE,
            autoOpen: false
        });

        parser = serialPort.pipe(new ReadlineParser({ delimiter: '\n' }));

        // Open the port
        serialPort.open((err) => {
            if (err) {
                console.log('❌ Serial Port Error:', err.message);
                console.log('\n💡 Troubleshooting:');
                console.log('   1. Check if Arduino is connected');
                console.log('   2. Verify the correct port (Windows: COM3, Mac: /dev/cu.usbmodem*, Linux: /dev/ttyUSB*)');
                console.log('   3. Close Arduino IDE Serial Monitor');
                console.log('   4. Try different USB cable');
                return;
            }
            console.log(`✅ Serial Port Connected: ${detectedPort}`);
        });

        // Handle serial data
        parser.on('data', handleArduinoData);

        // Handle serial errors
        serialPort.on('error', (err) => {
            console.log('❌ Serial Error:', err.message);
        });

        serialPort.on('close', () => {
            console.log('🔌 Serial Port Disconnected');
        });

    } catch (error) {
        console.log('❌ Serial Setup Error:', error.message);
    }
}

/* -------- WEBSOCKET SERVER -------- */
const wss = new WebSocket.Server({ 
    port: WEBSOCKET_PORT,
    perMessageDeflate: false
});

console.log(`✅ WebSocket Server running at ws://localhost:${WEBSOCKET_PORT}`);

/* -------- BROADCAST FUNCTION -------- */
function broadcast(data) {
    const message = JSON.stringify(data);
    let sentCount = 0;
    
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
            sentCount++;
        }
    });
    
    if (sentCount > 0) {
        console.log(`📤 Broadcasted to ${sentCount} client(s)`);
    }
}

/* -------- ARDUINO DATA HANDLER -------- */
function handleArduinoData(line) {
    try {
        // Clean the line
        const cleanLine = line.trim();
        if (!cleanLine) return;

        // Parse JSON
        const arduinoData = JSON.parse(cleanLine);
        
        // Add metadata
        const enhancedData = {
            ...arduinoData,
            timestamp: new Date().toISOString(),
            server_time: Date.now(),
            data_count: ++dataCount
        };

        // Store latest data
        latestData = enhancedData;

        // Log data
        console.log(`📟 Arduino [${dataCount}]:`, {
            soil: arduinoData.soil,
            temp: arduinoData.temperature,
            humidity: arduinoData.humidity,
            pump: arduinoData.pump,
            clients: connectedClients
        });

        // Broadcast to all connected clients
        broadcast(enhancedData);

        // Log to file (optional)
        logDataToFile(enhancedData);

    } catch (err) {
        console.log('⚠️ Invalid JSON from Arduino:', line.trim());
    }
}

/* -------- DATA LOGGING -------- */
function logDataToFile(data) {
    try {
        const logEntry = `${new Date().toISOString()},${JSON.stringify(data)}\n`;
        fs.appendFileSync(LOG_FILE, logEntry);
    } catch (err) {
        // Silent fail for logging
    }
}

/* -------- WEBSOCKET CLIENT HANDLING -------- */
wss.on('connection', (ws, req) => {
    connectedClients++;
    const clientIP = req.socket.remoteAddress;
    console.log(`🌐 Client connected from ${clientIP} (Total: ${connectedClients})`);

    // Send latest data to new client
    if (latestData) {
        ws.send(JSON.stringify(latestData));
        console.log('📤 Sent latest data to new client');
    }

    // Handle client messages
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('📥 Client message:', data);
            
            // Handle ping/pong
            if (data.type === 'ping') {
                ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
            }
        } catch (err) {
            console.log('⚠️ Invalid message from client:', message.toString());
        }
    });

    // Handle client disconnect
    ws.on('close', () => {
        connectedClients--;
        console.log(`❌ Client disconnected (Remaining: ${connectedClients})`);
    });

    // Handle client errors
    ws.on('error', (err) => {
        console.log('❌ Client error:', err.message);
    });
});

/* -------- HTTP STATUS SERVER (BONUS) -------- */
const http = require('http');
const statusServer = http.createServer((req, res) => {
    res.writeHead(200, { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    });
    
    const status = {
        status: 'running',
        serial_connected: serialPort && serialPort.isOpen,
        websocket_port: WEBSOCKET_PORT,
        connected_clients: connectedClients,
        data_count: dataCount,
        latest_data: latestData,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    };
    
    res.end(JSON.stringify(status, null, 2));
});

statusServer.listen(8081, () => {
    console.log('📊 Status server running at http://localhost:8081');
});

/* -------- STARTUP -------- */
async function startup() {
    console.log('🚀 Starting Arduino WebSocket Bridge...');
    await setupSerial();
    console.log('\n✅ System Ready!');
    console.log('🔗 WebSocket: ws://localhost:8080');
    console.log('📊 Status: http://localhost:8081');
    console.log('\n💡 Test in browser console:');
    console.log('   const ws = new WebSocket("ws://localhost:8080");');
    console.log('   ws.onmessage = e => console.log(JSON.parse(e.data));');
    console.log('\nPress Ctrl+C to stop');
}

/* -------- GRACEFUL SHUTDOWN -------- */
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down...');
    
    if (serialPort && serialPort.isOpen) {
        serialPort.close();
    }
    
    wss.close(() => {
        console.log('✅ WebSocket server closed');
        process.exit(0);
    });
});

// Start the system
startup().catch(console.error);