#!/bin/bash
set -e

echo "[entrypoint] Creating data directories..."
mkdir -p /app/data/uploads

echo "[entrypoint] Creating schema and seeding..."
python -c "from app.seed import seed_database; seed_database()"

echo "[entrypoint] Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
