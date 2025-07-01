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
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "papa_db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL: str = "redis://localhost:6379"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Will set from env in __init__

    # First superuser
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "adminpassword")

    # AI Service Keys
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") # Specifically for Gemini LLM
    OPENAI_API_KEY: Optional[str] = None

    # Google Cloud specific (for Vertex AI, etc.)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_CLOUD_LOCATION: Optional[str] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # Default location if not set
    DOCUMENTAI_PROCESSOR_ID: Optional[str] = os.getenv("DOCUMENTAI_PROCESSOR_ID") # For PDF processing
    DOCUMENTAI_LOCATION: Optional[str] = os.getenv("DOCUMENTAI_LOCATION", "us") # DocumentAI often uses 'us' or 'eu'

    # ChromaDB settings (example, if not running locally with defaults)
    # CHROMA_DB_HOST: str = os.getenv("CHROMA_DB_HOST", "localhost")
    # CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", 8000)) # Default Chroma port

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

    @property
    def database_url(self) -> str:
        """Get database URL for async operations"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()

# Set the SQLAlchemy database URI using the async PostgreSQL URL
settings.SQLALCHEMY_DATABASE_URI = settings.database_url
