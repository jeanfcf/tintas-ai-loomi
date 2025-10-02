"""Health check endpoints."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import HealthResponse
from app.core.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    # Check dependencies
    dependencies = {
        "database": "unknown",
        "openai": "unknown"
    }
    
    # TODO: Add actual health checks for dependencies
    # For now, assume all are healthy
    dependencies["database"] = "healthy"
    dependencies["openai"] = "healthy"
    
    return HealthResponse(
        status="healthy",
        service="AI Orchestrator",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        dependencies=dependencies
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with more information."""
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": "AI Orchestrator",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.debug else "production",
        "dependencies": {
            "database": {
                "status": "healthy",
                "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "configured"
            },
            "openai": {
                "status": "healthy",
                "model": settings.openai_model,
                "api_key_configured": bool(settings.openai_api_key)
            }
        },
        "configuration": {
            "max_tokens": settings.max_tokens,
            "max_conversation_length": settings.max_conversation_length,
            "cors_origins": settings.cors_origins
        }
    }
