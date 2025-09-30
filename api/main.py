"""
Main API for Suvinil system.
"""
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.core.config import settings, get_logger
from app.infrastructure.database import (
    create_tables, check_database_connection, setup_middleware
)
from app.presentation.api.v1.health import api_router

logger = get_logger(__name__)


class RootResponse(BaseModel):
    """Response model for root endpoint."""
    message: str
    version: str
    description: str
    environment: str
    docs: str
    redoc: str
    openapi: str
    warning: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Welcome to Tintas AI Loomi",
                "version": "1.0.0",
                "description": "API for paint system with AI",
                "environment": "production",
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
                "warning": "Production environment - docs visible"
            }
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown."""
    logger.info("Starting app", version=settings.app_version)
    
    if settings.is_production:
        logger.warning("Production mode - docs visible at /docs")
    
    if not check_database_connection():
        logger.error("DB connection failed")
        raise Exception("Database connection failed")
    
    try:
        create_tables()
        logger.info("DB tables ready")
    except Exception as e:
        logger.error("Failed to create tables", error=str(e))
        raise
    
    logger.info("App started")
    yield
    
    logger.info("Shutting down")


def create_app() -> FastAPI:
    """Create FastAPI app."""
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc", 
        openapi_url="/openapi.json",
        contact={
            "name": "Tintas AI Loomi Team",
            "email": "support@tintas-ai-loomi.com",
            "url": "https://tintas-ai-loomi.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.tintas-ai-loomi.com",
                "description": "Production server"
            }
        ],
        openapi_tags=[
            {
                "name": "root",
                "description": "Root endpoint with API information and documentation links"
            },
            {
                "name": "health",
                "description": "Health check endpoints for monitoring and service status"
            },
            {
                "name": "documentation",
                "description": "API documentation endpoints (Swagger UI, ReDoc, OpenAPI schema)"
            }
        ]
    )
    
    setup_middleware(app)
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request, exc):
        request_id = getattr(request.state, "request_id", None)
        logger.error("DB error", error=str(exc), request_id=request_id)
        return HTTPException(status_code=500, detail="Database error occurred")
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        request_id = getattr(request.state, "request_id", None)
        logger.error("Unhandled error", error=str(exc), request_id=request_id)
        return HTTPException(status_code=500, detail="Internal server error")
    
    app.include_router(api_router)
    
    @app.get("/", 
             tags=["root"],
             summary="API Root",
             description="Welcome endpoint with API information and available documentation links",
             response_description="API information and available endpoints",
             response_model=RootResponse)
    async def root():
        """
        Welcome endpoint that provides:
        - API name and version
        - Links to documentation (Swagger UI and ReDoc)
        - Environment warnings if in production
        """
        response = {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "description": settings.app_description,
            "environment": settings.environment,
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
        
        if settings.is_production:
            response["warning"] = "Production environment - docs visible"
        
        return response

    @app.get("/docs",
             tags=["documentation"],
             summary="Swagger UI Documentation",
             description="Interactive API documentation using Swagger UI. This endpoint provides a user-friendly interface to explore and test all available API endpoints.",
             response_description="Swagger UI interface for API documentation")
    async def swagger_docs():
        """
        Swagger UI Documentation
        
        This endpoint serves the Swagger UI interface which provides:
        - Interactive API documentation
        - Endpoint testing capabilities
        - Request/response examples
        - Schema definitions
        - Authentication testing (if configured)
        
        The interface is automatically generated from the OpenAPI schema.
        """
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")

    @app.get("/redoc",
             tags=["documentation"],
             summary="ReDoc Documentation",
             description="Clean and elegant API documentation using ReDoc. This endpoint provides a more readable and organized view of the API documentation.",
             response_description="ReDoc interface for API documentation")
    async def redoc_docs():
        """
        ReDoc Documentation
        
        This endpoint serves the ReDoc interface which provides:
        - Clean and elegant documentation layout
        - Better readability for API reference
        - Organized endpoint grouping
        - Detailed schema information
        - Search functionality
        
        ReDoc is particularly useful for:
        - API reference documentation
        - Developer onboarding
        - Technical documentation
        """
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/redoc")

    @app.get("/openapi.json",
             tags=["documentation"],
             summary="OpenAPI Schema",
             description="Complete OpenAPI 3.0 schema in JSON format. This endpoint provides the raw API specification that can be used by various tools and clients.",
             response_description="OpenAPI 3.0 schema in JSON format")
    async def openapi_schema():
        """
        OpenAPI Schema
        
        This endpoint provides the complete OpenAPI 3.0 specification including:
        - All API endpoints and their definitions
        - Request/response schemas
        - Authentication requirements
        - Server information
        - Tags and categories
        
        The schema can be used by:
        - API testing tools (Postman, Insomnia)
        - Code generation tools
        - API gateway configurations
        - Client SDK generation
        """
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/openapi.json")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower()
        )
