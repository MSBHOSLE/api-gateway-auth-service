from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _USE_PYDANTIC = True
except ImportError:
    _USE_PYDANTIC = False
    class BaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    SettingsConfigDict = dict


class Settings(BaseSettings):
    APP_NAME: str = "API Gateway & Auth Service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8080
    HOST: str = "0.0.0.0"

    # JWT Authentication
    JWT_SECRET: str = "super-secret-jwt-key-for-development-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting (Sliding Window)
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Persistence
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    if _USE_PYDANTIC:
        model_config = SettingsConfigDict(
            env_file=".env",
            case_sensitive=False,
            extra="ignore",
        )


settings = Settings()
