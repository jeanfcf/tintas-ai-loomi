"""Main application entry point."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.middleware.auth_middleware import AuthMiddleware
from app.api.v1 import chat, health

# Initialize logging and settings
setup_logging()
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Orchestrator - Paint Recommendations",
    description="Intelligent paint recommendation service with AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# Add API routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

# Serve generated images
import os
if os.path.exists("generated_images"):
    app.mount("/static/images", StaticFiles(directory="generated_images"), name="images")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Orchestrator",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
