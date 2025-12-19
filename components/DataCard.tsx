
import React from 'react';

interface DataCardProps {
  title: string;
  value: string | number;
  unit: string;
}

export const DataCard: React.FC<DataCardProps> = ({ title, value, unit }) => {


  const getEmojiTitle = () => {
    switch (title.toLowerCase()) {
      case 'temperature':
        return '🌡️ Temperature';
      case 'humidity':
        return '💨 Humidity';
      default:
        return title;
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center transition-all duration-300 hover:shadow-xl hover:scale-[1.02] border border-slate-700/50 h-[220px] card-glow">
      {/* Title */}
      <div className="mb-4">
        <p className="text-sm text-slate-300 font-medium text-center">{getEmojiTitle()}</p>
      </div>
      
      {/* Value */}
      <div className="text-center">
        <span className="text-4xl font-bold text-white transition-all duration-400 ease-out">
          {typeof value === 'number' && !isNaN(value) ? value.toFixed(1) : '0.0'}
        </span>
        <span className="text-xl text-slate-400 ml-1">{unit}</span>
      </div>
    </div>
  );
};
