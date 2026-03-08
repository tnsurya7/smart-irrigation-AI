import { useEffect, useRef, useState } from "react";
import { SensorData } from "../types";

// Production WebSocket configuration
const WS_URL = import.meta.env.VITE_WS_URL || "wss://smart-agriculture-backend-my7c.onrender.com/ws";

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
  
  const [hasLiveData, setHasLiveData] = useState(false);
  const [history, setHistory] = useState<SensorData[]>([]);
  const [predictedSoil, setPredictedSoil] = useState<number | null>(null);
  const [wsConnected, setWsConnected] = useState(false); // Track WebSocket connection
  const lastDataTimeRef = useRef<number>(0); // Track last ESP32 data time
  const localModeRef = useRef<"auto" | "manual">("auto"); // Track local mode state
  const localPumpStateRef = useRef<number>(0); // Track local pump state in manual mode
  
  // Check for ESP32 timeout (no data for 10 seconds = offline)
  useEffect(() => {
    const checkTimeout = setInterval(() => {
      if (lastDataTimeRef.current > 0) {
        const timeSinceLastData = Date.now() - lastDataTimeRef.current;
        if (timeSinceLastData > 10000) { // 10 seconds timeout
          console.log("⚠️ ESP32 timeout - no data for 10 seconds");
          setConnection("disconnected");
          setHasLiveData(false);
          
          // Clear all data on timeout - only show live data
          setData({
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
          setHistory([]);
          lastDataTimeRef.current = 0;
        }
      }
    }, 2000);
    
    return () => clearInterval(checkTimeout);
  }, []);
  
  useEffect(() => {
    if (!hasLiveData) {
      const timer = setTimeout(() => setPredictedSoil(45.2), 2000);
      return () => clearTimeout(timer);
    }
  }, [hasLiveData]);
  
  useEffect(() => {
    console.log("🚀 Connecting to WebSocket:", WS_URL);
    
    const connectWS = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("🔌 WebSocket connection opened (waiting for ESP32 data...)");
          setWsConnected(true);
          // Don't set connected yet - wait for actual ESP32 data
          ws.send(JSON.stringify({ type: "register", role: "dashboard", id: "dashboard1" }));
        };

        ws.onmessage = (msg) => {
          try {
            const obj = JSON.parse(msg.data);
            console.log("📊 WebSocket message:", obj);
            
            if (obj.type === "sensor_update" && obj.data) {
              const s = obj.data;
              
              // Only set connected when we receive actual ESP32 data
              if (s.source === "esp32") {
                console.log("✅ ESP32 data received - Device ONLINE");
                setConnection("connected");
                lastDataTimeRef.current = Date.now();
                
                // In manual mode, use local pump state instead of ESP32 state
                const pumpState = localModeRef.current === "manual" 
                  ? localPumpStateRef.current 
                  : (typeof s.pump === "number" ? s.pump : 0);
                
                const newData: SensorData = {
                  soil: typeof s.soil === "number" ? s.soil : 0,
                  temperature: typeof s.temperature === "number" ? s.temperature : 0,
                  humidity: typeof s.humidity === "number" ? s.humidity : 0,
                  rainRaw: typeof s.rain_raw === "number" ? s.rain_raw : 4095,
                  rainDetected: Boolean(s.rain_detected),
                  ldr: typeof s.light_raw === "number" ? s.light_raw : 0,
                  lightPercent: typeof s.light_percent === "number" ? s.light_percent : 0,
                  lightStatus: s.light_state || "Normal Light",
                  flow: typeof s.flow === "number" ? s.flow : 0,
                  totalLiters: typeof s.total === "number" ? s.total : 0,
                  pump: pumpState, // Use local pump state in manual mode
                  mode: localModeRef.current, // Use local mode state, don't override from backend
                  rainExpected: Boolean(s.rain_expected),
                };
                
                setData(newData);
                setHasLiveData(true);
                setHistory((h) => [...h.slice(-49), newData]);
                try {
                  localStorage.setItem('lastESP32Data', JSON.stringify(newData));
                } catch (e) {}
              }
            }
          } catch (e) {
            console.error("WebSocket parse error:", e);
          }
        };

        ws.onclose = (event) => {
          console.log("❌ WebSocket CLOSED, reconnecting...", event.code);
          setWsConnected(false);
          setConnection("disconnected");
          setHasLiveData(false);
          lastDataTimeRef.current = 0;
          
          // Clear all data when disconnected - don't show old values
          setData({
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
          setHistory([]); // Clear history too
          
          setTimeout(connectWS, 3000);
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket ERROR:", error);
          setWsConnected(false);
          setConnection("disconnected");
          setHasLiveData(false);
          lastDataTimeRef.current = 0;
          
          // Clear all data on error - don't show old values
          setData({
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
          setHistory([]);
        };
      } catch (error) {
        console.error("WebSocket connection failed:", error);
        setTimeout(connectWS, 3000);
      }
    };

    connectWS();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  const setMode = (newMode: "auto" | "manual") => {
    console.log("🔄 Mode change requested:", newMode);
    localModeRef.current = newMode; // Update local mode ref
    
    // When switching to auto mode, sync pump state from ESP32
    // When switching to manual mode, keep current pump state
    setData(prev => ({ ...prev, mode: newMode }));
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode: newMode }));
      console.log("📤 Mode command sent:", newMode);
    }
  };

  const sendPumpCommand = (command: "ON" | "OFF") => {
    console.log("🔄 Pump command requested:", command);
    
    // Update local pump state ref for manual mode
    const newPumpState = command === "ON" ? 1 : 0;
    localPumpStateRef.current = newPumpState;
    
    // Optimistic update - immediately update local state
    setData(prev => ({ ...prev, pump: newPumpState }));
    
    // Send command to backend via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ pump_cmd: command }));
      console.log("📤 Pump command sent to backend:", command);
    } else {
      console.error("❌ WebSocket not connected - cannot send pump command");
    }
  };

  const sendRainForecast = (rainExpected: boolean) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ rain_expected: rainExpected }));
      console.log("📤 Rain forecast sent:", rainExpected);
    }
  };

  return {
    data: { ...data, predictedSoil },
    history,
    connection,
    hasLiveData,
    sendPump: sendPumpCommand,
    mode: data.mode,
    setMode,
    sendRainForecast,
  };
}
