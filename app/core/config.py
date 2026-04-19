from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "TrackIQ Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "LangGraph-powered AI backend built with FastAPI"
    API_V1_STR: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080"]

    # Database
    DATABASE_URL: str = "sqlite:///./trackiq.db"

    # Redis (for checkpointing)
    REDIS_URL: str = "redis://localhost:6379"

    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gpt-4o"

    # LangSmith (optional tracing)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "trackiq"

    # JWT / Auth
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15        # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7           # 7 days

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
