
import React from 'react';
import { Alert, AlertType } from '../types';
import { WarningIcon } from './icons';

interface AlertsProps {
  alerts: Alert[];
  removeAlert: (id: number) => void;
}

const alertStyles = {
  [AlertType.Info]: 'bg-blue-100 border-blue-500 text-blue-700 dark:bg-blue-900/50 dark:border-blue-700 dark:text-blue-300',
  [AlertType.Warning]: 'bg-yellow-100 border-yellow-500 text-yellow-700 dark:bg-yellow-900/50 dark:border-yellow-600 dark:text-yellow-300',
  [AlertType.Critical]: 'bg-red-100 border-red-500 text-red-700 dark:bg-red-900/50 dark:border-red-600 dark:text-red-300',
};

export const Alerts: React.FC<AlertsProps> = ({ alerts, removeAlert }) => {
  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-3 right-3 sm:top-5 sm:right-5 w-72 sm:w-80 md:w-96 space-y-2 sm:space-y-3 z-50 max-h-screen overflow-y-auto">
      {alerts.map((alert, index) => (
        <div
          key={alert.id}
          className={`border-l-4 p-3 sm:p-4 rounded-lg shadow-lg flex items-start backdrop-blur-sm transition-all duration-300 hover:scale-[1.02] animate-slide-up ${alertStyles[alert.type]}`}
          style={{animationDelay: `${index * 0.1}s`}}
          role="alert"
        >
          <WarningIcon className="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3 flex-shrink-0 transition-transform duration-300 hover:scale-110" />
          <div className="flex-grow">
            <p className="font-bold capitalize text-sm sm:text-base">{alert.type}</p>
            <p className="text-xs sm:text-sm mt-0.5">{alert.message}</p>
          </div>
          <button 
            onClick={() => removeAlert(alert.id)} 
            className="ml-2 text-lg sm:text-xl font-semibold opacity-70 hover:opacity-100 transition-all duration-200 hover:scale-125 active:scale-95"
            aria-label="Close alert"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
};
