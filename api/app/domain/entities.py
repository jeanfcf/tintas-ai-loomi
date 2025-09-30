"""Domain entities."""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    """User roles."""
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """User entity."""
    id: Optional[int] = None
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserFilters(BaseModel):
    """User filters model."""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    
    def model_post_init(self, __context):
        from app.domain.validators import FilterValidator
        FilterValidator.validate_filters(self)
    
    def is_empty(self) -> bool:
        return not any([self.search, self.role, self.status])


class PaginationParams(BaseModel):
    """Pagination parameters model."""
    skip: int = 0
    limit: int = 100
    
    def model_post_init(self, __context):
        from app.domain.validators import PaginationValidator
        PaginationValidator.validate(self.skip, self.limit)


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[UserResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    
    def model_post_init(self, __context):
        from app.domain.validators import UsernameValidator, PasswordValidator
        UsernameValidator.validate(self.username)
        PasswordValidator.validate(self.password)


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data model."""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
