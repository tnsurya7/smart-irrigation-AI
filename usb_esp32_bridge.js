#!/usr/bin/env node
/**
 * ESP32 USB → Backend Bridge
 * 
 * Reads ESP32 JSON data from USB serial port and forwards it to the Render backend
 * This allows both web dashboard and mobile app to show LIVE ESP32 data
 */

const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const axios = require('axios');

// Configuration
const BACKEND_URL = 'https://smart-agriculture-backend-my7c.onrender.com';
const DEMO_ENDPOINT = '/demo/esp32';
const BAUD_RATE = 115200;

// Auto-detect ESP32 port or use manual configuration
const ESP32_PORT = process.env.ESP32_PORT || 'auto'; // Set to specific port like '/dev/ttyUSB0' if needed

class ESP32USBBridge {
    constructor() {
        this.port = null;
        this.parser = null;
        this.isConnected = false;
        this.lastDataTime = null;
        this.dataCount = 0;
    }

    async findESP32Port() {
        """Find ESP32 port automatically"""
        try {
            const ports = await SerialPort.list();
            console.log('🔍 Available serial ports:');
            
            ports.forEach((port, index) => {
                console.log(`   ${index + 1}. ${port.path} - ${port.manufacturer || 'Unknown'}`);
            });

            // Look for common ESP32 identifiers
            const esp32Port = ports.find(port => 
                port.manufacturer && (
                    port.manufacturer.toLowerCase().includes('silicon labs') ||
                    port.manufacturer.toLowerCase().includes('espressif') ||
                    port.manufacturer.toLowerCase().includes('cp210') ||
                    port.path.includes('ttyUSB') ||
                    port.path.includes('cu.usbserial')
                )
            );

            if (esp32Port) {
                console.log(`✅ ESP32 port detected: ${esp32Port.path}`);
                return esp32Port.path;
            }

            // If no auto-detection, use the first available port
            if (ports.length > 0) {
                console.log(`⚠️ No ESP32 detected, using first port: ${ports[0].path}`);
                return ports[0].path;
            }

            throw new Error('No serial ports found');
            
        } catch (error) {
            console.error('❌ Error finding ESP32 port:', error.message);
            throw error;
        }
    }

    async connect() {
        """Connect to ESP32 via USB serial"""
        try {
            console.log('🚀 ESP32 USB Bridge Starting...');
            console.log(`🎯 Backend: ${BACKEND_URL}${DEMO_ENDPOINT}`);
            
            // Determine port
            const portPath = ESP32_PORT === 'auto' ? await this.findESP32Port() : ESP32_PORT;
            
            console.log(`📡 Connecting to ESP32 on ${portPath} at ${BAUD_RATE} baud...`);
            
            // Create serial port connection
            this.port = new SerialPort({
                path: portPath,
                baudRate: BAUD_RATE,
                autoOpen: false
            });

            // Create line parser
            this.parser = this.port.pipe(new ReadlineParser({ delimiter: '\n' }));

            // Set up event handlers
            this.setupEventHandlers();

            // Open connection
            await new Promise((resolve, reject) => {
                this.port.open((error) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve();
                    }
                });
            });

            this.isConnected = true;
            console.log('✅ ESP32 USB connection established');
            console.log('📊 Waiting for ESP32 data...');
            
        } catch (error) {
            console.error('❌ Failed to connect to ESP32:', error.message);
            throw error;
        }
    }

    setupEventHandlers() {
        """Set up serial port event handlers"""
        
        // Handle incoming data
        this.parser.on('data', (line) => {
            this.handleESP32Data(line.trim());
        });

        // Handle connection errors
        this.port.on('error', (error) => {
            console.error('❌ Serial port error:', error.message);
            this.isConnected = false;
        });

        // Handle disconnection
        this.port.on('close', () => {
            console.log('📡 ESP32 disconnected');
            this.isConnected = false;
        });
    }

    async handleESP32Data(rawData) {
        """Process ESP32 JSON data and forward to backend"""
        try {
            // Skip empty lines
            if (!rawData || rawData.length === 0) {
                return;
            }

            // Skip non-JSON lines (debug messages, etc.)
            if (!rawData.startsWith('{')) {
                console.log(`📝 ESP32 Debug: ${rawData}`);
                return;
            }

            // Parse JSON
            let sensorData;
            try {
                sensorData = JSON.parse(rawData);
            } catch (parseError) {
                console.log(`⚠️ Invalid JSON from ESP32: ${rawData}`);
                return;
            }

            // Validate ESP32 data structure
            if (!sensorData.source || sensorData.source !== 'esp32') {
                console.log(`⚠️ Invalid ESP32 data format: ${rawData}`);
                return;
            }

            this.dataCount++;
            this.lastDataTime = new Date();

            console.log(`📡 ESP32 Data #${this.dataCount}:`, {
                temp: `${sensorData.temperature}°C`,
                humidity: `${sensorData.humidity}%`,
                soil: `${sensorData.soil}%`,
                pump: sensorData.pump ? 'ON' : 'OFF',
                mode: sensorData.mode
            });

            // Forward to backend
            await this.forwardToBackend(sensorData);

        } catch (error) {
            console.error('❌ Error processing ESP32 data:', error.message);
        }
    }

    async forwardToBackend(sensorData) {
        """Forward ESP32 data to Render backend"""
        try {
            const response = await axios.post(`${BACKEND_URL}${DEMO_ENDPOINT}`, sensorData, {
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'ESP32-USB-Bridge/1.0'
                },
                timeout: 5000
            });

            if (response.data.success) {
                console.log(`✅ Data sent to backend (${response.data.clients_notified} clients notified)`);
            } else {
                console.log('⚠️ Backend response:', response.data);
            }

        } catch (error) {
            if (error.code === 'ECONNABORTED') {
                console.log('⏰ Backend timeout (continuing...)');
            } else if (error.response) {
                console.log(`❌ Backend error ${error.response.status}: ${error.response.data?.detail || 'Unknown'}`);
            } else {
                console.log(`❌ Network error: ${error.message}`);
            }
        }
    }

    getStatus() {
        """Get bridge status"""
        return {
            connected: this.isConnected,
            dataCount: this.dataCount,
            lastDataTime: this.lastDataTime,
            uptime: process.uptime()
        };
    }

    async disconnect() {
        """Disconnect from ESP32"""
        if (this.port && this.port.isOpen) {
            await new Promise((resolve) => {
                this.port.close(resolve);
            });
        }
        this.isConnected = false;
        console.log('👋 ESP32 USB Bridge disconnected');
    }
}

// Main execution
async function main() {
    console.log('🌱 ESP32 USB → Backend Bridge');
    console.log('=' * 50);
    
    const bridge = new ESP32USBBridge();
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
        console.log('\n🛑 Shutting down ESP32 USB Bridge...');
        await bridge.disconnect();
        process.exit(0);
    });

    // Status reporting
    setInterval(() => {
        const status = bridge.getStatus();
        if (status.connected && status.dataCount > 0) {
            const timeSinceLastData = status.lastDataTime ? 
                Math.round((Date.now() - status.lastDataTime.getTime()) / 1000) : 'never';
            console.log(`📊 Status: ${status.dataCount} packets sent, last data ${timeSinceLastData}s ago`);
        }
    }, 30000); // Every 30 seconds

    try {
        await bridge.connect();
        
        // Keep running
        console.log('🔄 Bridge running... Press Ctrl+C to stop');
        
    } catch (error) {
        console.error('💥 Bridge startup failed:', error.message);
        console.log('\n🔧 Troubleshooting:');
        console.log('   1. Check ESP32 is connected via USB');
        console.log('   2. Check ESP32 is sending JSON data to Serial');
        console.log('   3. Try setting ESP32_PORT environment variable');
        console.log('   4. Check backend is accessible');
        process.exit(1);
    }
}

// Run the bridge
if (require.main === module) {
    main().catch(console.error);
}

module.exports = ESP32USBBridge;