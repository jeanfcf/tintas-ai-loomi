"""Repository interfaces."""
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities import (
    User, UserCreate, UserUpdate, UserFilters, PaginationParams,
    Paint, PaintCreate, PaintUpdate, PaintFilters,
    Conversation, ConversationCreate, ConversationUpdate, ConversationFilters,
    ChatMessage, ChatMessageCreate, ChatMessageUpdate
)


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


class PaintRepositoryInterface(ABC):
    """Paint repository interface."""

    @abstractmethod
    def create(self, db: Session, paint_data: PaintCreate) -> Paint:
        """Create a new paint."""
        pass

    @abstractmethod
    def get_by_id(self, db: Session, paint_id: int) -> Optional[Paint]:
        """Get paint by ID."""
        pass

    @abstractmethod
    def get_by_name(self, db: Session, name: str) -> Optional[Paint]:
        """Get paint by name."""
        pass

    @abstractmethod
    def get_all(self, db: Session, pagination: PaginationParams, filters: PaintFilters) -> List[Paint]:
        """Get all paints with pagination and filters."""
        pass

    @abstractmethod
    def count_all(self, db: Session, filters: PaintFilters) -> int:
        """Count all paints matching filters."""
        pass

    @abstractmethod
    def update(self, db: Session, paint_id: int, paint_data: PaintUpdate) -> Optional[Paint]:
        """Update paint."""
        pass

    @abstractmethod
    def delete(self, db: Session, paint_id: int) -> bool:
        """Soft delete paint."""
        pass

    @abstractmethod
    def exists_by_name(self, db: Session, name: str) -> bool:
        """Check if paint exists by name."""
        pass

    @abstractmethod
    def exists_active_by_name(self, db: Session, name: str) -> bool:
        """Check if active paint exists by name."""
        pass

    @abstractmethod
    def get_by_filters(self, db: Session, filters: PaintFilters) -> List[Paint]:
        """Get paints by specific filters without pagination."""
        pass


class ConversationRepositoryInterface(ABC):
    """Conversation repository interface."""

    @abstractmethod
    def create(self, db: Session, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        pass

    @abstractmethod
    def get_by_id(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        pass

    @abstractmethod
    def get_by_conversation_id(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by conversation_id string."""
        pass

    @abstractmethod
    def get_by_user(self, db: Session, user_id: int, pagination: PaginationParams, filters: ConversationFilters) -> List[Conversation]:
        """Get conversations by user with pagination and filters."""
        pass

    @abstractmethod
    def count_by_user(self, db: Session, user_id: int, filters: ConversationFilters) -> int:
        """Count conversations by user matching filters."""
        pass

    @abstractmethod
    def update(self, db: Session, conversation_id: int, conversation_data: ConversationUpdate) -> Optional[Conversation]:
        """Update conversation."""
        pass

    @abstractmethod
    def delete(self, db: Session, conversation_id: int) -> bool:
        """Soft delete conversation."""
        pass

    @abstractmethod
    def exists_by_conversation_id(self, db: Session, conversation_id: str) -> bool:
        """Check if conversation exists by conversation_id."""
        pass


class ChatMessageRepositoryInterface(ABC):
    """Chat message repository interface."""

    @abstractmethod
    def create(self, db: Session, message_data: ChatMessageCreate) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_by_id(self, db: Session, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        pass

    @abstractmethod
    def get_by_conversation(self, db: Session, conversation_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages by conversation with pagination."""
        pass

    @abstractmethod
    def count_by_conversation(self, db: Session, conversation_id: str) -> int:
        """Count messages in conversation."""
        pass

    @abstractmethod
    def update(self, db: Session, message_id: int, message_data: ChatMessageUpdate) -> Optional[ChatMessage]:
        """Update chat message."""
        pass

    @abstractmethod
    def delete(self, db: Session, message_id: int) -> bool:
        """Soft delete chat message."""
        pass

    @abstractmethod
    def get_latest_by_conversation(self, db: Session, conversation_id: str, limit: int = 1) -> List[ChatMessage]:
        """Get latest messages by conversation."""
        pass
