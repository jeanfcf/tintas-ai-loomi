"""Repository interfaces."""
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities import User, UserCreate, UserUpdate, UserFilters, PaginationParams


class UserRepositoryInterface(ABC):
    """User repository interface."""

    @abstractmethod
    def create(self, db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_all(self, db: Session, pagination: PaginationParams, filters: UserFilters) -> List[User]:
        """Get all users with pagination and filters."""
        pass

    @abstractmethod
    def count_all(self, db: Session, filters: UserFilters) -> int:
        """Count all users matching filters."""
        pass

    @abstractmethod
    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        pass

    @abstractmethod
    def delete(self, db: Session, user_id: int) -> bool:
        """Soft delete user."""
        pass


    @abstractmethod
    def exists_by_email(self, db: Session, email: str) -> bool:
        """Check if user exists by email."""
        pass

    @abstractmethod
    def exists_by_username(self, db: Session, username: str) -> bool:
        """Check if user exists by username."""
        pass

    @abstractmethod
    def exists_active_by_email(self, db: Session, email: str) -> bool:
        """Check if active user exists by email."""
        pass

    @abstractmethod
    def exists_active_by_username(self, db: Session, username: str) -> bool:
        """Check if active user exists by username."""
        pass

    @abstractmethod
    def update_last_login(self, db: Session, user_id: int) -> None:
        """Update user's last login timestamp."""
        pass

    @abstractmethod
    def get_user_with_password(self, db: Session, username: str) -> Optional[tuple[User, str]]:
        """Get user with hashed password."""
        pass
