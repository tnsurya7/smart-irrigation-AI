#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting Smart Agriculture Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Generate sample data if no data exists
if [ ! -f "sensor_data.csv" ]; then
    echo "📊 Generating sample sensor data..."
    python sample_data_generator.py
fi

# Train models if not already trained
if [ ! -f "arimax_metadata.joblib" ]; then
    echo "🧠 Training ARIMAX models..."
    python train_arimax.py --csv sensor_data.csv
fi

# Start the backend server
echo "✅ Starting FastAPI server on http://localhost:8000"
python backend.py
