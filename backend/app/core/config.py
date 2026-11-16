from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Textile Waste Management Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "dev-secret-key-change-in-production-092837492837"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    DATABASE_URL: str = "sqlite:///./textile_waste.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600

    RATE_LIMIT_LOGIN_PER_MINUTE: int = 15
    RATE_LIMIT_SCAN_PER_MINUTE: int = 40

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    DEFECT_CONFIDENCE_THRESHOLD: float = 0.45
    AI_UNCERTAINTY_MARGIN: float = 0.20
    AI_UNCERTAINTY_ENTROPY: float = 0.70
    MATERIAL_MODEL_VERSION: str = "v1.0-uncalibrated-option-b"
    DEFECT_MODEL_VERSION: str = "v1.0-provisional-0.45"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
