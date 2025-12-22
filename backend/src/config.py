"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM Provider Configuration (gemini or openai)
    llm_provider: str = "gemini"

    # Gemini Configuration
    gemini_api_key: str = ""
    
    # OpenAI Configuration
    openai_api_key: str = ""

    # Model Configuration
    embedding_model: str = "models/embedding-001"
    chat_model: str = "gemini-2.5-flash"
    max_tokens: int = 1024

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "book_chunks"

    # Database Configuration
    database_url: str

    # CORS Configuration
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # RAG Configuration
    confidence_threshold: float = 0.7
    max_context_chunks: int = 5

    # Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50

    # JWT Configuration
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
