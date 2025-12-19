@echo off
REM Start the FastAPI backend server (Windows)

echo Starting Smart Agriculture Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\installed" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    type nul > venv\installed
)

REM Generate sample data if no data exists
if not exist "sensor_data.csv" (
    echo Generating sample sensor data...
    python sample_data_generator.py
)

REM Train models if not already trained
if not exist "arimax_metadata.joblib" (
    echo Training ARIMAX models...
    python train_arimax.py --csv sensor_data.csv
)

REM Start the backend server
echo Starting FastAPI server on http://localhost:8000
python backend.py
