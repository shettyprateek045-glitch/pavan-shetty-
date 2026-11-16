#!/usr/bin/env bash
PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
echo "Starting Unified AI Server on ${HOST}:${PORT}..."
exec uvicorn app:app --host "$HOST" --port "$PORT"
