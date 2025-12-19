#!/usr/bin/env node
/**
 * Arduino Port Detection Utility
 * Helps find the correct serial port for your Arduino
 */

const { SerialPort } = require('serialport');

async function detectArduinoPorts() {
    console.log('🔍 Smart Agriculture Arduino Port Detector');
    console.log('=' * 50);
    
    try {
        const ports = await SerialPort.list();
        
        if (ports.length === 0) {
            console.log('❌ No serial ports found');
            console.log('\n💡 Troubleshooting:');
            console.log('   1. Make sure Arduino is connected via USB');
            console.log('   2. Install Arduino drivers if needed');
            console.log('   3. Try a different USB cable');
            return;
        }

        console.log(`📡 Found ${ports.length} serial port(s):\n`);

        let arduinoPorts = [];

        ports.forEach((port, index) => {
            console.log(`${index + 1}. ${port.path}`);
            console.log(`   Manufacturer: ${port.manufacturer || 'Unknown'}`);
            console.log(`   Product ID: ${port.productId || 'Unknown'}`);
            console.log(`   Vendor ID: ${port.vendorId || 'Unknown'}`);
            
            // Check if it looks like an Arduino
            const isArduino = port.manufacturer && (
                port.manufacturer.toLowerCase().includes('arduino') ||
                port.manufacturer.toLowerCase().includes('ch340') ||
                port.manufacturer.toLowerCase().includes('ftdi') ||
                port.path.includes('usbmodem') ||
                port.path.includes('ttyUSB') ||
                port.path.includes('ttyACM') ||
                port.path.includes('COM')
            );
            
            if (isArduino) {
                console.log('   ✅ Likely Arduino device');
                arduinoPorts.push(port.path);
            }
            
            console.log('');
        });

        // Summary
        console.log('=' * 50);
        console.log('📊 SUMMARY');
        console.log('=' * 50);

        if (arduinoPorts.length > 0) {
            console.log(`✅ Found ${arduinoPorts.length} Arduino-like device(s):`);
            arduinoPorts.forEach(port => {
                console.log(`   • ${port}`);
            });
            
            console.log(`\n🔧 Update your server.js file:`);
            console.log(`   const SERIAL_PORT = '${arduinoPorts[0]}';`);
            
            console.log(`\n🚀 Or set environment variable:`);
            if (process.platform === 'win32') {
                console.log(`   set ARDUINO_PORT=${arduinoPorts[0]} && node server.js`);
            } else {
                console.log(`   ARDUINO_PORT=${arduinoPorts[0]} node server.js`);
            }
        } else {
            console.log('⚠️ No Arduino-like devices detected');
            console.log('\n💡 Manual port selection:');
            ports.forEach(port => {
                console.log(`   Try: ARDUINO_PORT=${port.path} node server.js`);
            });
        }

        console.log('\n🧪 Test connection:');
        console.log('   node server.js');

    } catch (error) {
        console.log('❌ Error detecting ports:', error.message);
    }
}

// Run detection
detectArduinoPorts();