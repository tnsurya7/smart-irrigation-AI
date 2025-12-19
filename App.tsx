
import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { AppRouter } from './components/AppRouter';

function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}

export default App;
