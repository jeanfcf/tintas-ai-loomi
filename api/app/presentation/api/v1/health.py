"""Health check routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.infrastructure.database import get_db, check_database_connection
from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("", 
                  response_model=Dict[str, Any],
                  summary="Health Check",
                  description="Complete application health check including database connectivity and service status",
                  response_description="Health status of the application and its services",
                  responses={
                      200: {
                          "description": "All services are healthy",
                          "content": {
                              "application/json": {
                                  "example": {
                                      "status": "healthy",
                                      "message": "API is running",
                                      "version": "1.0.0",
                                      "environment": "production",
                                      "services": {"database": "healthy"},
                                      "timestamp": "2024-01-01T00:00:00Z"
                                  }
                              }
                          }
                      },
                      503: {
                          "description": "One or more services are unavailable",
                          "content": {
                              "application/json": {
                                  "example": {
                                      "detail": "Database is not available"
                                  }
                              }
                          }
                      }
                  })
async def health_check():
    """Complete application health check endpoint."""
    
    db_healthy = check_database_connection()
    
    if not db_healthy:
        logger.error("Database connection failed during health check")
        raise HTTPException(status_code=503, detail="Database is not available")
    
    from datetime import datetime
    return {
        "status": "healthy",
        "message": "API is running",
        "version": settings.app.version,
        "environment": settings.app.environment,
        "services": {"database": "healthy"},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


