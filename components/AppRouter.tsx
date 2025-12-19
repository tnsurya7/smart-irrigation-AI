import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { ProjectLanding } from './ProjectLanding';
import { AdminLogin } from './AdminLogin';
import { SmartAgricultureDashboard } from './SmartAgricultureDashboard';

type AppScreen = 'landing' | 'login' | 'dashboard';

export const AppRouter: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('landing');

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Smart Agriculture Dashboard...</p>
        </div>
      </div>
    );
  }

  // If authenticated, always show dashboard
  if (isAuthenticated) {
    return <SmartAgricultureDashboard />;
  }

  // Navigation flow for non-authenticated users
  switch (currentScreen) {
    case 'landing':
      return (
        <ProjectLanding 
          onProceedToLogin={() => setCurrentScreen('login')} 
        />
      );
    
    case 'login':
      return (
        <AdminLogin 
          onBackToLanding={() => setCurrentScreen('landing')} 
        />
      );
    
    default:
      return (
        <ProjectLanding 
          onProceedToLogin={() => setCurrentScreen('login')} 
        />
      );
  }
};