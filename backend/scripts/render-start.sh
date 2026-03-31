#!/usr/bin/env bash
# Render dockerCommand must be a single argv or Render misparses `bash -c '...'`.
# WORKDIR in the backend image is /app/backend.
set -euo pipefail
cd /app/backend
python app/backend_pre_start.py
alembic upgrade head
python app/initial_data.py
exec fastapi run --host 0.0.0.0 --port "${PORT:-10000}" --workers 4 app/main.py
