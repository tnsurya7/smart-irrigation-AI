"""
Render Entry Point - Simple and Clean
"""
import os
import uvicorn

# Import the main FastAPI app
from production_backend import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Smart Agriculture API on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)