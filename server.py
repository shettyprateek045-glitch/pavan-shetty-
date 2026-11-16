"""
Server Runner for PaaS / Container Environments
"""
import os
import sys
from pathlib import Path
import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8000)))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=False)
