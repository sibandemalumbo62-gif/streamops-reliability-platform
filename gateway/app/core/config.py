from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Service URLs
    AUTH_SERVICE_URL: str
    CATALOG_SERVICE_URL: str
    PLAYBACK_SERVICE_URL: str
    RECOMMENDATION_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str
    INTEGRITY_SERVICE_URL: str


    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"


    # Gateway Settings
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100

    HOST: str = "0.0.0.0"
    PORT: int = 8000


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()