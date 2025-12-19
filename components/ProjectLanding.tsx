import React from 'react';

interface ProjectLandingProps {
  onProceedToLogin: () => void;
}

export const ProjectLanding: React.FC<ProjectLandingProps> = ({ onProceedToLogin }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl">🌱</span>
            </div>
            <h1 className="text-sm font-medium text-slate-600 uppercase tracking-wide">
              Final Year Project 2025-2026
            </h1>
          </div>
        </div>

        {/* Project Title */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
            <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent animate-pulse">
              Accurate Soil Moisture Prediction
            </span>
            <br />
            <span className="text-white">in </span>
            <span className="bg-gradient-to-r from-green-400 via-emerald-500 to-teal-400 bg-clip-text text-transparent">
              Smart Agriculture
            </span>
            <br />
            <span className="text-white">Using </span>
            <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-indigo-500 bg-clip-text text-transparent">
              ARIMAX Algorithm
            </span>
          </h1>
          
          <div className="max-w-3xl mx-auto">
            <p className="text-lg md:text-xl text-slate-300 leading-relaxed mb-8">
              An intelligent irrigation management system that combines real-time sensor data, 
              weather forecasting, and advanced time series analysis to optimize agricultural water usage.
            </p>
            
            <div className="flex flex-wrap justify-center gap-3 text-sm text-slate-300">
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Machine Learning
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Artificial Intelligence
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
                IoT Integration
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Time Series Analysis
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                Full Stack Development
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                N8N Automation
              </span>
              <span className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-full shadow-sm hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <svg className="w-4 h-4 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                AI Agents
              </span>
            </div>
          </div>
        </div>

        {/* Project Guide Section */}
        <div className="max-w-4xl mx-auto mb-16 animate-slide-up" style={{animationDelay: '0.3s'}}>
          <div className="bg-slate-800 rounded-2xl shadow-lg p-8 border border-slate-700 hover:shadow-2xl hover:scale-[1.02] transition-all duration-500 card-glow">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Project Guide</h2>
            
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                <div className="w-20 h-20 rounded-full overflow-hidden shadow-lg border-4 border-blue-500 animate-float ring-2 ring-blue-300/50">
                  <img 
                    src="/gopisir.png" 
                    alt="Mr. V. GOPINATH" 
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    onError={(e) => {
                      // Fallback to gradient background with emoji if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.className = "w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center animate-float shadow-lg border-4 border-blue-500 ring-2 ring-blue-300/50";
                        parent.innerHTML = '<span class="text-2xl text-blue-600">👨‍🏫</span>';
                      }
                    }}
                  />
                </div>
              </div>
              
              <div className="text-center md:text-left">
                <h3 className="text-xl font-semibold text-white mb-2">
                  Mr. V. GOPINATH
                </h3>
                <p className="text-slate-300 mb-1">Assistant Professor, Department of Computer Science & Engineering</p>
                <p className="text-slate-400 text-sm">Project Supervisor & Technical Mentor</p>
              </div>
            </div>
          </div>
        </div>

        {/* Team Members Section */}
        <div className="max-w-6xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Project Team</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Team Member 1 */}
            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 border border-slate-700 hover:shadow-2xl transition-all duration-500 hover:scale-105 card-glow animate-scale-in" style={{animationDelay: '0.5s'}}>
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden shadow-lg animate-float border-4 border-pink-500/30">
                  <img 
                    src="/team/moni.png" 
                    alt="MONIKA M" 
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    onError={(e) => {
                      // Fallback to gradient background with SVG if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.className = "w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-pink-500 to-rose-600 rounded-full flex items-center justify-center animate-float shadow-lg";
                        parent.innerHTML = '<svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>';
                      }
                    }}
                  />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">MONIKA M</h3>
                <p className="text-green-400 font-medium mb-1">Computer Science & Engineering</p>
                <p className="text-slate-400 text-sm">Final Year</p>
              </div>
            </div>

            {/* Team Member 2 */}
            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 border border-slate-700 hover:shadow-2xl transition-all duration-500 hover:scale-105 card-glow animate-scale-in" style={{animationDelay: '0.6s'}}>
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden shadow-lg animate-float border-4 border-blue-500/30" style={{animationDelay: '1s'}}>
                  <img 
                    src="/team/surya.png" 
                    alt="SURYA KUMAR M" 
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    onError={(e) => {
                      // Fallback to gradient background with SVG if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.className = "w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center animate-float shadow-lg";
                        parent.innerHTML = '<svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>';
                      }
                    }}
                  />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">SURYA KUMAR M</h3>
                <p className="text-green-400 font-medium mb-1">Computer Science & Engineering</p>
                <p className="text-slate-400 text-sm">Final Year</p>
              </div>
            </div>

            {/* Team Member 3 */}
            <div className="bg-slate-800 rounded-2xl shadow-lg p-6 border border-slate-700 hover:shadow-2xl transition-all duration-500 hover:scale-105 card-glow animate-scale-in" style={{animationDelay: '0.7s'}}>
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden shadow-lg animate-float border-4 border-emerald-500/30" style={{animationDelay: '2s'}}>
                  <img 
                    src="/team/karan.png" 
                    alt="KARAN M" 
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                    onError={(e) => {
                      // Fallback to gradient background with SVG if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.className = "w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center animate-float shadow-lg";
                        parent.innerHTML = '<svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>';
                      }
                    }}
                  />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">KARAN M</h3>
                <p className="text-green-400 font-medium mb-1">Computer Science & Engineering</p>
                <p className="text-slate-400 text-sm">Final Year</p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Features */}
        <div className="max-w-6xl mx-auto mb-16 animate-slide-up" style={{animationDelay: '0.8s'}}>
          <h2 className="text-2xl font-bold text-white text-center mb-8">System Features</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-slide-in-left" style={{animationDelay: '0.9s'}}>
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-white">ARIMAX Prediction</h3>
              </div>
              <p className="text-slate-300 text-sm">Advanced time series analysis with exogenous variables for accurate soil moisture forecasting.</p>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-scale-in" style={{animationDelay: '1.0s'}}>
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-white">Weather Integration</h3>
              </div>
              <p className="text-slate-300 text-sm">Real-time weather data from OpenWeather API for intelligent irrigation decisions.</p>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-slide-in-right" style={{animationDelay: '1.1s'}}>
              <div className="flex items-center gap-3 mb-3">
                <svg className="w-8 h-8 text-green-400 icon-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
                <h3 className="font-semibold text-white">IoT Sensors</h3>
              </div>
              <p className="text-slate-300 text-sm">ESP32-based real-time monitoring of soil moisture, temperature, and environmental conditions.</p>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-slide-in-left" style={{animationDelay: '1.2s'}}>
              <div className="flex items-center gap-3 mb-3">
                <svg className="w-8 h-8 text-cyan-400 icon-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                <h3 className="font-semibold text-white">Smart Irrigation</h3>
              </div>
              <p className="text-slate-300 text-sm">Automated irrigation control with weather-aware decision support system.</p>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-scale-in" style={{animationDelay: '1.3s'}}>
              <div className="flex items-center gap-3 mb-3">
                <svg className="w-8 h-8 text-purple-400 icon-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <h3 className="font-semibold text-white">N8N Email Automation</h3>
              </div>
              <p className="text-slate-300 text-sm">Daily weather reports automatically sent at 5 AM via N8N workflow automation.</p>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:shadow-2xl hover:scale-105 transition-all duration-500 card-glow animate-slide-in-right" style={{animationDelay: '1.4s'}}>
              <div className="flex items-center gap-3 mb-3">
                <svg className="w-8 h-8 text-emerald-400 icon-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <h3 className="font-semibold text-white">AI Agriculture Assistant</h3>
              </div>
              <p className="text-slate-300 text-sm">Intelligent chatbot powered by N8N automation and AI agents for agricultural guidance.</p>
            </div>
          </div>
        </div>

        {/* Proceed Button */}
        <div className="text-center">
          <button
            onClick={onProceedToLogin}
            className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            Access Admin Dashboard →
          </button>
          <p className="text-slate-500 text-sm mt-4">
            Secure admin access required for system monitoring
          </p>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 pt-8 border-t border-slate-700">
          <p className="text-slate-400 text-sm">
            © 2025-2026 Final Year Project | Department of Computer Science & Engineering
          </p>
        </div>
      </div>
    </div>
  );
};