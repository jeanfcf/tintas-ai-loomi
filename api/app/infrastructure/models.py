"""
SQLAlchemy models for RBAC system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base
from app.domain.entities import UserRole, UserStatus


class BaseModel(Base):
    """Base model with common fields for all entities."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class UserModel(BaseModel):
    """User SQLAlchemy model."""
    __tablename__ = "users"

    email = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Only enforce uniqueness for non-deleted records
    __table_args__ = (
        Index('ix_users_email_active', 'email', unique=True, 
              postgresql_where='deleted_at IS NULL'),
        Index('ix_users_username_active', 'username', unique=True, 
              postgresql_where='deleted_at IS NULL'),
    )

    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"
