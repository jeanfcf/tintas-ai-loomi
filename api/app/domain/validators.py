"""Domain validators."""
import re
from typing import Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class PasswordValidator:
    """Password validation."""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @classmethod
    def validate(cls, password: str) -> None:
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < cls.MIN_LENGTH:
            raise ValueError(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        if len(password) > cls.MAX_LENGTH:
            raise ValueError(f"Password must be no more than {cls.MAX_LENGTH} characters long")


class EmailValidator:
    """Email validation."""
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def validate(cls, email: str) -> None:
        if not email:
            raise ValueError("Email is required")
        
        if not cls.EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format")


class UsernameValidator:
    """Username validation."""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @classmethod
    def validate(cls, username: str) -> None:
        if not username:
            raise ValueError("Username is required")
        
        if len(username) < cls.MIN_LENGTH:
            raise ValueError(f"Username must be at least {cls.MIN_LENGTH} characters long")
        
        if len(username) > cls.MAX_LENGTH:
            raise ValueError(f"Username must be no more than {cls.MAX_LENGTH} characters long")
        
        if not cls.USERNAME_REGEX.match(username):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")


class UserValidator:
    """User entity validation."""
    
    @staticmethod
    def validate_create_data(user_data) -> None:
        EmailValidator.validate(user_data.email)
        UsernameValidator.validate(user_data.username)
        PasswordValidator.validate(user_data.password)
        if not user_data.full_name or not user_data.full_name.strip():
            raise ValueError("Full name is required")
        
        if len(user_data.full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        
        if len(user_data.full_name) > 255:
            raise ValueError("Full name must be no more than 255 characters long")
    
    @staticmethod
    def validate_update_data(user_data) -> None:
        if user_data.email is not None:
            EmailValidator.validate(user_data.email)
        
        if user_data.username is not None:
            UsernameValidator.validate(user_data.username)
        
        if user_data.password is not None and user_data.password.strip():
            PasswordValidator.validate(user_data.password)
        
        if user_data.full_name is not None:
            if not user_data.full_name.strip():
                raise ValueError("Full name cannot be empty")
            
            if len(user_data.full_name.strip()) < 2:
                raise ValueError("Full name must be at least 2 characters long")
            
            if len(user_data.full_name) > 255:
                raise ValueError("Full name must be no more than 255 characters long")


class PaginationValidator:
    """Pagination parameters validation."""
    
    MAX_LIMIT = 1000
    MIN_LIMIT = 1
    
    @classmethod
    def validate(cls, skip: int, limit: int) -> None:
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit < cls.MIN_LIMIT:
            raise ValueError(f"Limit must be at least {cls.MIN_LIMIT}")
        
        if limit > cls.MAX_LIMIT:
            raise ValueError(f"Limit must be no more than {cls.MAX_LIMIT}")


class FilterValidator:
    """Filter parameters validation."""
    
    MAX_SEARCH_LENGTH = 100
    
    @classmethod
    def validate_filters(cls, filters) -> None:
        if filters.search is not None:
            if len(filters.search) > cls.MAX_SEARCH_LENGTH:
                raise ValueError(f"Search term must be no more than {cls.MAX_SEARCH_LENGTH} characters long")
            
            if len(filters.search.strip()) == 0:
                raise ValueError("Search term cannot be empty")
