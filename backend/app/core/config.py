from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str = "change_this_to_a_long_random_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Uploads
    UPLOAD_DIR: str = "uploads/screenshots"
    MAX_UPLOAD_SIZE_MB: int = 5

    # Payments
    PAYMENT_GRACE_DAYS: int = 15
    DEFAULT_PAYMENT_AMOUNT: float = 1000.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
