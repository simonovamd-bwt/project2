# Pre-legal — FastAPI serving both the JSON API and the built Next.js frontend.
#
# Stage 1: build the Next.js static export (output: "export").
FROM node:20-slim AS frontend-build

# Anonymous telemetry would make a network call during `next build`; disable it
# so the build never depends on reaching nextjs.org.
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# Stage 2: the FastAPI app, with the built frontend copied in as static files.
FROM python:3.11-slim AS backend

RUN pip install --no-cache-dir uv

WORKDIR /app/backend

COPY backend/pyproject.toml ./
RUN uv sync --no-dev

COPY backend/app ./app
COPY --from=frontend-build /frontend/out /app/frontend/out

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
