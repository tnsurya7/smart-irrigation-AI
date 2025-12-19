
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { SensorData } from '../types';

interface HistoryChartProps {
  data: SensorData[];
}

export const HistoryChart: React.FC<HistoryChartProps> = ({ data }) => {
  // Safe data handling - provide empty array if no data
  const safeData = Array.isArray(data) ? data : [];
  
  // Transform data to include soil percentage with safe defaults
  const chartData = safeData.length > 0 ? safeData.map((d, idx) => ({
    ...d,
    soilPercent: typeof d.soil === 'number' ? d.soil : 0,
    temperature: typeof d.temperature === 'number' ? d.temperature : 0,
    humidity: typeof d.humidity === 'number' ? d.humidity : 0,
    ldr: typeof d.ldr === 'number' ? d.ldr : 0,
    index: idx,
  })) : [
    // Provide sample data points when no real data available
    { index: 0, temperature: 0, humidity: 0, soilPercent: 0, ldr: 0 },
    { index: 1, temperature: 0, humidity: 0, soilPercent: 0, ldr: 0 }
  ];

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg transition-all duration-300 hover:shadow-xl border border-slate-700/50 animate-fade-in h-[400px] flex flex-col card-glow">
      <div className="flex items-center gap-2 mb-4">
        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        <h3 className="text-sm text-slate-400">Sensor History (Temp & Humidity)</h3>
      </div>
      <div className="w-full flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
            <XAxis 
              dataKey="index" 
              stroke="rgb(100 116 139)" 
              fontSize={10}
              interval="preserveStartEnd"
              tickMargin={5}
            />
            <YAxis 
              stroke="rgb(100 116 139)" 
              fontSize={10}
              width={40}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(30, 41, 59, 0.95)',
                borderColor: 'rgb(51 65 85)',
                color: '#fff',
                borderRadius: '0.5rem',
                fontSize: '12px',
                padding: '8px',
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '4px' }}
              animationDuration={200}
            />
            <Legend 
              wrapperStyle={{fontSize: "11px"}}
              iconSize={12}
            />
            <Line 
              type="monotone" 
              dataKey="temperature" 
              stroke="#f97316" 
              strokeWidth={2} 
              dot={false} 
              name="Temp (°C)"
              animationDuration={1000}
              animationEasing="ease-out"
            />
            <Line 
              type="monotone" 
              dataKey="humidity" 
              stroke="#3b82f6" 
              strokeWidth={2} 
              dot={false} 
              name="Humidity (%)"
              animationDuration={1000}
              animationEasing="ease-out"
            />
            <Line 
              type="monotone" 
              dataKey="soilPercent" 
              stroke="#22c55e" 
              strokeWidth={2} 
              dot={false} 
              name="Soil (%)" 
              strokeDasharray="5 5"
              animationDuration={1000}
              animationEasing="ease-out"
            />
            <Line 
              type="monotone" 
              dataKey="ldr" 
              stroke="#eab308" 
              strokeWidth={1.5} 
              dot={false} 
              name="Light" 
              opacity={0.6}
              animationDuration={1000}
              animationEasing="ease-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
