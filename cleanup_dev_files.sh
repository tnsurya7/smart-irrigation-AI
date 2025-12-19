#!/bin/bash
# Clean up development and test files for production deployment

echo "🧹 Cleaning up development files for production..."

# Remove test files
echo "Removing test files..."
rm -f test_*.py
rm -f test_*.html
rm -f test.html

# Remove check/debug files
echo "Removing check/debug files..."
rm -f check_*.py
rm -f debug_*.py

# Remove simulation files
echo "Removing simulation files..."
rm -f simulate_*.py
rm -f detect_*.py
rm -f detect_*.js

# Remove development logs
echo "Removing development logs..."
rm -f *.log
rm -f backend.log
rm -f frontend.log
rm -f telegram.log
rm -f websocket.log
rm -f arduino_data.log

# Remove temporary files
echo "Removing temporary files..."
rm -f *.tmp
rm -f *.temp
rm -f .DS_Store

# Remove development artifacts
echo "Removing development artifacts..."
rm -f send_test_message.py
rm -f direct_bot_test.py
rm -f clear_localStorage.html

# Keep essential files but remove development versions
echo "Cleaning up duplicate files..."
rm -f TestApp.tsx 2>/dev/null || true

# Remove old CSV files (will be replaced with database)
echo "Removing old CSV files..."
rm -f soil_moisture_*.csv 2>/dev/null || true
rm -f live_sensor_data.csv 2>/dev/null || true

# Remove old model files (will be regenerated)
echo "Removing old model artifacts..."
rm -f *.pickle 2>/dev/null || true
rm -f arima_*.joblib 2>/dev/null || true
rm -f arimax_*.joblib 2>/dev/null || true
rm -f model_*.joblib 2>/dev/null || true

echo "✅ Development files cleaned up!"
echo "📁 Remaining files are production-ready"

# List remaining important files
echo ""
echo "📋 Production files summary:"
echo "Frontend: App.tsx, components/, hooks/, contexts/"
echo "Backend: backend/production_*.py"
echo "Config: .env.example, .env.production, vite.config.ts"
echo "Deploy: vercel.json, render.yaml, Dockerfile.*"
echo "Docs: PRODUCTION_DEPLOYMENT.md, SECURITY_CHECKLIST.md"