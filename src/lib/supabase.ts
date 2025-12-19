/**
 * Supabase Client Configuration for Smart Agriculture Dashboard
 * Production-ready database integration
 */

import { createClient } from '@supabase/supabase-js';

// Environment variables validation
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
  throw new Error('VITE_SUPABASE_URL environment variable is required');
}

if (!supabaseAnonKey) {
  throw new Error('VITE_SUPABASE_ANON_KEY environment variable is required');
}

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
});

// Database types
export interface SensorData {
  id?: number;
  timestamp: string;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  rain_raw: number;
  rain_detected: boolean;
  light_raw: number;
  light_percent: number;
  light_state: 'dark' | 'low' | 'normal' | 'very_bright';
  flow_rate: number;
  total_liters: number;
  pump_status: 0 | 1;
  mode: 'AUTO' | 'MANUAL';
  rain_expected: boolean;
  source: 'esp32' | 'simulation' | 'test';
  created_at?: string;
  updated_at?: string;
}

export interface IrrigationEvent {
  id?: number;
  timestamp: string;
  event_type: 'pump_on' | 'pump_off' | 'auto_start' | 'auto_stop' | 'manual_start' | 'manual_stop';
  trigger_reason: string;
  soil_moisture_before?: number;
  soil_moisture_after?: number;
  duration_seconds?: number;
  water_used_liters?: number;
  mode: 'AUTO' | 'MANUAL';
  created_at?: string;
}

export interface RainEvent {
  id?: number;
  timestamp: string;
  event_type: 'rain_detected' | 'rain_stopped' | 'rain_forecast' | 'rain_alert';
  rain_probability?: number;
  rain_amount_mm?: number;
  source: 'esp32' | 'openweather' | 'forecast';
  location: string;
  created_at?: string;
}

export interface ModelMetrics {
  id?: number;
  timestamp: string;
  model_name: 'ARIMA' | 'ARIMAX';
  accuracy_percent: number;
  rmse: number;
  mape: number;
  training_data_rows: number;
  training_duration_seconds?: number;
  model_version: string;
  is_active: boolean;
  created_at?: string;
}

export interface SystemStatus {
  id?: number;
  timestamp: string;
  component: 'esp32' | 'backend' | 'websocket' | 'telegram' | 'weather_api';
  status: 'online' | 'offline' | 'error' | 'warning';
  message?: string;
  response_time_ms?: number;
  created_at?: string;
}

// Database service functions
export class DatabaseService {
  
  // Sensor data operations
  static async insertSensorData(data: Omit<SensorData, 'id' | 'created_at' | 'updated_at'>) {
    const { error } = await supabase
      .from('sensor_data')
      .insert([data]);
    
    if (error) {
      console.error('Error inserting sensor data:', error);
      throw error;
    }
  }

  static async getLatestSensorData(limit: number = 100) {
    const { data, error } = await supabase
      .from('sensor_data')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit);
    
    if (error) {
      console.error('Error fetching sensor data:', error);
      throw error;
    }
    
    return data as SensorData[];
  }

  static async getSensorDataRange(startDate: string, endDate: string) {
    const { data, error } = await supabase
      .from('sensor_data')
      .select('*')
      .gte('timestamp', startDate)
      .lte('timestamp', endDate)
      .order('timestamp', { ascending: true });
    
    if (error) {
      console.error('Error fetching sensor data range:', error);
      throw error;
    }
    
    return data as SensorData[];
  }

  // Irrigation events
  static async insertIrrigationEvent(event: Omit<IrrigationEvent, 'id' | 'created_at'>) {
    const { error } = await supabase
      .from('irrigation_events')
      .insert([event]);
    
    if (error) {
      console.error('Error inserting irrigation event:', error);
      throw error;
    }
  }

  static async getIrrigationEvents(days: number = 7) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const { data, error } = await supabase
      .from('irrigation_events')
      .select('*')
      .gte('timestamp', startDate.toISOString())
      .order('timestamp', { ascending: false });
    
    if (error) {
      console.error('Error fetching irrigation events:', error);
      throw error;
    }
    
    return data as IrrigationEvent[];
  }

  // Rain events
  static async insertRainEvent(event: Omit<RainEvent, 'id' | 'created_at'>) {
    const { error } = await supabase
      .from('rain_events')
      .insert([event]);
    
    if (error) {
      console.error('Error inserting rain event:', error);
      throw error;
    }
  }

  // Model metrics
  static async getActiveModelMetrics() {
    const { data, error } = await supabase
      .from('model_metrics')
      .select('*')
      .eq('is_active', true)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single();
    
    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
      console.error('Error fetching active model metrics:', error);
      throw error;
    }
    
    return data as ModelMetrics | null;
  }

  static async updateModelMetrics(metrics: Omit<ModelMetrics, 'id' | 'created_at'>) {
    // Deactivate all existing models
    await supabase
      .from('model_metrics')
      .update({ is_active: false })
      .eq('model_name', metrics.model_name);
    
    // Insert new active model
    const { error } = await supabase
      .from('model_metrics')
      .insert([{ ...metrics, is_active: true }]);
    
    if (error) {
      console.error('Error updating model metrics:', error);
      throw error;
    }
  }

  // System status
  static async updateSystemStatus(status: Omit<SystemStatus, 'id' | 'created_at'>) {
    const { error } = await supabase
      .from('system_status')
      .insert([status]);
    
    if (error) {
      console.error('Error updating system status:', error);
      throw error;
    }
  }

  static async getSystemStatus() {
    const { data, error } = await supabase
      .from('system_status')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(5);
    
    if (error) {
      console.error('Error fetching system status:', error);
      throw error;
    }
    
    return data as SystemStatus[];
  }

  // Real-time subscriptions
  static subscribeToSensorData(callback: (data: SensorData) => void) {
    return supabase
      .channel('sensor_data_changes')
      .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'sensor_data' },
        (payload) => callback(payload.new as SensorData)
      )
      .subscribe();
  }

  static subscribeToIrrigationEvents(callback: (event: IrrigationEvent) => void) {
    return supabase
      .channel('irrigation_events_changes')
      .on('postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'irrigation_events' },
        (payload) => callback(payload.new as IrrigationEvent)
      )
      .subscribe();
  }
}

export default supabase;