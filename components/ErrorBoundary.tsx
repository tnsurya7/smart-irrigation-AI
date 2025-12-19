import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Dashboard Error Boundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-4">
          <div className="text-center max-w-md">
            <div className="mb-6">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold mb-2">🌱 Dashboard Error</h1>
              <p className="text-slate-400 mb-4">
                Something went wrong with the dashboard. The system is still running.
              </p>
              <div className="bg-slate-800/50 p-4 rounded-lg text-left text-sm text-slate-300 mb-4">
                <p className="font-semibold mb-2">Error Details:</p>
                <p className="text-red-400 font-mono text-xs">
                  {this.state.error?.message || 'Unknown error'}
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
              >
                🔄 Reload Dashboard
              </button>
              
              <button
                onClick={() => this.setState({ hasError: false })}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
              >
                ↩️ Try Again
              </button>
            </div>
            
            <div className="mt-6 text-xs text-slate-500">
              <p>ESP32 and backend services continue running normally.</p>
              <p>This error only affects the dashboard display.</p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}