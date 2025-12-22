"""
Render Health Check Entry Point
Separate minimal FastAPI app for health checks only
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# 🔹 Minimal app ONLY for Render health checks
health_app = FastAPI(title="Health Check App")

@health_app.api_route("/", methods=["GET", "HEAD"])
def root():
    return PlainTextResponse("ok", status_code=200)

@health_app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return PlainTextResponse("ok", status_code=200)

# 🔹 Import your real app AFTER health app
from production_backend import app as main_app

# 🔹 Mount real app under /api
health_app.mount("/api", main_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting health app on port {port}")
    uvicorn.run("main:health_app", host="0.0.0.0", port=port, reload=False)