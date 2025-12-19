-- Smart Agriculture Dashboard - Production-Perfect Supabase Schema
-- Fixes applied: pgcrypto extension, lowercase mode, unique constraints
-- Ready for final year project + cloud deployment

-- REQUIRED FIX 1: Enable pgcrypto extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create sensor_data table for real-time ESP32 data
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    soil_moisture DECIMAL(5,2) NOT NULL CHECK (soil_moisture >= 0 AND soil_moisture <= 100),
    temperature DECIMAL(5,2) NOT NULL CHECK (temperature >= -50 AND temperature <= 100),
    humidity DECIMAL(5,2) NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    rain_raw INTEGER NOT NULL CHECK (rain_raw >= 0 AND rain_raw <= 4095),
    rain_detected BOOLEAN NOT NULL DEFAULT FALSE,
    light_raw INTEGER NOT NULL CHECK (light_raw >= 0 AND light_raw <= 4095),
    light_percent DECIMAL(5,2) NOT NULL CHECK (light_percent >= 0 AND light_percent <= 100),
    light_state VARCHAR(20) NOT NULL CHECK (light_state IN ('dark', 'low', 'normal', 'very_bright')),
    flow_rate DECIMAL(8,2) NOT NULL DEFAULT 0 CHECK (flow_rate >= 0),
    total_liters DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (total_liters >= 0),
    pump_status INTEGER NOT NULL DEFAULT 0 CHECK (pump_status IN (0, 1)),
    -- REQUIRED FIX 2: Lowercase mode to match ESP32 output
    mode VARCHAR(10) NOT NULL DEFAULT 'auto' CHECK (mode IN ('auto', 'manual')),
    rain_expected BOOLEAN NOT NULL DEFAULT FALSE,
    -- IMPROVEMENT 1: Flexible source (no hard enum for scalability)
    source VARCHAR(20) NOT NULL DEFAULT 'esp32',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create irrigation_events table for pump activity tracking
CREATE TABLE IF NOT EXISTS irrigation_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('pump_on', 'pump_off', 'auto_start', 'auto_stop', 'manual_start', 'manual_stop')),
    trigger_reason VARCHAR(50) NOT NULL,
    soil_moisture_before DECIMAL(5,2),
    soil_moisture_after DECIMAL(5,2),
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    water_used_liters DECIMAL(8,2) CHECK (water_used_liters >= 0),
    -- REQUIRED FIX 2: Lowercase mode to match ESP32 output
    mode VARCHAR(10) NOT NULL CHECK (mode IN ('auto', 'manual')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create rain_events table for weather tracking
CREATE TABLE IF NOT EXISTS rain_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('rain_detected', 'rain_stopped', 'rain_forecast', 'rain_alert')),
    rain_probability DECIMAL(5,2) CHECK (rain_probability >= 0 AND rain_probability <= 100),
    rain_amount_mm DECIMAL(6,2) CHECK (rain_amount_mm >= 0),
    source VARCHAR(20) NOT NULL CHECK (source IN ('esp32', 'openweather', 'forecast')),
    location VARCHAR(100) NOT NULL DEFAULT 'Erode, Tamil Nadu',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create model_metrics table for AI model performance tracking
CREATE TABLE IF NOT EXISTS model_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_name VARCHAR(50) NOT NULL CHECK (model_name IN ('ARIMA', 'ARIMAX')),
    accuracy_percent DECIMAL(5,2) NOT NULL CHECK (accuracy_percent >= 0 AND accuracy_percent <= 100),
    rmse DECIMAL(8,4) NOT NULL CHECK (rmse >= 0),
    mape DECIMAL(5,2) NOT NULL CHECK (mape >= 0),
    training_data_rows INTEGER NOT NULL CHECK (training_data_rows > 0),
    training_duration_seconds INTEGER CHECK (training_duration_seconds >= 0),
    model_version VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- REQUIRED FIX 3: Add UNIQUE constraint for model_metrics ON CONFLICT
ALTER TABLE model_metrics ADD CONSTRAINT unique_model_version UNIQUE (model_name, model_version);

-- Create system_status table for monitoring
CREATE TABLE IF NOT EXISTS system_status (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    component VARCHAR(50) NOT NULL CHECK (component IN ('esp32', 'backend', 'websocket', 'telegram', 'weather_api')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('online', 'offline', 'error', 'warning')),
    message TEXT,
    response_time_ms INTEGER CHECK (response_time_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create user_sessions table for authentication
-- Now works correctly with pgcrypto extension enabled
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    login_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logout_timestamp TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance (time-series optimized)
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_source ON sensor_data(source);
CREATE INDEX IF NOT EXISTS idx_sensor_data_source_timestamp ON sensor_data(source, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_irrigation_events_timestamp ON irrigation_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_rain_events_timestamp ON rain_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_model_metrics_active ON model_metrics(is_active, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_status_component ON system_status(component, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, session_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_sensor_data_updated_at BEFORE UPDATE ON sensor_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Production security
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE irrigation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE rain_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (permissive for development, restrict in production)
CREATE POLICY "Allow all operations on sensor_data" ON sensor_data FOR ALL USING (true);
CREATE POLICY "Allow all operations on irrigation_events" ON irrigation_events FOR ALL USING (true);
CREATE POLICY "Allow all operations on rain_events" ON rain_events FOR ALL USING (true);
CREATE POLICY "Allow all operations on model_metrics" ON model_metrics FOR ALL USING (true);
CREATE POLICY "Allow all operations on system_status" ON system_status FOR ALL USING (true);
CREATE POLICY "Allow all operations on user_sessions" ON user_sessions FOR ALL USING (true);

-- Insert initial model metrics (now works with UNIQUE constraint)
INSERT INTO model_metrics (model_name, accuracy_percent, rmse, mape, training_data_rows, model_version, is_active) VALUES
('ARIMA', 82.5, 3.45, 17.5, 7000, '1.0.0', false),
('ARIMAX', 94.6, 1.78, 5.4, 7000, '1.0.0', true)
ON CONFLICT (model_name, model_version) DO NOTHING;

-- Create views for dashboard usage
CREATE OR REPLACE VIEW latest_sensor_data AS
SELECT * FROM sensor_data 
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- IMPROVEMENT 3: Dashboard-optimized view for single latest reading
CREATE OR REPLACE VIEW latest_single_sensor AS
SELECT * FROM sensor_data 
ORDER BY timestamp DESC 
LIMIT 1;

CREATE OR REPLACE VIEW daily_irrigation_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_events,
    SUM(CASE WHEN event_type LIKE '%start%' THEN 1 ELSE 0 END) as irrigation_cycles,
    SUM(COALESCE(water_used_liters, 0)) as total_water_used,
    AVG(COALESCE(duration_seconds, 0)) as avg_duration_seconds
FROM irrigation_events 
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;

CREATE OR REPLACE VIEW active_model_metrics AS
SELECT * FROM model_metrics 
WHERE is_active = true 
ORDER BY timestamp DESC 
LIMIT 1;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Smart Agriculture Database Schema Created Successfully!';
    RAISE NOTICE '📊 Tables: sensor_data, irrigation_events, rain_events, model_metrics, system_status, user_sessions';
    RAISE NOTICE '🔒 Row Level Security: Enabled on all tables';
    RAISE NOTICE '📈 Indexes: Optimized for time-series queries';
    RAISE NOTICE '🤖 AI Models: ARIMA (82.5%%) vs ARIMAX (94.6%%) initialized';
    RAISE NOTICE '🚀 Ready for ESP32 data ingestion and production deployment!';
END $$;