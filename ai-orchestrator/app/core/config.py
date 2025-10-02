"""Application configuration."""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = Field(default="AI Orchestrator", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8001, env="PORT")
    
    # OpenAI settings
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    
    # Database settings
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis removed to simplify the system
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # JWT settings
    jwt_secret_key: str = Field(default="ai_orchestrator_secret_key_2024", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=1440, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API settings
    api_base_url: str = Field(default="http://api:8000", env="API_BASE_URL")
    ai_orchestrator_base_url: str = Field(default="http://localhost:8001", env="AI_ORCHESTRATOR_BASE_URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # AI settings
    max_tokens: int = Field(default=1500, env="MAX_TOKENS")
    max_conversation_length: int = Field(default=20, env="MAX_CONVERSATION_LENGTH")
    
    # Security settings
    secret_key: str = Field(default="change-this-secret-key", env="SECRET_KEY")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
