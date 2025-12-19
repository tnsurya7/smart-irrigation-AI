import React, { useState, useEffect } from 'react';

interface SensorData {
  source: string;
  soil: number;
  temperature: number;
  humidity: number;
  rain_raw: number;
  light: number;
  flow: number;
  total: number;
  pump: number;
  mode: string;
  rain_expected: boolean;
}

const SimpleDashboard: React.FC = () => {
  const [data, setData] = useState<SensorData>({
    source: 'esp32',
    soil: 0,
    temperature: 0,
    humidity: 0,
    rain_raw: 4095,
    light: 500,
    flow: 0,
    total: 0,
    pump: 0,
    mode: 'auto',
    rain_expected: false
  });
  
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('Never');

  useEffect(() => {
    console.log('🔥 Connecting to WebSocket...');
    const WS_URL = import.meta.env.VITE_WS_URL;
    if (!WS_URL) {
      console.error('VITE_WS_URL environment variable is required');
      return;
    }
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
      // Register as dashboard
      ws.send(JSON.stringify({
        type: "register",
        role: "dashboard",
        id: "dashboard1"
      }));
    };
    
    ws.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        console.log('📡 Received data:', newData);
        
        if (newData.source === 'esp32') {
          setData(newData);
          setLastUpdate(new Date().toLocaleTimeString());
        }
      } catch (error) {
        console.error('❌ Parse error:', error);
      }
    };
    
    ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      setConnected(false);
      // Reconnect after 3 seconds
      setTimeout(() => {
        console.log('🔄 Reconnecting...');
      }, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  const getLightStatus = (light: number) => {
    if (light < 300) return "Bright Sunlight";
    if (light > 800) return "Dark / Night";
    return "Normal Light";
  };

  const getRainStatus = (rainRaw: number) => {
    return rainRaw < 500 ? "Rain Detected" : "Clear";
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-center mb-2">
          🌱 Smart Agriculture Dashboard
        </h1>
        <p className="text-center text-slate-400">
          ARIMAX Algorithm | Final Year Project 2025-2026
        </p>
        <div className="text-center mt-4">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            connected ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              connected ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
            {connected ? 'Connected' : 'Disconnected'}
          </span>
          <span className="ml-4 text-sm text-slate-400">
            Last Update: {lastUpdate}
          </span>
        </div>
      </div>

      {/* Sensor Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Temperature Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">🌡️ Temperature</h3>
          </div>
          <div className="text-3xl font-bold text-blue-400 mb-2">
            {data.temperature.toFixed(1)}°C
          </div>
          <div className="text-sm text-slate-400">
            {data.temperature > 35 ? 'Very Hot' : 
             data.temperature > 25 ? 'Warm' : 
             data.temperature > 15 ? 'Cool' : 'Cold'}
          </div>
        </div>

        {/* Humidity Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">💨 Humidity</h3>
          </div>
          <div className="text-3xl font-bold text-cyan-400 mb-2">
            {data.humidity.toFixed(1)}%
          </div>
          <div className="text-sm text-slate-400">
            {data.humidity > 70 ? 'High' : 
             data.humidity > 40 ? 'Normal' : 'Low'}
          </div>
        </div>

        {/* Soil Moisture Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">💧 Soil Moisture</h3>
          </div>
          <div className="text-3xl font-bold text-green-400 mb-2">
            {data.soil}%
          </div>
          <div className="text-sm text-slate-400">
            {data.soil > 70 ? 'Wet' : 
             data.soil > 30 ? 'Optimal' : 'Dry'}
          </div>
        </div>

        {/* Light Sensor Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">☀️ Light Sensor</h3>
          </div>
          <div className="text-3xl font-bold text-yellow-400 mb-2">
            {data.light} lux
          </div>
          <div className="text-sm text-slate-400">
            {getLightStatus(data.light)}
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Irrigation Control */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <h3 className="text-xl font-semibold mb-4">💧 Irrigation Control</h3>
          
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span>Pump Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                data.pump === 1 ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
              }`}>
                {data.pump === 1 ? '🟢 Pump Running' : '🔴 Pump Off'}
              </span>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span>Mode</span>
              <span className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm font-medium">
                {data.mode.toUpperCase()}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-slate-400 mb-1">Flow Rate</div>
              <div className="text-lg font-semibold">{data.flow.toFixed(2)} L/min</div>
            </div>
            <div>
              <div className="text-sm text-slate-400 mb-1">Total Liters</div>
              <div className="text-lg font-semibold">{data.total.toFixed(2)} L</div>
            </div>
          </div>
        </div>

        {/* Weather Status */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          <h3 className="text-xl font-semibold mb-4">🌧️ Weather Status</h3>
          
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span>Rain Sensor</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                data.rain_raw < 500 ? 'bg-blue-900/30 text-blue-300' : 'bg-green-900/30 text-green-300'
              }`}>
                {getRainStatus(data.rain_raw)}
              </span>
            </div>
          </div>

          <div className="mb-4">
            <div className="text-sm text-slate-400 mb-1">Rain Raw Value</div>
            <div className="text-lg font-semibold">{data.rain_raw}</div>
          </div>

          <div className="text-sm text-slate-400">
            {data.rain_raw < 500 ? 
              '🌧️ Rain detected - Irrigation paused for safety' : 
              '☀️ Clear weather - Normal irrigation operation'
            }
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
        <h3 className="text-xl font-semibold mb-4">📊 System Status</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-sm text-slate-400 mb-1">Data Source</div>
            <div className="text-lg font-semibold text-green-400">{data.source.toUpperCase()}</div>
          </div>
          
          <div>
            <div className="text-sm text-slate-400 mb-1">Connection</div>
            <div className={`text-lg font-semibold ${connected ? 'text-green-400' : 'text-red-400'}`}>
              {connected ? 'Live Data' : 'Disconnected'}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-slate-400 mb-1">Last Update</div>
            <div className="text-lg font-semibold text-blue-400">{lastUpdate}</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center mt-8 text-slate-500 text-sm">
        <p>Team: MONIKA M, SURYA KUMAR M, KARAN M | Dept: CSE</p>
        <p>Smart Agriculture Dashboard - Real-time ESP32 WiFi Monitoring</p>
      </div>
    </div>
  );
};

export default SimpleDashboard;