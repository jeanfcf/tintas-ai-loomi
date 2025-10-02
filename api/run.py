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
        logger.info(f"Starting server on {settings.app.host}:{settings.app.port}")
        
        uvicorn.run(
            "main:app",
            host=settings.app.host,
            port=settings.app.port,
            log_level=log_level.lower(),
            reload=settings.is_development,
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server start failed: {e}")
        sys.exit(1)
