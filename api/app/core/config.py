"""
App configuration.
"""
import logging
import sys
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path
import structlog
from pythonjsonlogger import jsonlogger


class Settings(BaseSettings):
    """App settings from environment."""
    
    # Application Settings
    app_name: str = "Tintas AI Loomi"
    app_version: str = "1.0.0"
    app_description: str = "API for paint system with AI"
    debug: bool = False
    environment: str = "production"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/tintas_ai_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "tintas_ai_db"
    database_user: str = "user"
    database_password: str = "password"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/app.log"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors_headers: List[str] = ["*"]
    
    # External APIs
    external_api_url: Optional[str] = None
    external_api_key: Optional[str] = None
    
    # Monitoring and Health Check
    health_check_interval: int = 30
    health_check_timeout: int = 5
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v):
        allowed_formats = ["json", "text"]
        if v not in allowed_formats:
            raise ValueError(f"Log format must be one of {allowed_formats}")
        return v
    
    @property
    def database_url_parsed(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    def setup_logging(self):
        """Setup logging system."""
        # Create logs directory
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure structlog
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        if self.log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure default logging
        handlers = []
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        if self.log_format == "json":
            file_handler.setFormatter(jsonlogger.JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
        handlers.append(file_handler)
        
        # Console handler (development only)
        if self.is_development:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            handlers.append(console_handler)
        
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            handlers=handlers,
            force=True
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
settings.setup_logging()


def get_logger(name: str):
    """Get configured logger."""
    return structlog.get_logger(name)
