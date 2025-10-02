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
                logger.warning("Authentication failed: Invalid token")
                raise credentials_exception

            user = self.user_service.get_user(db, token_data.user_id)
            if user is None:
                logger.warning(f"Authentication failed: User not found for user_id: {token_data.user_id}")
                raise credentials_exception

            return user
            
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"Authentication service error: {e}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
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
            
            logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request error: {e} ({process_time:.3f}s)")
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
    
    app.add_middleware(QueryParameterValidationMiddleware)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_current_admin_user: Exception type: {type(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency to get current user (optional - returns None if not authenticated)."""
    if credentials is None:
        return None
    
    try:
        return await auth_service.get_current_user(credentials, db)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"get_current_user_optional: Could not validate credentials: {e}")
        return None


class QueryParameterValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate query parameters and prevent backend errors."""
    
    async def dispatch(self, request: Request, call_next):
        """Validate query parameters before processing."""
        try:
            # Only validate paint endpoints
            if request.url.path.startswith("/api/v1/paints/") and request.method == "GET":
                await self._validate_paint_query_params(request)
            
            response = await call_next(request)
            return response
            
        except ValueError as e:
            logger.warning(f"Query parameter validation failed: {e}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error in query validation middleware: {e}")
            # Don't break the request, just log and continue
            try:
                response = await call_next(request)
                return response
            except Exception as call_error:
                logger.error(f"Error calling next middleware: {call_error}")
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )
    
    async def _validate_paint_query_params(self, request: Request):
        """Validate paint query parameters."""
        query_params = request.query_params
        
        # Basic validation - just check for extremely long parameters
        for param_name, param_value in query_params.items():
            if len(param_value) > 1000:  # Very generous limit
                raise ValueError(f"Parameter {param_name} is too long")
        
        # Validate skip parameter
        skip = query_params.get("skip", "0")
        try:
            skip_int = int(skip)
            if skip_int < 0:
                raise ValueError("Skip parameter must be non-negative")
        except ValueError:
            raise ValueError("Skip parameter must be a valid integer")
        
        # Validate limit parameter
        limit = query_params.get("limit", "100")
        try:
            limit_int = int(limit)
            if limit_int < 1:
                raise ValueError("Limit parameter must be at least 1")
            if limit_int > 1000:
                raise ValueError("Limit parameter must be no more than 1000")
        except ValueError:
            raise ValueError("Limit parameter must be a valid integer")


