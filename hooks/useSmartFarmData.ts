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
          console.log("✅ WebSocket CONNECTED");
          setConnection("connected");
          ws.send(JSON.stringify({ type: "register", role: "dashboard", id: "dashboard1" }));
        };

        ws.onmessage = (msg) => {
          try {
            const obj = JSON.parse(msg.data);
            console.log("📊 WebSocket message:", obj);
            
            if (obj.type === "sensor_update" && obj.data) {
              const s = obj.data;
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
                pump: typeof s.pump === "number" ? s.pump : 0,
                mode: s.mode || "auto",
                rainExpected: Boolean(s.rain_expected),
              };
              
              setData(newData);
              setHasLiveData(true);
              setHistory((h) => [...h.slice(-49), newData]);
              try {
                localStorage.setItem('lastESP32Data', JSON.stringify(newData));
              } catch (e) {}
            }
          } catch (e) {
            console.error("WebSocket parse error:", e);
          }
        };

        ws.onclose = (event) => {
          console.log("❌ WebSocket CLOSED, reconnecting...", event.code);
          setConnection("disconnected");
          setHasLiveData(false);
          setTimeout(connectWS, 3000);
        };

        ws.onerror = (error) => {
          console.error("❌ WebSocket ERROR:", error);
          setConnection("disconnected");
          setHasLiveData(false);
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
    setData(prev => ({ ...prev, mode: newMode }));
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode: newMode }));
      console.log("📤 Mode command sent:", newMode);
    }
  };

  const sendPumpCommand = (command: "ON" | "OFF") => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ pump_cmd: command }));
      console.log("📤 Pump command sent:", command);
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
