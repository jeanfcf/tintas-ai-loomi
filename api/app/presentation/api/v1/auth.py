"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domain.entities import LoginRequest, Token, UserResponse
from app.infrastructure.middleware import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials
from app.core.logging import get_logger
from app.core.container import container

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token, summary="User Login")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token."""
    try:
        auth_service = container.get_auth_application_service()
        token = auth_service.login(db, login_data)
        logger.info(f"User login - username: {login_data.username}")
        return token
        
    except ValueError as e:
        error_msg = f"Login validation failed: {e}"
        logger.warning(f"{error_msg} - username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    except Exception as e:
        error_msg = f"Unexpected error during login: {e}"
        logger.error(f"{error_msg} - username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse, summary="Get Current User")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user information."""
    current_user = await get_current_user(credentials, db)
    return current_user


@router.post("/logout", summary="User Logout")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Successfully logged out"}
