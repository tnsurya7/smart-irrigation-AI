"""
Render Entry Point - Import and serve production backend
"""
import os
import sys
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main FastAPI app
try:
    from production_backend import app
    print("✅ Successfully imported production_backend app")
except ImportError as e:
    print(f"❌ Failed to import production_backend: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Smart Agriculture API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)