"""
Configuration settings for LCious Application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "LCious API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database - SQLite (SQLite doesn't need password)
    DATABASE_URL: str = "sqlite:///./licious_db.sqlite"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Local network access
        "http://192.168.100.202:8091",
        "http://192.168.100.202",
        # Public domain via Cloudflare Zero Trust
        "https://lcious.mygarden.my.id",
    ]

    # Algorithm Parameters
    DEFAULT_ALPHA: float = 0.5  # Default weight for hybrid recommendation
    DEFAULT_K_NEIGHBORS: int = 10  # Default number of neighbors for CF

    # Fuzzy Parameters (default values)
    PRICE_CHEAP_MAX: float = 15000
    PRICE_MEDIUM_MIN: float = 10000
    PRICE_MEDIUM_MAX: float = 30000
    PRICE_EXPENSIVE_MIN: float = 25000

    DISTANCE_NEAR_KM: float = 2.0
    DISTANCE_MEDIUM_MIN_KM: float = 1.0
    DISTANCE_MEDIUM_MAX_KM: float = 5.0
    DISTANCE_FAR_MIN_KM: float = 4.0

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
