"""Authentication middleware for AI Orchestrator."""
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from app.core.auth import JWTService
from app.core.logging import AILogger

logger = AILogger(__name__)

security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication."""
    
    def __init__(self, app):
        super().__init__(app)
        self.jwt_service = JWTService()
        self.public_endpoints = [
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/test-token"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            response = await call_next(request)
            return response
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.log_error(
                error=Exception("Missing or invalid authorization header"),
                context={"path": request.url.path, "method": request.method}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        # Verify token
        token_payload = self.jwt_service.verify_token(token)
        if not token_payload:
            logger.log_error(
                error=Exception("Invalid or expired token"),
                context={"path": request.url.path, "method": request.method}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check permissions based on endpoint
        required_permission = self._get_required_permission(request.url.path)
        if required_permission and not self.jwt_service.has_permission(token_payload, required_permission):
            logger.log_error(
                error=Exception("Insufficient permissions"),
                context={
                    "path": request.url.path,
                    "method": request.method,
                    "required_permission": required_permission,
                    "token_permissions": token_payload.get("permissions", [])
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission}"
            )
        
        # Add token info to request state
        request.state.auth_service = token_payload.get("service_name")
        request.state.auth_permissions = token_payload.get("permissions", [])
        
        logger.log_tool_execution(
            tool_name="auth_middleware",
            input_params={"path": request.url.path, "service": token_payload.get("service_name")},
            output="Authentication successful",
            execution_time=0.0
        )
        
        response = await call_next(request)
        return response
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)."""
        return any(path.startswith(endpoint) for endpoint in self.public_endpoints)
    
    def _get_required_permission(self, path: str) -> Optional[str]:
        """Get required permission for endpoint."""
        if "/chat" in path:
            return "chat"
        elif "/rag" in path:
            return "rag"
        elif "/embeddings" in path:
            return "write"
        else:
            return "read"


async def get_current_service(request: Request) -> dict:
    """Dependency to get current authenticated service."""
    if not hasattr(request.state, 'auth_service'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "service_name": request.state.auth_service,
        "permissions": getattr(request.state, 'auth_permissions', [])
    }
