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

# 🔹 Import and include telegram router directly
try:
    from telegram_bot import router as telegram_router
    health_app.include_router(telegram_router)
    print("✅ Telegram router included in health app")
except ImportError as e:
    print(f"⚠️ Failed to import telegram router: {e}")

# 🔹 Mount real app under /api for API endpoints
health_app.mount("/api", main_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting health app on port {port}")
    uvicorn.run("main:health_app", host="0.0.0.0", port=port, reload=False)