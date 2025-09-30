"""Middleware for security, CORS, and request logging."""
import time
import uuid
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from app.infrastructure.database import get_db
from app.domain.entities import User, UserRole, TokenData
from app.core.logging import get_logger
from app.core.container import container
from app.core.settings import settings

logger = get_logger(__name__)

security = HTTPBearer()


class AuthenticationService:
    """Service responsible for user authentication."""

    def __init__(self):
        self.auth_service = container.get_auth_service()
        self.user_service = container.get_user_service()

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials,
        db: Session
    ) -> User:
        """Get current authenticated user."""
        try:
            credentials_exception = HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

            token_data = self.auth_service.verify_token(credentials.credentials)
            if token_data is None:
                raise credentials_exception

            user = self.user_service.get_user(db, token_data.user_id)
            if user is None:
                raise credentials_exception

            return user
            
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"Authentication error: {e}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )


class AuthorizationService:
    """Service responsible for user authorization."""

    async def get_current_active_user(self, current_user: User) -> User:
        """Get current active user."""
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if current_user.status != "active":
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return current_user

    async def get_current_admin_user(self, current_user: User) -> User:
        """Get current admin user."""
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        return current_user


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP request logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log it."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"HTTP Request - method: {request.method}, path: {request.url.path}, status_code: {response.status_code}, response_time: {process_time}, request_id: {request_id}"
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Application Error - error_type: {type(e).__name__}, error_message: {str(e)}, method: {request.method}, path: {request.url.path}, response_time: {process_time}, request_id: {request_id}",
                exc_info=True
            )
            raise


def setup_middleware(app):
    """Setup all app middlewares."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins_list,
        allow_credentials=True,
        allow_methods=settings.cors.methods_list,
        allow_headers=settings.cors.headers_list,
    )
    
    app.add_middleware(RequestLoggingMiddleware)


auth_service = AuthenticationService()
authorization_service = AuthorizationService()
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    return await auth_service.get_current_user(credentials, db)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user."""
    return await authorization_service.get_current_active_user(current_user)


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current admin user."""
    
    try:
        current_user = await auth_service.get_current_user(credentials, db)
        admin_user = await authorization_service.get_current_admin_user(current_user)
        return admin_user
    except Exception as e:
        logger.error(f"get_current_admin_user: Exception type: {type(e)}")
        raise


