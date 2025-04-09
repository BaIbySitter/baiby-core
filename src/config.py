from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import ClassVar, Optional
from src.constants import RedisChannels

class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "bAIby Core"
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CHANNELS: ClassVar[RedisChannels] = RedisChannels

    # Supabase settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Analysis settings
    ANALYSIS_EXPIRATION_TIME: int = 3600  # segundos
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 