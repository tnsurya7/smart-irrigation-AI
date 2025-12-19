
import React from 'react';
import { SunIcon, MoonIcon } from './icons';

interface HeaderProps {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isDarkMode, toggleDarkMode }) => {
  return (
    <header className="mb-6 flex justify-between items-center">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white transition-all duration-300">
          Smart Agriculture Dashboard
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Real-time sensor data and irrigation control
        </p>
      </div>
      <button
        onClick={toggleDarkMode}
        className="p-2.5 rounded-full bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 transition-all duration-300 hover:scale-110 active:scale-95"
        aria-label="Toggle dark mode"
      >
        {isDarkMode ? <SunIcon className="w-6 h-6" /> : <MoonIcon className="w-6 h-6" />}
      </button>
    </header>
  );
};
