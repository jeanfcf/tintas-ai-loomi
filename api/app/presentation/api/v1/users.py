"""User management routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database import get_db
from app.domain.entities import User, UserCreate, UserUpdate, UserResponse, UserFilters, PaginationParams, PaginatedResponse
from app.infrastructure.middleware import get_current_admin_user
from app.core.logging import get_logger
from app.core.container import container

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create User")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        user_service = container.get_user_service()
        user = user_service.create_user(db, user_data)
        
        logger.info(f"User created - username: {user.username}")
        return user
        
    except ValueError as e:
        logger.warning(f"User creation validation failed: {e} - username: {user_data.username}, email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e} - username: {user_data.username}, email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=PaginatedResponse, summary="Get All Users")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    search: str = Query("", description="Search term for username, email, or full name"),
    role: str = Query("", description="Filter by user role (user, admin)"),
    status: str = Query("", description="Filter by user status (active, inactive)"),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination and filters."""
    try:
        pagination = PaginationParams(skip=skip, limit=limit)
        filters = UserFilters(
            search=search if search else None,
            role=role if role else None,
            status=status if status else None
        )
        
        user_service = container.get_user_service()
        result = user_service.get_users(db, pagination, filters)
        return result
    except ValueError as e:
        logger.warning(f"Get users validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get users error - error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}", response_model=UserResponse, summary="Get User by ID")
async def get_user(
    user_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    try:
        user_service = container.get_user_service()
        user = user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error - error: {str(e)}, user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{user_id}", response_model=UserResponse, summary="Update User")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user."""
    try:
        user_service = container.get_user_service()
        user = user_service.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User updated - user_id: {user_id}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error - error: {str(e)}, user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft Delete User")
async def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Soft delete user."""
    try:
        user_service = container.get_user_service()
        success = user_service.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User deleted - user_id: {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error - error: {str(e)}, user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
