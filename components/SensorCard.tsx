import React from 'react';

interface SensorCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

export const SensorCard: React.FC<SensorCardProps> = ({ 
  title, 
  value, 
  unit = '', 
  icon,
  children 
}) => {
  return (
    <div 
      className="
        min-h-[200px]
        p-6
        rounded-[18px]
        bg-slate-800/40
        backdrop-blur-sm
        shadow-[0_4px_20px_rgba(0,0,0,0.25)]
        flex
        flex-col
        justify-center
        items-center
        transition-all
        duration-250
        hover:translate-y-[-3px]
        hover:shadow-[0_8px_24px_rgba(0,0,0,0.35)]
        border
        border-slate-700/30
      "
    >
      {/* Title */}
      <p className="text-sm font-semibold text-slate-300 mb-3 text-center">
        {title}
      </p>

      {/* Icon (if provided) */}
      {icon && (
        <div className="mb-2 opacity-60">
          {icon}
        </div>
      )}

      {/* Main content or children */}
      {children ? (
        children
      ) : (
        <div className="flex items-baseline justify-center">
          <span className="text-5xl font-bold text-white transition-all duration-300">
            {typeof value === 'number' ? value.toFixed(1) : value}
          </span>
          {unit && (
            <span className="text-lg font-normal text-slate-400 ml-1">
              {unit}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
