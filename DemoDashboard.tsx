import React, { useState, useEffect } from 'react';

interface ESP32Data {
  source: string;
  soil: number;
  temperature: number;
  humidity: number;
  rain_detected: boolean;
  light_percent: number;
  light_state: string;
  pump: number;
  mode: string;
  timestamp: string;
  device_status: 'online' | 'offline';
}

const DemoDashboard: React.FC = () => {
  const [data, setData] = useState<ESP32Data>({
    source: 'usb',
    soil: 0,
    temperature: 0,
    humidity: 0,
    rain_detected: false,
    light_percent: 0,
    light_state: 'unknown',
    pump: 0,
    mode: 'auto',
    timestamp: new Date().toISOString(),
    device_status: 'offline'
  });
  
  const [lastUpdate, setLastUpdate] = useState<string>('Never');
  const [apiStatus, setApiStatus] = useState<'connecting' | 'online' | 'offline'>('connecting');

  useEffect(() => {
    console.log('🚀 Demo Dashboard starting...');
    console.log('📡 Polling backend every 2 seconds');
    
    const pollData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/live-data');
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const newData: ESP32Data = await response.json();
        
        setData(newData);
        setLastUpdate(new Date().toLocaleTimeString());
        setApiStatus('online');
        
        console.log('📊 Data updated:', {
          temp: `${newData.temperature}°C`,
          humidity: `${newData.humidity}%`,
          soil: `${newData.soil}%`,
          pump: newData.pump ? 'ON' : 'OFF',
          device: newData.device_status
        });
        
      } catch (error) {
        console.error('❌ Failed to fetch data:', error);
        setApiStatus('offline');
      }
    };

    // Initial fetch
    pollData();
    
    // Poll every 2 seconds
    const interval = setInterval(pollData, 2000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-yellow-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return 'Live Data';
      case 'offline': return 'Device Offline';
      default: return 'Connecting...';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">🌱 Smart Agriculture Demo</h1>
        <p className="text-gray-400">ESP32 USB → Backend → Dashboard</p>
        
        {/* Status Banner */}
        <div className="mt-4 flex justify-center items-center space-x-4">
          <div className={`flex items-center px-4 py-2 rounded-full ${
            apiStatus === 'online' ? 'bg-green-900/30 text-green-300' : 
            apiStatus === 'offline' ? 'bg-red-900/30 text-red-300' : 
            'bg-yellow-900/30 text-yellow-300'
          }`}>
            <div className={`w-3 h-3 rounded-full mr-2 ${getStatusColor(apiStatus)}`}></div>
            API: {getStatusText(apiStatus)}
          </div>
          
          <div className={`flex items-center px-4 py-2 rounded-full ${
            data.device_status === 'online' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
          }`}>
            <div className={`w-3 h-3 rounded-full mr-2 ${getStatusColor(data.device_status)}`}></div>
            ESP32: {getStatusText(data.device_status)}
          </div>
          
          <div className="text-sm text-gray-400">
            Last Update: {lastUpdate}
          </div>
        </div>
        
        {/* Offline Warning */}
        {data.device_status === 'offline' && (
          <div className="mt-4 bg-orange-900/30 border border-orange-500/50 rounded-lg p-3">
            <p className="text-orange-300">
              ⚠️ Live device offline – showing last known data
            </p>
          </div>
        )}
      </div>

      {/* Sensor Data Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Temperature */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">🌡️ Temperature</h3>
          </div>
          <div className="text-3xl font-bold text-blue-400 mb-2">
            {data.temperature.toFixed(1)}°C
          </div>
          <div className="text-sm text-gray-400">
            {data.temperature > 35 ? 'Very Hot' : 
             data.temperature > 25 ? 'Warm' : 
             data.temperature > 15 ? 'Cool' : 'Cold'}
          </div>
        </div>

        {/* Humidity */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">💨 Humidity</h3>
          </div>
          <div className="text-3xl font-bold text-cyan-400 mb-2">
            {data.humidity}%
          </div>
          <div className="text-sm text-gray-400">
            {data.humidity > 70 ? 'High' : 
             data.humidity > 40 ? 'Normal' : 'Low'}
          </div>
        </div>

        {/* Soil Moisture */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">💧 Soil Moisture</h3>
          </div>
          <div className="text-3xl font-bold text-green-400 mb-2">
            {data.soil}%
          </div>
          <div className="text-sm text-gray-400">
            {data.soil > 70 ? 'Wet' : 
             data.soil > 30 ? 'Optimal' : 'Dry'}
          </div>
        </div>

        {/* Light Level */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">☀️ Light Level</h3>
          </div>
          <div className="text-3xl font-bold text-yellow-400 mb-2">
            {data.light_percent}%
          </div>
          <div className="text-sm text-gray-400 capitalize">
            {data.light_state.replace('_', ' ')}
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Irrigation Status */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4">💧 Irrigation System</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Pump Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                data.pump === 1 ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
              }`}>
                {data.pump === 1 ? '🟢 Running' : '🔴 Stopped'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Mode</span>
              <span className="px-3 py-1 bg-blue-900/30 text-blue-300 rounded-full text-sm font-medium uppercase">
                {data.mode}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Rain Detection</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                data.rain_detected ? 'bg-blue-900/30 text-blue-300' : 'bg-green-900/30 text-green-300'
              }`}>
                {data.rain_detected ? '🌧️ Rain Detected' : '☀️ Clear'}
              </span>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4">📊 System Info</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Data Source</span>
              <span className="px-3 py-1 bg-purple-900/30 text-purple-300 rounded-full text-sm font-medium uppercase">
                {data.source}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Device Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                data.device_status === 'online' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
              }`}>
                {data.device_status === 'online' ? '🟢 Online' : '🔴 Offline'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Last Update</span>
              <span className="text-sm text-gray-400">
                {new Date(data.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center mt-8 text-gray-500 text-sm">
        <p>Demo Mode: ESP32 → USB → Python Backend → React Dashboard</p>
        <p>Polling every 2 seconds | No WebSocket | Localhost only</p>
      </div>
    </div>
  );
};

export default DemoDashboard;