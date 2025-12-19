
import React from 'react';
import { PumpIcon } from './icons';

interface ControlCardProps {
  pumpStatus: 'ON' | 'OFF';
  mode: 'AUTO' | 'MANUAL';
  flowRate: number;
  totalLiters: number;
  predictedSoil: number;
  sendPump: (state: 'ON' | 'OFF') => void;
  setMode: (mode: 'AUTO' | 'MANUAL') => void;
}

export const ControlCard: React.FC<ControlCardProps> = ({ 
  pumpStatus, 
  mode,
  flowRate, 
  totalLiters,
  predictedSoil,
  sendPump, 
  setMode,
}) => {
  const isPumpOn = pumpStatus === 'ON';
  
  // Safe defaults to prevent crashes
  const safeFlowRate = typeof flowRate === 'number' ? flowRate : 0;
  const safeTotalLiters = typeof totalLiters === 'number' ? totalLiters : 0;
  const safePredictedSoil = typeof predictedSoil === 'number' ? predictedSoil : null;
  const safeMode = mode || 'AUTO';

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg transition-all duration-300 hover:shadow-xl border border-slate-700/50 h-[400px] flex flex-col card-glow">
      <div className="flex-1 flex flex-col justify-between">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <h3 className="text-sm text-slate-400">💧 Irrigation Control</h3>
        </div>
        
        {/* Pump Status Display */}
        <div className="flex items-center space-x-4 mb-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${isPumpOn ? 'bg-blue-500 animate-pulse shadow-lg shadow-blue-500/50' : 'bg-slate-700'}`}>
            <PumpIcon className={`w-8 h-8 transition-all duration-300 ${isPumpOn ? 'text-white' : 'text-slate-400'}`} />
          </div>
          <div>
            <p className="text-xs text-slate-400">Pump Status</p>
            <p className={`text-xl font-bold transition-colors duration-300 ${isPumpOn ? 'text-blue-400' : 'text-white'}`}>
              {isPumpOn ? '🟢 Pump Running' : '🔴 Pump Off'}
            </p>
          </div>
        </div>



        {/* Auto Irrigation Mode Toggle */}
        <div className="mb-4">
          <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg transition-all duration-300 hover:shadow-md border border-slate-600/30">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <label htmlFor="auto-mode" className="text-sm text-slate-200 font-semibold cursor-pointer select-none">
                Auto Irrigation Mode
              </label>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs font-medium ${safeMode === 'AUTO' ? 'text-green-400' : 'text-orange-400'}`}>
                {safeMode === 'AUTO' ? 'ON' : 'OFF'}
              </span>
              {/* Custom Toggle Switch */}
              <div 
                onClick={() => {
                  const newMode = safeMode === 'AUTO' ? 'MANUAL' : 'AUTO';
                  console.log('🔄 Changing mode from', safeMode, 'to', newMode);
                  setMode(newMode);
                }}
                className={`relative inline-flex h-6 w-11 items-center rounded-full cursor-pointer transition-all duration-200 hover:scale-105 shadow-inner ${
                  safeMode === 'AUTO' ? 'bg-green-500 shadow-green-500/30' : 'bg-slate-600 shadow-slate-600/30'
                }`}
                title={`Click to turn Auto Irrigation ${safeMode === 'AUTO' ? 'OFF' : 'ON'}`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-all duration-200 ${
                    safeMode === 'AUTO' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </div>
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            {safeMode === 'AUTO' 
              ? '🤖 ESP32 automatically controls irrigation based on soil moisture' 
              : '👤 Manual mode - You control the pump with buttons below'
            }
          </p>
        </div>

        {/* Manual Controls - Only enabled when AUTO mode is OFF */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-slate-300">Manual Controls</p>
            {safeMode === 'AUTO' ? (
              <span className="text-xs text-amber-400 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
                Disabled (Auto Mode ON)
              </span>
            ) : (
              <span className="text-xs text-green-400 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Enabled
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => sendPump('ON')}
              disabled={safeMode === 'AUTO'}
              className="px-4 py-2 rounded-lg font-bold text-sm text-white transition-all duration-300 flex-1 bg-green-500 hover:bg-green-600 hover:scale-105 hover:shadow-lg disabled:bg-slate-600 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:opacity-50 active:scale-95"
              title={safeMode === 'AUTO' ? 'Turn off Auto Mode to use manual controls' : 'Turn pump on manually'}
            >
              Pump ON
            </button>
            <button
              onClick={() => sendPump('OFF')}
              disabled={safeMode === 'AUTO'}
              className="px-4 py-2 rounded-lg font-bold text-sm text-white transition-all duration-300 flex-1 bg-red-500 hover:bg-red-600 hover:scale-105 hover:shadow-lg disabled:bg-slate-600 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:opacity-50 active:scale-95"
              title={safeMode === 'AUTO' ? 'Turn off Auto Mode to use manual controls' : 'Turn pump off manually'}
            >
              Pump OFF
            </button>
          </div>

        </div>

        {/* Flow Meter Stats */}
        <div className="grid grid-cols-2 gap-3 text-center">
          <div className="bg-slate-700/50 p-3 rounded-lg transition-all duration-300 hover:shadow-md hover:scale-105 border border-slate-600/30">
            <p className="text-xs text-slate-400">Flow Rate</p>
            <p className="text-lg font-semibold text-blue-400 transition-all duration-300">{safeFlowRate.toFixed(2)} L/min</p>
          </div>
          <div className="bg-slate-700/50 p-3 rounded-lg transition-all duration-300 hover:shadow-md hover:scale-105 border border-slate-600/30">
            <p className="text-xs text-slate-400">Total Liters</p>
            <p className="text-lg font-semibold text-blue-400 transition-all duration-300">{safeTotalLiters.toFixed(2)} L</p>
          </div>
        </div>

      </div>
    </div>
  );
};
