#!/usr/bin/env bash
# Build and start the single-container app (API + frontend) via docker-compose.
# Serves on http://localhost:8000. Stop it with scripts/stop.sh.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose up --build "$@"
