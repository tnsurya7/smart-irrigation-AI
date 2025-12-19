
import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';

interface GaugeChartProps {
  value: number;
  label: string;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({ value, label }) => {
  const data = [{ name: 'Moisture', value: value }];
  const color = value < 30 ? '#ef4444' : value < 60 ? '#f97316' : '#22c55e';

  return (
    <div className="w-full h-48 relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          barSize={20}
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <PolarAngleAxis
            type="number"
            domain={[0, 100]}
            angleAxisId={0}
            tick={false}
          />
          <RadialBar
            background
            dataKey="value"
            angleAxisId={0}
            fill={color}
            cornerRadius={10}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-slate-800 dark:text-white">{value}%</span>
        <span className="text-sm text-slate-500 dark:text-slate-400">{label}</span>
      </div>
    </div>
  );
};
