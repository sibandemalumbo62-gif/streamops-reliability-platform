from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Playback Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/playback_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    STREAM_TIMEOUT_MINUTES: int = 120
    MAX_CONCURRENT_STREAMS: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
