from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./app/db/pre_legal.db"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    environment: str = "development"
    session_cookie: str = "prelegal_session"


settings = Settings()
