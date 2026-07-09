from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] == repo root
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./app/db/pre_legal.db"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    environment: str = "development"
    session_cookie: str = "prelegal_session"
    # Next.js static export output (`next build` with `output: "export"`).
    # Optional: when missing (e.g. API-only dev) static serving is skipped.
    frontend_dir: Path = REPO_ROOT / "frontend" / "out"


settings = Settings()
