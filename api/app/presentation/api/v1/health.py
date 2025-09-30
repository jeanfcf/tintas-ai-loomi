"""
Health check routes and main API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.infrastructure.database import get_db, check_database_connection
from app.core.config import get_logger, settings

logger = get_logger(__name__)

# Main API router
api_router = APIRouter()

# Health check routes
health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", 
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
    """
    Complete application health check endpoint.
    
    This endpoint performs a comprehensive health check of the application including:
    
    **Services Checked:**
    - Application runtime status
    - Database connectivity
    - Service availability
    
    **Response Codes:**
    - `200 OK`: All services are healthy and operational
    - `503 Service Unavailable`: One or more services are down or unreachable
    
    **Use Cases:**
    - Load balancer health checks
    - Monitoring system probes
    - Service discovery health verification
    - Container orchestration health checks
    
    **Response Fields:**
    - `status`: Overall health status ("healthy" or "unhealthy")
    - `message`: Human-readable status message
    - `version`: Current API version
    - `environment`: Current environment (development/staging/production)
    - `services`: Status of individual services
    - `timestamp`: When the health check was performed
    """
    logger.debug("Health check requested")
    
    # Check database
    db_healthy = check_database_connection()
    
    if not db_healthy:
        logger.error("Database connection failed during health check")
        raise HTTPException(status_code=503, detail="Database is not available")
    
    from datetime import datetime
    return {
        "status": "healthy",
        "message": "API is running",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {"database": "healthy"},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Include health check routes
api_router.include_router(health_router)
