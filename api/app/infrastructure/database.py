"""
Database configuration and middleware.
"""
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

from app.core.config import settings, get_logger

logger = get_logger(__name__)

# Database engine configuration
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.is_development,
    future=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for SQLAlchemy models
Base = declarative_base()

# Metadata for Alembic
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        logger.debug("Database session closed")
        db.close()


def create_tables() -> None:
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Error creating database tables", error=str(e))
        raise


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP request logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log it."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        logger.info(
            "Request received",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            request_id=request_id,
            client_ip=request.client.host if request.client else None
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                "HTTP Request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time=process_time,
                request_id=request_id
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Application Error",
                error_type=type(e).__name__,
                error_message=str(e),
                method=request.method,
                path=request.url.path,
                response_time=process_time,
                request_id=request_id,
                exc_info=True
            )
            raise


def setup_middleware(app):
    """Setup all app middlewares."""
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
