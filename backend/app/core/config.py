import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Agent OnboardX API"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    JWT_SECRET_KEY: str = Field(default="super_secret_key_for_development_purposes_only", validation_alias="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(default="super_refresh_secret_key_for_development", validation_alias="JWT_REFRESH_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:1234@localhost:5432/agent_onboardx", validation_alias="DATABASE_URL")
    
    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="models/gemma-4-31b-it", validation_alias="GEMINI_MODEL")
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "https://agent-onboardx.vercel.app"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
