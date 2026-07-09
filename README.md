# Pre-legal

A SaaS platform for generating legal agreements from templates. A user picks an
agreement type, answers a few guided questions, and gets a draft-level legal
document (a draft — not a substitute for a lawyer).

> **Draft only.** Documents generated here are drafts and are subject to legal
> review. They are not legal advice.

## Stack

- **Backend:** FastAPI (Python ≥ 3.11), managed with [`uv`](https://github.com/astral-sh/uv)
- **Frontend:** Next.js 14 (App Router, static export)
- **Database:** SQLite (file-based for v1)
- **Deploy:** a single Docker image — Next.js is built to static files and
  served by FastAPI (multistage `backend/Dockerfile`), one `app` service on port 8000

## Quick start

### With Docker (recommended)

```bash
./scripts/start.sh          # docker compose up --build  → http://localhost:8000
./scripts/stop.sh           # docker compose down
```

### Local development (no Docker)

```bash
./scripts/dev.sh            # backend with auto-reload on http://localhost:8000
```

### Tests

```bash
./scripts/test.sh           # uv sync --extra dev && uv run pytest  (67 tests)
```

Tests run on in-memory SQLite — no Docker, no Postgres required.

## Features

- **Auth** — bcrypt password hashing + server-side session tokens in httpOnly
  cookies (`/api/auth` register/login/logout/me)
- **Document history** — save and list generated documents, isolated per user
  (`/api/documents`)
- **AI chat drafting** — a conversational interface that asks guided questions
  and builds a live document preview, with a Download PDF button on completion
- **Single-container deploy** — FastAPI serves both the JSON API and the built
  frontend with SPA fallback

## Project structure

```
backend/          FastAPI app (api/ core/ models/ schemas/ services/ db/) + tests/
frontend/         Next.js App Router (app/ components/ lib/)
scripts/          dev / start / stop / test wrappers
.claude/skills/   agent skills (cerebras, legal-template-drafting)
catalog.json      available document types (id, name, fields)
docker-compose.yml
Claude.md         project "law": architecture, standards, and status log
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed. Secrets are never committed
(`.env` is gitignored). The document types the chat can draft live in
`catalog.json` at the project root.

> **Note on the AI:** this build ships **without** a live LLM — the chat runs on
> a deterministic mock (`backend/app/services/chat.py`) so it works with no key.
> The intended path for real calls is the `cerebras` skill
> (`.claude/skills/cerebras/`): LiteLLM → OpenRouter → Cerebras
> (`openai/gpt-oss-120b`), one non-streaming structured-output call. The mock
> already mirrors that response shape, so enabling a live model is just setting
> `OPENROUTER_API_KEY` — no contract change.

## Status

v1 complete — all planned issues closed, 67/67 tests green. Known next steps:
wiring the auth UI to the backend live, a real LLM once a key is available, and
server-side PDF generation.
