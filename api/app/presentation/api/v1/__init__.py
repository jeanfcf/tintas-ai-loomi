"""
API v1 router configuration.
"""
from fastapi import APIRouter

from .health import health_router
from .auth import router as auth_router
from .users import router as users_router
from .paints import router as paints_router
from .chat import router as chat_router

# Main API v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(paints_router)
api_router.include_router(chat_router)
