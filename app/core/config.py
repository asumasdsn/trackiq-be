from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "TrackIQ Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "LangGraph-powered AI backend built with FastAPI"
    API_V1_STR: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
