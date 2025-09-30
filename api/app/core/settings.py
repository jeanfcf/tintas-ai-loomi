"""Application settings."""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: Optional[str] = Field(default=None, env="DATABASE_URL")
    db_host: str = Field(default="postgres", env="DATABASE_HOST")
    db_port: int = Field(default=5432, env="DATABASE_PORT")
    db_name: str = Field(default="tintas_ai_db", env="DATABASE_NAME")
    db_user: str = Field(default="tintas_user", env="DATABASE_USER")
    db_password: str = Field(default="tintas_secure_password_2024", env="DATABASE_PASSWORD")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.url:
            self.url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = {
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False
    }


class AppSettings(BaseSettings):
    """Application configuration."""
    name: str = Field(default="Tintas AI Loomi", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    description: str = Field(default="API for paint system with AI", env="APP_DESCRIPTION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    model_config = {
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False
    }


class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default="change-this-secret-key-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    model_config = {
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False
    }


class CORSSettings(BaseSettings):
    """CORS configuration."""
    origins: str = Field(default="http://localhost:3000,http://localhost:3001", env="CORS_ORIGINS")
    methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="CORS_METHODS")
    headers: str = Field(default="*", env="CORS_HEADERS")
    
    @property
    def origins_list(self) -> list:
        return [origin.strip() for origin in self.origins.split(",")]
    
    @property
    def methods_list(self) -> list:
        return [method.strip() for method in self.methods.split(",")]
    
    @property
    def headers_list(self) -> list:
        return [header.strip() for header in self.headers.split(",")]
    
    model_config = {
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": False
    }


class Settings:
    """Main settings container."""
    
    def __init__(self):
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        
        self.database = DatabaseSettings()
        self.app = AppSettings()
        self.security = SecuritySettings()
        self.cors = CORSSettings()
    
    @property
    def is_development(self) -> bool:
        return self.app.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app.environment == "production"


settings = Settings()
