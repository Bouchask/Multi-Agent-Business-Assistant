import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    # Application Settings
    APP_ENV: str = "development"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "development-secret-key-multi-agent-assistant"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOG_LEVEL: str = "INFO"

    # Database Settings
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/business_assistant.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_HOST: str = "http://localhost:6333"
    QDRANT_LOCAL_PATH: str = str(BASE_DIR / "data" / "qdrant_storage")

    # OpenRouter LLM Settings
    OPENROUTER_API_KEY: str = "sk-or-v1-replace-with-your-openrouter-key"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_FAST_MODEL: str = "google/gemini-pro-1.5"

    # External APIs & Integration Tokens
    TAVILY_API_KEY: str = ""
    GITHUB_PERSONAL_ACCESS_TOKEN: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
