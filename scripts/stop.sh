#!/usr/bin/env bash
# Stop and remove the app containers started by scripts/start.sh.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose down "$@"
