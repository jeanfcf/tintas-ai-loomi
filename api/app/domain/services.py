"""Domain services."""
from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities import User, UserCreate, UserUpdate, LoginRequest, Token, TokenData, UserFilters, PaginationParams, PaginatedResponse


class AuthServiceInterface(ABC):
    """Authentication service interface."""

    @abstractmethod
    def authenticate_user(self, db: Session, login_data: LoginRequest) -> Optional[User]:
        """Authenticate user with username and password."""
        pass

    @abstractmethod
    def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token."""
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        pass


class UserServiceInterface(ABC):
    """User service interface."""

    @abstractmethod
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_users(self, db: Session, pagination: PaginationParams, filters: UserFilters) -> PaginatedResponse:
        """Get all users with pagination and filters."""
        pass

    @abstractmethod
    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        pass

    @abstractmethod
    def delete_user(self, db: Session, user_id: int) -> bool:
        """Soft delete user."""
        pass

    @abstractmethod
    def update_last_login(self, db: Session, user_id: int) -> None:
        """Update user's last login timestamp."""
        pass


class AuthApplicationServiceInterface(ABC):
    """Authentication application service interface."""

    @abstractmethod
    def login(self, db: Session, login_data: LoginRequest) -> Token:
        """Authenticate user and return token."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token."""
        pass
