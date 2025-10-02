"""
SQLAlchemy models for RBAC system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Index, Text, ARRAY, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.infrastructure.database import Base
from app.domain.entities import UserRole, UserStatus, SurfaceType, Environment, FinishType, PaintLine

# Define ENUMs explicitly for better Alembic detection
user_role_enum = ENUM(UserRole, name='userrole', create_type=False)
user_status_enum = ENUM(UserStatus, name='userstatus', create_type=False)
surface_type_enum = ENUM(SurfaceType, name='surfacetype', create_type=False)
environment_enum = ENUM(Environment, name='environment', create_type=False)
finish_type_enum = ENUM(FinishType, name='finishtype', create_type=False)
paint_line_enum = ENUM(PaintLine, name='paintline', create_type=False)


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
    role = Column(user_role_enum, default=UserRole.USER, nullable=False)
    status = Column(user_status_enum, default=UserStatus.ACTIVE, nullable=False)
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


class PaintModel(BaseModel):
    """Paint SQLAlchemy model."""
    __tablename__ = "paints"

    name = Column(String(255), nullable=False, index=True)
    color = Column(String(100), nullable=False, index=True)
    surface_types = Column(ARRAY(surface_type_enum), default=[], nullable=False)
    environment = Column(environment_enum, nullable=False, index=True)
    finish_type = Column(finish_type_enum, nullable=False, index=True)
    features = Column(ARRAY(String), default=[], nullable=False)
    line = Column(paint_line_enum, nullable=False, index=True)
    description = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # Vector embedding for RAG

    # Indexes for better query performance
    __table_args__ = (
        Index('ix_paints_name_active', 'name', unique=True, 
              postgresql_where='deleted_at IS NULL'),
        Index('ix_paints_color_surface', 'color', 'surface_types'),
        Index('ix_paints_environment_line', 'environment', 'line'),
        Index('ix_paints_features_gin', 'features', postgresql_using='gin'),
        Index('ix_paints_surface_types_gin', 'surface_types', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<PaintModel(id={self.id}, name='{self.name}', color='{self.color}')>"


class ConversationModel(BaseModel):
    """Conversation SQLAlchemy model."""
    __tablename__ = "conversations"

    user_id = Column(Integer, nullable=True)  # Nullable for guest conversations
    conversation_id = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index('ix_conversations_user_id', 'user_id'),
        Index('ix_conversations_conversation_id', 'conversation_id'),
        Index('ix_conversations_user_active', 'user_id', 'is_active'),
        Index('ix_conversations_active', 'is_active'),
    )

    def __repr__(self):
        return f"<ConversationModel(id={self.id}, conversation_id='{self.conversation_id}', user_id={self.user_id})>"


class ChatMessageModel(BaseModel):
    """Chat message SQLAlchemy model."""
    __tablename__ = "chat_messages"

    user_id = Column(Integer, nullable=True)  # Nullable for guest messages
    conversation_id = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    is_user = Column(Boolean, default=True, nullable=False)
    has_image = Column(Boolean, default=False, nullable=False)
    image_url = Column(Text, nullable=True)
    intent = Column(String(100), nullable=True)
    confidence = Column(String(20), nullable=True)  # Store as string to avoid precision issues
    tools_used = Column(ARRAY(String), nullable=True)
    processing_time_ms = Column(String(20), nullable=True)  # Store as string to avoid precision issues

    # Indexes for performance
    __table_args__ = (
        Index('ix_chat_messages_conversation_id', 'conversation_id'),
        Index('ix_chat_messages_user_id', 'user_id'),
        Index('ix_chat_messages_conversation_created', 'conversation_id', 'created_at'),
        Index('ix_chat_messages_is_user', 'is_user'),
    )

    def __repr__(self):
        return f"<ChatMessageModel(id={self.id}, conversation_id='{self.conversation_id}', is_user={self.is_user})>"
