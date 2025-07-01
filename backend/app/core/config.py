from pydantic_settings import BaseSettings
from typing import List, Union, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Past Questions App"
    PROJECT_VERSION: str = "0.1.0"

    API_V1_STR: str = "/api/v1"

    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Will set from env in __init__

    # First superuser
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "adminpassword")

    # AI Service Keys
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY") # General key, might be used by some Google APIs
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") # Specifically for Gemini LLM

    # Google Cloud specific (for Vertex AI, etc.)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_CLOUD_LOCATION: Optional[str] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # Default location if not set
    DOCUMENTAI_PROCESSOR_ID: Optional[str] = os.getenv("DOCUMENTAI_PROCESSOR_ID") # For PDF processing
    DOCUMENTAI_LOCATION: Optional[str] = os.getenv("DOCUMENTAI_LOCATION", "us") # DocumentAI often uses 'us' or 'eu'

    # ChromaDB settings (example, if not running locally with defaults)
    # CHROMA_DB_HOST: str = os.getenv("CHROMA_DB_HOST", "localhost")
    # CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", 8000)) # Default Chroma port


    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()

# Construct SQLAlchemy Database URI after loading other settings
if settings.POSTGRES_USER and settings.POSTGRES_PASSWORD and settings.POSTGRES_SERVER and settings.POSTGRES_DB:
    settings.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
else:
    # Handle case where DB connection details might not be fully provided if app can run without DB
    # For now, we assume they are provided if DB is intended to be used.
    # If running in a mode that doesn't require DB, this might be None.
    pass
