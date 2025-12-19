import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface DashboardHeaderProps {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  connection?: "connected" | "disconnected";
  hasLiveData?: boolean;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ 
  isDarkMode, 
  toggleDarkMode, 
  connection = "disconnected", 
  hasLiveData = false 
}) => {
  const { logout } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const handleLogout = () => {
    setShowLogoutModal(true);
  };

  const confirmLogout = () => {
    logout();
    setShowLogoutModal(false);
  };

  return (
    <div className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700 mb-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 p-4">
        {/* Project Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white text-lg">🌱</span>
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">
              Smart Agriculture Dashboard
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              ARIMAX Algorithm | Final Year Project 2025-2026
            </p>
          </div>
        </div>

        {/* Admin Controls */}
        <div className="flex items-center gap-3">
          {/* Connection Status - Only show when live data is available */}
          {hasLiveData && (
            <div className="bg-green-900/30 text-green-300 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400"></div>
              Connected
            </div>
          )}

          {/* Admin Badge */}
          <div className="bg-blue-900/30 text-blue-300 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Admin Access
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="bg-red-900/30 hover:bg-red-900/50 text-red-300 px-4 py-2 rounded-lg font-medium transition-all duration-300 text-sm flex items-center gap-2 hover:scale-105"
            title="Logout from Admin Dashboard"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>

      {/* Project Team Info */}
      <div className="px-4 pb-4">
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
            <div className="flex items-center gap-4">
              <span className="text-slate-600 dark:text-slate-400">
                <strong>Team:</strong> MONIKA M, SURYA KUMAR M, KARAN M
              </span>
              <span className="text-slate-600 dark:text-slate-400">
                <strong>Dept:</strong> CSE
              </span>
            </div>
            <div className="text-slate-500 dark:text-slate-400">
              Trained on 2000 samples • Auto-retrains every 24 hours
            </div>
          </div>
        </div>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 max-w-sm w-full mx-4 animate-scale-in">
            <div className="text-center">
              <div className="w-12 h-12 bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Confirm Logout</h3>
              <p className="text-slate-300 mb-6">Are you sure you want to logout from the admin dashboard?</p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowLogoutModal(false)}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmLogout}
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};