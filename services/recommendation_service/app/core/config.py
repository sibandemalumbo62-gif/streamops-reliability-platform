from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Recommendation Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/recommendation_db"
    
    RECOMMENDATION_COUNT: int = 20
    MIN_RATING_THRESHOLD: float = 7.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
