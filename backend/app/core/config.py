from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings.
    
    These settings are loaded from environment variables and/or .env files.
    """
    # Base
    APP_NAME: str = "Roll Call by AI"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=False)
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(default="mysql+aiomysql://root:password@localhost:3306/rollcall", env="DATABASE_URL")
    DATABASE_NAME: str = Field(default="rollcall", env="DATABASE_NAME")
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

@lru_cache()
def get_settings() -> Settings:
    """Get application settings as a cached singleton."""
    return Settings()

settings = get_settings()