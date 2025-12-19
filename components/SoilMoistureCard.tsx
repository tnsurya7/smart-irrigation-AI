import React, { useState, useEffect, useRef } from 'react';

interface SoilMoistureCardProps {
  soilADC: number;
}

export const SoilMoistureCard: React.FC<SoilMoistureCardProps> = ({ soilADC }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const prevValueRef = useRef(0);

  // Handle both percentage and ADC formats with safe defaults
  const calculateSoilPercent = (value: number): number => {
    // Ensure value is a valid number
    const safeValue = typeof value === 'number' && !isNaN(value) ? value : 0;
    let percent: number;
    
    // If value is already a percentage (0-100), use it directly
    if (safeValue <= 100) {
      percent = Math.round(safeValue);
    } else {
      // If value is ADC format (0-4095), convert to percentage
      percent = Math.round((safeValue / 4095) * 100);
    }
    
    if (percent < 0) percent = 0;
    if (percent > 100) percent = 100;
    return percent;
  };

  const soilPercent = calculateSoilPercent(soilADC);

  // Get color based on moisture level (orange like screenshot)
  const getArcColor = (moisture: number): string => {
    if (moisture < 20) return '#ef4444'; // red
    if (moisture < 40) return '#f97316'; // orange
    if (moisture < 60) return '#f59e0b'; // amber/orange
    if (moisture < 80) return '#84cc16'; // lime
    return '#22c55e'; // green
  };

  // Animate value changes
  useEffect(() => {
    const duration = 400;
    const steps = 20;
    const stepValue = (soilPercent - displayValue) / steps;
    const stepDuration = duration / steps;

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      if (currentStep >= steps) {
        setDisplayValue(soilPercent);
        clearInterval(interval);
      } else {
        setDisplayValue((prev: number) => prev + stepValue);
      }
    }, stepDuration);

    prevValueRef.current = soilPercent;

    return () => clearInterval(interval);
  }, [soilPercent, displayValue]);

  // Calculate arc path
  const size = 140;
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  // Semi-circle arc (180 degrees)
  const arcLength = circumference * 0.5;
  const progress = (displayValue / 100) * arcLength;
  const offset = arcLength - progress;

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center transition-all duration-300 hover:shadow-xl hover:scale-[1.02] border border-slate-700/50 h-[220px] card-glow">
      {/* Title */}
      <p className="text-sm text-slate-400 mb-2">💧 Soil Moisture</p>

      {/* Semicircle gauge */}
      <div className="relative flex items-end justify-center" style={{ width: size, height: size / 2 + 30 }}>
        <svg width={size} height={size / 2 + 10} className="overflow-visible">
          {/* Background arc - 180 degrees */}
          <path
            d={`M ${strokeWidth/2} ${size/2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${size/2}`}
            fill="none"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          
          {/* Progress arc - 180 degrees */}
          <path
            d={`M ${strokeWidth/2} ${size/2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${size/2}`}
            fill="none"
            stroke={getArcColor(displayValue)}
            strokeWidth={strokeWidth}
            strokeDasharray={arcLength}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-400 ease-out"
            style={{
              filter: `drop-shadow(0 0 6px ${getArcColor(displayValue)}60)`
            }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <p 
            className="text-4xl font-bold transition-all duration-400 ease-out text-center"
            style={{ color: getArcColor(displayValue) }}
          >
            {Math.round(displayValue)}<span className="text-2xl">%</span>
          </p>
        </div>
      </div>
    </div>
  );
};
