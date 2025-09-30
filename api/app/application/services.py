"""Application services."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities import User, UserCreate, UserUpdate, LoginRequest, Token, TokenData, UserRole, UserFilters, PaginationParams, PaginatedResponse
from app.domain.services import UserServiceInterface, AuthServiceInterface, AuthApplicationServiceInterface
from app.domain.repositories import UserRepositoryInterface
from app.core.logging import get_logger
from app.core.settings import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

logger = get_logger(__name__)


class AuthService(AuthServiceInterface):
    """Authentication service implementation."""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            deprecated="auto",
            pbkdf2_sha256__default_rounds=290000
        )
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.access_token_expire_minutes = settings.security.access_token_expire_minutes

    def authenticate_user(self, db: Session, login_data: LoginRequest, user_repo: UserRepositoryInterface) -> Optional[User]:
        """Authenticate user with username and password."""
        result = user_repo.get_user_with_password(db, login_data.username)
        
        if not result:
            return None
            
        user, hashed_password = result
        if not self.verify_password(login_data.password, hashed_password):
            return None
            
        return user

    def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "exp": expire
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            role: str = payload.get("role")
            
            if user_id is None or username is None or role is None:
                return None
                
            return TokenData(
                user_id=int(user_id),
                username=username,
                role=UserRole(role)
            )
        except JWTError:
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2-SHA256."""
        try:
            return self.pwd_context.hash(password)
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError(f"Password hashing failed: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)


class UserService(UserServiceInterface):
    """User service implementation."""

    def __init__(self, user_repo: UserRepositoryInterface, auth_service: AuthServiceInterface):
        self.user_repo = user_repo
        self.auth_service = auth_service

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            from app.domain.validators import UserValidator
            UserValidator.validate_create_data(user_data)

            if self.user_repo.exists_active_by_email(db, user_data.email):
                raise ValueError("User with this email already exists")

            if self.user_repo.exists_active_by_username(db, user_data.username):
                raise ValueError("User with this username already exists")

            hashed_password = self.auth_service.hash_password(user_data.password)
            user = self.user_repo.create(db, user_data, hashed_password)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error creating user: {e}"
            logger.error(f"{error_msg} - username: {user_data.username}, email: {user_data.email}")
            raise Exception(error_msg)

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repo.get_by_email(db, email)

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return self.user_repo.get_by_username(db, username)

    def get_users(self, db: Session, pagination: PaginationParams, filters: UserFilters) -> PaginatedResponse:
        """Get all users with pagination and filters."""
        users = self.user_repo.get_all(db, pagination, filters)
        total = self.user_repo.count_all(db, filters)
        
        return PaginatedResponse(
            items=users,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_next=pagination.skip + pagination.limit < total,
            has_prev=pagination.skip > 0
        )

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        try:
            from app.domain.validators import UserValidator
            UserValidator.validate_update_data(user_data)
            
            if user_data.password and user_data.password.strip():
                hashed_password = self.auth_service.hash_password(user_data.password)
                
                from app.domain.entities import UserUpdate
                update_data = UserUpdate(
                    email=user_data.email,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    role=user_data.role,
                    status=user_data.status,
                    password=hashed_password
                )
                return self.user_repo.update(db, user_id, update_data)
            else:
                return self.user_repo.update(db, user_id, user_data)
                
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error updating user: {e}"
            logger.error(f"{error_msg} - user_id: {user_id}")
            raise Exception(error_msg)

    def delete_user(self, db: Session, user_id: int) -> bool:
        """Soft delete user."""
        return self.user_repo.delete(db, user_id)


    def update_last_login(self, db: Session, user_id: int) -> None:
        """Update user's last login timestamp."""
        self.user_repo.update_last_login(db, user_id)


class AuthApplicationService(AuthApplicationServiceInterface):
    """Authentication application service."""

    def __init__(self, auth_service: AuthServiceInterface, user_service: UserServiceInterface):
        self.auth_service = auth_service
        self.user_service = user_service

    def login(self, db: Session, login_data: LoginRequest) -> Token:
        """Authenticate user and return token."""
        try:
            user = self.auth_service.authenticate_user(db, login_data, self.user_service.user_repo)
            if not user:
                raise ValueError("Invalid username or password")

            self.user_service.update_last_login(db, user.id)
            access_token = self.auth_service.create_access_token(user)
            
            logger.info(f"User login - username: {user.username}")
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.auth_service.access_token_expire_minutes * 60
            )
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during login: {e}"
            logger.error(f"{error_msg} - username: {login_data.username}")
            raise Exception(error_msg)

    def verify_token(self, token: str):
        """Verify token and return token data."""
        return self.auth_service.verify_token(token)
