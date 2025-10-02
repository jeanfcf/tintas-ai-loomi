"""Logging configuration."""
import logging
import sys
from pathlib import Path
from typing import Optional


_logging_configured = False


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/app.log",
    log_format: str = "json",
    max_bytes: int = 10*1024*1024,
    backup_count: int = 5
) -> None:
    """Setup logging configuration."""
    global _logging_configured
    
    if _logging_configured:
        return
    
    _logging_configured = True
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    from pythonjsonlogger import jsonlogger
    file_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging system ready")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
