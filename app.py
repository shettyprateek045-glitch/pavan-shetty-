"""
Production Root Entrypoint
==========================
Unified YOLOv11 Computer Vision and Multi-Model ATS Resume Intelligence Dashboard Server.
Binds to 0.0.0.0 and dynamic port ($PORT) provided by cloud hosting platforms (e.g. Onslate, Render, Railway).
"""

import os
import sys
from pathlib import Path
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the main FastAPI application
from backend.main import app

# Mount static files if present
if (ROOT_DIR / "runs").exists():
    app.mount("/runs", StaticFiles(directory=str(ROOT_DIR / "runs")), name="runs")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8000)))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"================================================================")
    print(f" Starting Unified AI Server on http://{host}:{port}")
    print(f" Environment PORT: {os.environ.get('PORT', 'Not set (using default 8000)')}")
    print(f" Serving Dashboard UI directly at http://{host}:{port}/")
    print(f"================================================================")
    uvicorn.run("app:app", host=host, port=port, reload=False)
