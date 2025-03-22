from pydantic_settings import BaseSettings
from functools import lru_cache
from src.constants import RedisChannels

class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "bAIby Core"
    VERSION: str = "1.0.0"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # analysis expiration time
    ANALYSIS_EXPIRATION_TIME: int = 10
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    # Redis channels
    REDIS_CHANNELS = RedisChannels
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 