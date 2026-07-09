#!/usr/bin/env bash
# Run the backend locally with auto-reload — no Docker, no Postgres.
# FastAPI serves the JSON API on http://localhost:8000; if the frontend has
# been built (frontend/out), it is served too, otherwise API-only.
set -euo pipefail
cd "$(dirname "$0")/../backend"

uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
