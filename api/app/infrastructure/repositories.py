"""Repository implementations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.entities import User, UserCreate, UserUpdate, UserFilters, PaginationParams
from app.domain.repositories import UserRepositoryInterface
from app.infrastructure.models import UserModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository(UserRepositoryInterface):
    """User repository implementation."""

    def create(self, db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        try:
            db_user = UserModel(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=user_data.role,
                status=user_data.status if hasattr(user_data, 'status') else None
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return self._model_to_entity(db_user)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error creating user: {e}"
            logger.error(f"{error_msg} - username: {user_data.username}, email: {user_data.email}")
            raise Exception(error_msg)

    def _get_active_user_query(self, db: Session):
        """Get base query for active users."""
        return db.query(UserModel).filter(UserModel.deleted_at.is_(None))

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        db_user = self._get_active_user_query(db).filter(UserModel.id == user_id).first()
        return self._model_to_entity(db_user) if db_user else None

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        db_user = self._get_active_user_query(db).filter(UserModel.email == email).first()
        return self._model_to_entity(db_user) if db_user else None

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        db_user = self._get_active_user_query(db).filter(UserModel.username == username).first()
        return self._model_to_entity(db_user) if db_user else None

    def get_all(self, db: Session, pagination: PaginationParams, filters: UserFilters) -> List[User]:
        """Get all users with pagination and filters."""
        query = self._get_active_user_query(db)
        query = self._apply_filters(query, filters)
        
        db_users = query.offset(pagination.skip).limit(pagination.limit).all()
        return [self._model_to_entity(db_user) for db_user in db_users]

    def count_all(self, db: Session, filters: UserFilters) -> int:
        """Count all users matching filters."""
        query = self._get_active_user_query(db)
        query = self._apply_filters(query, filters)
        return query.count()

    def _apply_filters(self, query, filters: UserFilters):
        """Apply filters to query."""
        if not filters.is_empty():
            if filters.search:
                search_term = f"%{filters.search.lower()}%"
                query = query.filter(
                    or_(
                        UserModel.username.ilike(search_term),
                        UserModel.email.ilike(search_term),
                        UserModel.full_name.ilike(search_term)
                    )
                )
            
            if filters.role:
                query = query.filter(UserModel.role == filters.role)
            
            if filters.status:
                query = query.filter(UserModel.status == filters.status)
        
        return query

    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        db_user = self._get_active_user_query(db).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            model_field = 'hashed_password' if field == 'password' else field
            setattr(db_user, model_field, value)

        db.commit()
        db.refresh(db_user)
        return self._model_to_entity(db_user)

    def delete(self, db: Session, user_id: int) -> bool:
        """Soft delete user."""
        db_user = self._get_active_user_query(db).filter(UserModel.id == user_id).first()
        if not db_user:
            return False

        from datetime import datetime
        db_user.deleted_at = datetime.utcnow()
        db.commit()
        return True


    def exists_by_email(self, db: Session, email: str) -> bool:
        """Check if user exists by email."""
        db_user = db.query(UserModel).filter(UserModel.email == email).first()
        return db_user is not None

    def exists_by_username(self, db: Session, username: str) -> bool:
        """Check if user exists by username."""
        db_user = db.query(UserModel).filter(UserModel.username == username).first()
        return db_user is not None

    def exists_active_by_email(self, db: Session, email: str) -> bool:
        """Check if active user exists by email."""
        db_user = self._get_active_user_query(db).filter(UserModel.email == email).first()
        return db_user is not None

    def exists_active_by_username(self, db: Session, username: str) -> bool:
        """Check if active user exists by username."""
        db_user = self._get_active_user_query(db).filter(UserModel.username == username).first()
        return db_user is not None

    def update_last_login(self, db: Session, user_id: int) -> None:
        """Update user's last login timestamp."""
        db_user = self._get_active_user_query(db).filter(UserModel.id == user_id).first()
        if db_user:
            from datetime import datetime
            db_user.last_login = datetime.utcnow()
            db.commit()

    def get_user_with_password(self, db: Session, username: str) -> Optional[tuple[User, str]]:
        """Get user with hashed password."""
        db_user = self._get_active_user_query(db).filter(UserModel.username == username).first()
        
        if not db_user:
            return None
            
        user = self._model_to_entity(db_user)
        return user, db_user.hashed_password

    def _model_to_entity(self, db_user: UserModel) -> User:
        """Convert model to entity."""
        return User(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            role=db_user.role,
            status=db_user.status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            deleted_at=db_user.deleted_at,
            last_login=db_user.last_login
        )


