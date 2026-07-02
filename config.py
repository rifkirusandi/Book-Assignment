"""Application configuration and settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the FastAPI application."""

    APP_NAME: str = "Book CRUD API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./books.db"

    # Pagination defaults
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100

    class Config:
        env_file = ".env"


settings = Settings()
