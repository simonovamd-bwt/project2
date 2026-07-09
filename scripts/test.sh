#!/usr/bin/env bash
# Install dev dependencies and run the backend test suite on in-memory SQLite
# (no Docker, no Postgres). Extra args are passed through to pytest.
set -euo pipefail
cd "$(dirname "$0")/../backend"

uv sync --extra dev
uv run pytest "$@"
