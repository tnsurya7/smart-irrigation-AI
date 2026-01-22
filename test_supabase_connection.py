#!/usr/bin/env python3
"""
Test Supabase connection and set up database schema
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def test_supabase_connection():
    """Test Supabase database connection"""
    try:
        print("🔗 Testing Supabase connection...")
        
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test connection by trying to query a system table
        result = supabase.table('information_schema.tables').select('table_name').limit(1).execute()
        
        if result.data is not None:
            print("✅ Supabase connection successful!")
            print(f"📊 Database URL: {SUPABASE_URL}")
            return True
        else:
            print("❌ Supabase connection failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def check_tables():
    """Check if our tables exist"""
    try:
        print("\n📋 Checking database tables...")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # List of tables we expect
        expected_tables = [
            'sensor_data',
            'irrigation_events', 
            'rain_events',
            'model_metrics',
            'system_status',
            'user_sessions'
        ]
        
        existing_tables = []
        
        for table in expected_tables:
            try:
                # Try to query the table
                result = supabase.table(table).select('*').limit(1).execute()
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing: {str(e)[:100]}...")
        
        print(f"\n📊 Tables found: {len(existing_tables)}/{len(expected_tables)}")
        
        if len(existing_tables) == 0:
            print("\n⚠️  No tables found. You need to run the database schema!")
            print("📝 Go to Supabase SQL Editor and run: database/supabase-schema.sql")
        elif len(existing_tables) < len(expected_tables):
            print("\n⚠️  Some tables are missing. Consider re-running the schema.")
        else:
            print("\n🎉 All tables are present!")
            
        return existing_tables
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

def test_insert_sample_data():
    """Test inserting sample data"""
    try:
        print("\n🧪 Testing data insertion...")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test sensor data insertion
        sample_data = {
            "soil_moisture": 65.5,
            "temperature": 28.3,
            "humidity": 72.1,
            "rain_raw": 3800,
            "rain_detected": False,
            "light_raw": 450,
            "light_percent": 75.2,
            "light_state": "normal",
            "flow_rate": 0.0,
            "total_liters": 0.0,
            "pump_status": 0,
            "mode": "auto",
            "rain_expected": False,
            "source": "test"
        }
        
        result = supabase.table('sensor_data').insert(sample_data).execute()
        
        if result.data:
            print("✅ Sample data inserted successfully!")
            print(f"📝 Inserted record ID: {result.data[0]['id']}")
            
            # Clean up - delete the test record
            supabase.table('sensor_data').delete().eq('source', 'test').execute()
            print("🧹 Test data cleaned up")
            
            return True
        else:
            print("❌ Failed to insert sample data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data insertion: {e}")
        return False

def main():
    """Main test function"""
    print("🌱 Smart Agriculture Dashboard - Supabase Setup Test")
    print("=" * 60)
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Cannot proceed - Supabase connection failed")
        return
    
    # Check tables
    existing_tables = check_tables()
    
    # Test data operations if tables exist
    if 'sensor_data' in existing_tables:
        test_insert_sample_data()
    else:
        print("\n⚠️  Skipping data test - sensor_data table not found")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    
    if len(existing_tables) == 0:
        print("1. 📝 Go to Supabase Dashboard → SQL Editor")
        print("2. 📋 Copy and paste content from: database/supabase-schema.sql")
        print("3. ▶️  Run the SQL script to create all tables")
        print("4. 🔄 Run this test again to verify setup")
    else:
        print("1. ✅ Database is ready for development!")
        print("2. 🚀 You can now run the backend services")
        print("3. 🌐 Deploy to production when ready")
    
    print(f"\n🔗 Supabase Dashboard: https://supabase.com/dashboard/project/your-project-id")

if __name__ == "__main__":
    main()