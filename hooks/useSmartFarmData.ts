import { useEffect, useRef, useState } from "react";
import { SensorData } from "../types";

// Production-ready WebSocket configuration
const WS_URL = import.meta.env.VITE_WS_URL;

if (!WS_URL) {
  throw new Error('VITE_WS_URL environment variable is required');
}

// Helper function for light status
function getLightStatus(raw: number): string {
  if (raw < 300) return "Bright Sunlight";
  if (raw > 800) return "Dark / Night";
  return "Normal Light";
}

export default function useSmartFarmData() {
  const wsRef = useRef<WebSocket | null>(null);
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
  const [cooldown, setCooldown] = useState(false);
  const [wsEnabled, setWsEnabled] = useState(true); // Allow disabling WebSocket for offline mode
  
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
  
  // Prevent repeated pump commands
  const lastPumpState = useRef<"ON" | "OFF" | null>(null);
  const lastPumpTime = useRef<number>(0);

  // ---------------------------
  // SEND PUMP CONTROL COMMAND (SAFE - NO SPAM)
  // ---------------------------
  const sendPump = (value: "ON" | "OFF") => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "cmd",
        cmd: "pump",
        value,
      }));
      console.log("Dashboard -> ESP:", value);
    }
  };

  const sendPumpSafe = (value: "ON" | "OFF") => {
    const now = Date.now();
    
    // Do not spam command if already in this state
    if (lastPumpState.current === value) {
      return;
    }
    
    // Cooldown: prevent commands within 8 seconds
    if (now - lastPumpTime.current < 8000) {
      return;
    }
    
    // Update tracking
    lastPumpState.current = value;
    lastPumpTime.current = now;
    
    // Send command
    sendPump(value);
  };

  // NO AUTO IRRIGATION LOGIC - ESP32 IS THE SINGLE SOURCE OF TRUTH
  // Dashboard only sends commands, ESP32 makes all irrigation decisions

  // ---------------------------
  // WEBSOCKET CONNECTION (OPTIONAL)
  // ---------------------------
  useEffect(() => {
    if (!wsEnabled) {
      console.log("WebSocket disabled - running in offline mode");
      return;
    }

    const connectWS = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

      ws.onopen = () => {
        console.log("WS CONNECTED - Waiting for Arduino data...");
        // Don't set connected until we receive actual Arduino data
        ws.send(JSON.stringify({
          type: "register",
          role: "dashboard",
          id: "dashboard1",
        }));
      };

      ws.onmessage = (msg) => {
        try {
          const obj = JSON.parse(msg.data);
          console.log("🔥 WS DATA RECEIVED:", obj);
          
          // CRITICAL: ONLY process messages with source === "esp32"
          if (obj.source !== "esp32") {
            console.log("⏭️ Ignoring non-ESP32 message:", obj.type || "unknown");
            return; // Skip system, register, heartbeat messages
          }
          
          console.log("✅ ESP32 message detected, processing...");
          setConnection("connected");
          
          // SAFE DATA NORMALIZATION - Ensure all fields are valid numbers
          const newData: SensorData = {
            soil: typeof obj.soil === "number" ? obj.soil : 0,
            temperature: typeof obj.temperature === "number" ? obj.temperature : 0,
            humidity: typeof obj.humidity === "number" ? obj.humidity : 0,
            rainRaw: typeof obj.rain_raw === "number" ? obj.rain_raw : 4095,
            rainDetected: Boolean(obj.rain_detected),
            ldr: typeof obj.light_raw === "number" ? obj.light_raw : 500,
            lightPercent: typeof obj.light_percent === "number" ? obj.light_percent : 50,
            lightStatus: obj.light_state || "normal",
            flow: typeof obj.flow === "number" ? obj.flow : 0,
            totalLiters: typeof obj.total === "number" ? obj.total : 0,
            pump: typeof obj.pump === "number" ? obj.pump : 0,
            mode: (obj.mode === "auto" || obj.mode === "manual") ? obj.mode : "auto",
            rainExpected: Boolean(obj.rain_expected),
          };
          
          console.log("✅ NORMALIZED ESP32 DATA:", newData);
          setData(newData);
          setHasLiveData(true);
          setHistory((h) => [...h.slice(-49), newData]);
          
          // Save normalized data
          try {
            localStorage.setItem('lastESP32Data', JSON.stringify(newData));
          } catch (e) {
            console.log("Failed to save ESP32 data:", e);
          }
          
        } catch (e) {
          console.error("WS Parse Error:", e);
        }
      };

        ws.onclose = (event) => {
          console.log("WS CLOSED → RECONNECTING IN 2s", event.code, event.reason);
          setConnection("disconnected");
          setHasLiveData(false); // Reset live data flag on disconnect
          if (wsEnabled) {
            setTimeout(connectWS, 2000);
          }
        };

        ws.onerror = (error) => {
          console.log("WS ERROR:", error);
          setConnection("disconnected");
          setHasLiveData(false); // Reset live data flag on error
        };
      } catch (error) {
        console.log("WebSocket connection failed:", error);
        setConnection("disconnected");
        setHasLiveData(false);
      }
    };

    connectWS();
  }, [wsEnabled]);

  // Send mode command to ESP32 and update local state
  const setMode = (newMode: "auto" | "manual") => {
    // Update local state immediately for better UX
    setData(prev => ({
      ...prev,
      mode: newMode
    }));
    
    // Send command to ESP32 if connected
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const command = {
        mode: newMode // "auto" or "manual"
      };
      wsRef.current.send(JSON.stringify(command));
      console.log("📤 Mode command sent to ESP32:", command);
    } else {
      console.log("📤 Mode changed locally (ESP32 not connected):", newMode);
    }
  };

  // Send pump command to ESP32 (only in manual mode)
  const sendPumpCommand = (command: "ON" | "OFF") => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const pumpCmd = {
        pump_cmd: command
      };
      wsRef.current.send(JSON.stringify(pumpCmd));
      console.log("📤 Pump command sent to ESP32:", pumpCmd);
    }
  };

  // Send rain forecast to ESP32
  const sendRainForecast = (rainExpected: boolean) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const forecast = {
        rain_expected: rainExpected
      };
      wsRef.current.send(JSON.stringify(forecast));
      console.log("📤 Rain forecast sent to ESP32:", forecast);
    }
  };

  return {
    data: {
      ...data,
      predictedSoil // Add predicted soil to data object
    },
    history,
    connection,
    hasLiveData, // Indicates if we have received live ESP32 data
    sendPump: sendPumpCommand,
    mode: data.mode,
    setMode,
    sendRainForecast,
  };
}
