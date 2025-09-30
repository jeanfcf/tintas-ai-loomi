"""Simple script to run the API."""
import uvicorn
import sys
import os

log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/app.log")
log_format = os.getenv("LOG_FORMAT", "json")
log_max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))
log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

from app.core.logging import setup_logging, get_logger
setup_logging(
    log_level=log_level,
    log_file=log_file,
    log_format=log_format,
    max_bytes=log_max_bytes,
    backup_count=log_backup_count
)

from app.core.settings import settings

logger = get_logger(__name__)

if __name__ == "__main__":
    try:
        logger.info(f"Starting API server on {settings.app.host}:{settings.app.port}")
        
        log_config = None
        
        uvicorn.run(
            "main:app",
            host=settings.app.host,
            port=settings.app.port,
            log_level=log_level.lower(),
            reload=settings.is_development,
            access_log=True,
            log_config=log_config
        )
        
    except KeyboardInterrupt:
        logger.info("API stopped")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Failed to start API: {e}"
        logger.error(error_msg)
        sys.exit(1)
