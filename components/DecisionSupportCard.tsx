import React, { useState, useEffect } from 'react';

interface IrrigationRecommendation {
  action: string;
  reason: string;
  confidence: string;
  predicted_soil: number;
  weather_factor: boolean;
}

interface DecisionSupportCardProps {
  currentSoil: number;
  className?: string;
}

export const DecisionSupportCard: React.FC<DecisionSupportCardProps> = ({ 
  currentSoil, 
  className = "" 
}) => {
  const [recommendation, setRecommendation] = useState<IrrigationRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    const fetchRecommendation = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/irrigation-recommendation?current_soil=${currentSoil}`
        );
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        setRecommendation(data);
      } catch (err) {
        console.error('Recommendation fetch error:', err);
        // Fallback recommendation
        setRecommendation({
          action: "ALLOW_IRRIGATION",
          reason: "Unable to generate recommendation",
          confidence: "Low",
          predicted_soil: currentSoil,
          weather_factor: false
        });
      } finally {
        setLoading(false);
      }
    };

    if (currentSoil > 0) {
      fetchRecommendation();
    }
  }, [currentSoil]);

  if (loading) {
    return (
      <div className={`bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg transition-all duration-300 hover:shadow-xl border border-slate-700/50 card-glow ${className}`}>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className={`bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg transition-all duration-300 hover:shadow-xl border border-slate-700/50 card-glow ${className}`}>
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364-.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h3 className="text-sm text-slate-400">
            ARIMAX Decision Support
          </h3>
        </div>
        <div className="text-center text-slate-400">
          <p>Waiting for sensor data...</p>
        </div>
      </div>
    );
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'ALLOW_IRRIGATION':
        return 'bg-green-900/20 text-green-300 border-green-500';
      case 'DELAY_IRRIGATION':
        return 'bg-yellow-900/20 text-yellow-300 border-yellow-500';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-500';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'High':
        return 'text-green-400';
      case 'Medium':
        return 'text-yellow-400';
      case 'Low':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  return (
    <div className={`bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl shadow-lg transition-all duration-300 hover:shadow-xl border border-slate-700/50 card-glow ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364-.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-sm text-slate-400">
              ARIMAX Decision Support
            </h3>
          </div>
          <div 
            className="relative"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          >
            <span className="text-slate-400 hover:text-slate-600 cursor-help">ℹ️</span>
            {showTooltip && (
              <div className="absolute bottom-full left-0 mb-2 w-64 p-2 bg-slate-900 text-white text-xs rounded shadow-lg z-10">
                Prediction based on historical data + weather forecast
              </div>
            )}
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(recommendation.confidence)}`}>
          {recommendation.confidence} Confidence
        </span>
      </div>

      {/* Recommendation Action */}
      <div className={`p-4 rounded-lg border-2 mb-4 ${getActionColor(recommendation.action)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-lg">
              {recommendation.action.replace('_', ' ')}
            </p>
            <p className="text-sm opacity-90">
              {recommendation.reason}
            </p>
          </div>
          <div className="text-2xl">
            {recommendation.action === 'ALLOW_IRRIGATION' ? '✅' : '⏳'}
          </div>
        </div>
      </div>

      {/* Predicted Soil Moisture */}
      <div className="bg-slate-700/50 p-4 rounded-lg mb-4 border border-slate-600/30">
        <h4 className="text-sm font-semibold text-slate-300 mb-2">
          Predicted Soil Moisture (Next Interval)
        </h4>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-2xl font-bold text-purple-400">
              {typeof recommendation.predicted_soil === "number" ? recommendation.predicted_soil.toFixed(1) : "--"}%
            </p>
            <p className="text-xs text-slate-400">
              Current: {typeof currentSoil === "number" ? currentSoil.toFixed(1) : "--"}%
            </p>
          </div>
          <div className="text-right">
            {recommendation.predicted_soil > currentSoil ? (
              <span className="text-green-400 text-sm">↗ Increasing</span>
            ) : recommendation.predicted_soil < currentSoil ? (
              <span className="text-red-400 text-sm">↘ Decreasing</span>
            ) : (
              <span className="text-slate-400 text-sm">→ Stable</span>
            )}
          </div>
        </div>
      </div>

      {/* Environmental Factors */}
      <div className="bg-blue-900/20 p-3 rounded-lg border border-blue-800/30">
        <h4 className="text-sm font-semibold text-slate-300 mb-2">
          Environmental Factors Used
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
          <div className="flex items-center gap-1">
            <span>🌡️</span>
            <span>Temperature</span>
          </div>
          <div className="flex items-center gap-1">
            <span>💧</span>
            <span>Humidity</span>
          </div>
          <div className="flex items-center gap-1">
            <span>🌧️</span>
            <span>Rain Forecast</span>
          </div>
          <div className="flex items-center gap-1">
            <span>☀️</span>
            <span>Light Intensity</span>
          </div>
        </div>
        {recommendation.weather_factor && (
          <div className="mt-2 text-xs text-blue-400 font-medium">
            ⚠️ Weather conditions considered in recommendation
          </div>
        )}
      </div>

      <div className="mt-3 text-xs text-slate-400 text-center">
        ESP32 retains pump control authority
      </div>
    </div>
  );
};