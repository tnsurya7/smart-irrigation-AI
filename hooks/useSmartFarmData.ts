import { useEffect, useRef, useState } from "react";
import { SensorData } from "../types";

// Demo mode: Use USB backend instead of WebSocket
const USB_API_URL = "http://localhost:5002/api/live-data";

// Helper function for light status
function getLightStatus(raw: number): string {
  if (raw < 300) return "Bright Sunlight";
  if (raw > 800) return "Dark / Night";
  return "Normal Light";
}

export default function useSmartFarmData() {
  const [connection, setConnection] = useState<"connected" | "disconnected">("disconnected");
  const [data, setData] = useState<SensorData>({
    // STRICT: Only zeros and safe defaults - NEVER fake values like 25°C or 50%
    soil: 0,
    temperature: 0,
    humidity: 0,
    rainRaw: 4095,
    rainDetected: false,
    ldr: 0,
    lightPercent: 0,
    lightStatus: "Normal Light",
    flow: 0,
    totalLiters: 0,
    pump: 0,
    mode: "auto",
    rainExpected: false,
  });
  
  const [hasLiveData, setHasLiveData] = useState(false); // Track if we have received live ESP32 data
  const [history, setHistory] = useState<SensorData[]>([]);
  const [deviceOffline, setDeviceOffline] = useState(false); // Track if ESP32 is offline
  
  // Add predicted soil moisture for ML forecast display
  const [predictedSoil, setPredictedSoil] = useState<number | null>(null);
  
  // Simulate ML prediction for demonstration (when no live data)
  useEffect(() => {
    if (!hasLiveData) {
      // Set a realistic predicted value for demo purposes
      const timer = setTimeout(() => {
        setPredictedSoil(45.2); // Realistic predicted soil moisture
      }, 2000); // Delay to simulate ML processing
      
      return () => clearTimeout(timer);
    }
  }, [hasLiveData]);
  
  // ---------------------------
  // USB POLLING (REPLACES WEBSOCKET)
  // ---------------------------
  useEffect(() => {
    console.log("🚀 Starting USB polling mode for demo");
    console.log("📡 Polling:", USB_API_URL);
    
    const pollUSBData = async () => {
      try {
        const response = await fetch(USB_API_URL);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const usbData = await response.json();
        console.log("📊 USB Data received:", usbData);
        
        // Check if ESP32 device is offline
        const isDeviceOffline = usbData.device_status === "offline";
        setDeviceOffline(isDeviceOffline);
        
        // Set connection status based on API response
        setConnection("connected"); // API is working
        
        // Convert USB data to dashboard format (EXACT MATCH)
        const newData: SensorData = {
          soil: typeof usbData.soil === "number" ? usbData.soil : 0,
          temperature: typeof usbData.temperature === "number" ? usbData.temperature : 0,
          humidity: typeof usbData.humidity === "number" ? usbData.humidity : 0,
          rainRaw: typeof usbData.rainRaw === "number" ? usbData.rainRaw : 4095,
          rainDetected: Boolean(usbData.rainDetected),
          ldr: typeof usbData.ldr === "number" ? usbData.ldr : 0,
          lightPercent: typeof usbData.lightPercent === "number" ? usbData.lightPercent : 0,
          lightStatus: usbData.lightStatus || "Normal Light",
          flow: typeof usbData.flow === "number" ? usbData.flow : 0,
          totalLiters: typeof usbData.totalLiters === "number" ? usbData.totalLiters : 0,
          pump: typeof usbData.pump === "number" ? usbData.pump : 0,
          mode: (usbData.mode === "auto" || usbData.mode === "manual") ? usbData.mode : "auto",
          rainExpected: Boolean(usbData.rainExpected),
        };
        
        console.log("✅ NORMALIZED USB DATA:", newData);
        setData(newData);
        setHasLiveData(!isDeviceOffline); // Only set live data if device is online
        setHistory((h) => [...h.slice(-49), newData]);
        
        // Save normalized data
        try {
          localStorage.setItem('lastESP32Data', JSON.stringify(newData));
        } catch (e) {
          console.log("Failed to save ESP32 data:", e);
        }
        
      } catch (error) {
        console.error("❌ USB polling failed:", error);
        setConnection("disconnected");
        setHasLiveData(false);
        setDeviceOffline(true);
      }
    };

    // Initial poll
    pollUSBData();
    
    // Poll every 2 seconds
    const interval = setInterval(pollUSBData, 2000);
    
    return () => clearInterval(interval);
  }, []);

  // Send pump command (USB mode - actual commands)
  const sendPumpCommand = async (command: "ON" | "OFF") => {
    try {
      const endpoint = command === "ON" ? "/api/pump/on" : "/api/pump/off";
      const response = await fetch(`http://localhost:5002${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      console.log("📤 Pump command result:", result);
      
      if (result.status === "success") {
        console.log(`✅ Pump ${command} command sent successfully`);
      } else {
        console.error(`❌ Pump command failed: ${result.message}`);
      }
    } catch (error) {
      console.error("❌ Failed to send pump command:", error);
    }
  };

  // Send mode command (USB mode - actual commands)
  const setMode = async (newMode: "auto" | "manual") => {
    // Update local state immediately for better UX
    setData(prev => ({
      ...prev,
      mode: newMode
    }));
    
    try {
      if (newMode === "auto") {
        const response = await fetch("http://localhost:5002/api/pump/auto", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        const result = await response.json();
        console.log("📤 Auto mode result:", result);
        
        if (result.status === "success") {
          console.log("✅ Auto mode enabled successfully");
        } else {
          console.error(`❌ Auto mode failed: ${result.message}`);
        }
      } else {
        console.log("📤 Manual mode set locally (no ESP32 command needed)");
      }
    } catch (error) {
      console.error("❌ Failed to set mode:", error);
    }
  };

  // Send rain forecast (demo mode - log only)
  const sendRainForecast = (rainExpected: boolean) => {
    console.log("📤 Rain forecast (demo mode):", rainExpected);
    console.log("🎯 In production, this would send forecast to ESP32");
  };

  return {
    data: {
      ...data,
      predictedSoil // Add predicted soil to data object
    },
    history,
    connection,
    hasLiveData, // Indicates if we have received live ESP32 data
    deviceOffline, // Indicates if ESP32 device is offline
    sendPump: sendPumpCommand,
    mode: data.mode,
    setMode,
    sendRainForecast,
  };
}
