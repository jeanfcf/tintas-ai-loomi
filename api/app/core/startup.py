"""Application startup and shutdown management."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings import settings
from app.core.logging import get_logger
from app.infrastructure.middleware import setup_middleware
from init import initialize_system

logger = get_logger(__name__)


class ApplicationStartup:
    """Handles application startup and shutdown logic."""
    
    def __init__(self, settings):
        self.settings = settings
    
    async def startup(self) -> None:
        """Initialize application on startup."""
        try:
            logger.info(f"Starting application v{self.settings.app.version}")
            
            if self.settings.is_production:
                logger.warning("Running in production mode")
            
            if not initialize_system():
                logger.error("System initialization failed")
                raise Exception("System initialization failed")
            
            logger.info("Generating paint embeddings...")
            from init import generate_missing_embeddings
            await generate_missing_embeddings()
            
            logger.info("Application started successfully")
            
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Cleanup on application shutdown."""
        try:
            logger.info("Application shutdown")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


def create_lifespan() -> asynccontextmanager:
    """Create lifespan context manager for FastAPI."""
    startup_handler = ApplicationStartup(settings)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await startup_handler.startup()
        yield
        await startup_handler.shutdown()
    
    return lifespan


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers."""
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request, exc):
        logger.error(f"Database error: {exc}")
        return HTTPException(status_code=500, detail="Database error occurred")
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled error: {exc}")
        return HTTPException(status_code=500, detail="Internal server error")


def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application."""
    from pydantic import BaseModel
    from typing import Optional
    from app.presentation.api.v1 import api_router
    
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
            json_schema_extra = {
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
    
    app = FastAPI(
        title=settings.app.name,
        description=settings.app.description,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=create_lifespan(),
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
    setup_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    @app.get("/", 
             tags=["root"],
             summary="API Root",
             description="Welcome endpoint with API information and available documentation links",
             response_description="API information and available endpoints",
             response_model=RootResponse)
    async def root():
        """Welcome endpoint with API information and documentation links."""
        response = {
            "message": f"Welcome to {settings.app.name}",
            "version": settings.app.version,
            "description": settings.app.description,
            "environment": settings.app.environment,
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
        """Swagger UI Documentation endpoint."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")

    @app.get("/redoc",
             tags=["documentation"],
             summary="ReDoc Documentation",
             description="Clean and elegant API documentation using ReDoc. This endpoint provides a more readable and organized view of the API documentation.",
             response_description="ReDoc interface for API documentation")
    async def redoc_docs():
        """ReDoc Documentation endpoint."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/redoc")

    @app.get("/openapi.json",
             tags=["documentation"],
             summary="OpenAPI Schema",
             description="Complete OpenAPI 3.0 schema in JSON format. This endpoint provides the raw API specification that can be used by various tools and clients.",
             response_description="OpenAPI 3.0 schema in JSON format")
    async def openapi_schema():
        """OpenAPI Schema endpoint."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/openapi.json")
    
    return app
