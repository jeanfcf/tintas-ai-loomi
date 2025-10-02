"""Domain services."""
from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain.entities import (
    User, UserCreate, UserUpdate, LoginRequest, Token, TokenData, UserFilters, PaginationParams, PaginatedResponse,
    Paint, PaintCreate, PaintUpdate, PaintFilters, PaginatedPaintResponse,
    CSVImportRequest, CSVImportResponse, CSVImportResult,
    ChatRequest, ChatResponse, VisualSimulationRequest, VisualSimulationResponse, ChatHistoryRequest, ChatHistoryResponse,
    Conversation, ConversationCreate, ConversationUpdate, ConversationFilters, PaginatedConversationResponse,
    ChatMessage, ChatMessageCreate, ChatMessageUpdate
)


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


class PaintServiceInterface(ABC):
    """Paint service interface."""

    @abstractmethod
    def create_paint(self, db: Session, paint_data: PaintCreate) -> Paint:
        """Create a new paint."""
        pass

    @abstractmethod
    def get_paint(self, db: Session, paint_id: int) -> Optional[Paint]:
        """Get paint by ID."""
        pass

    @abstractmethod
    def get_paint_by_name(self, db: Session, name: str) -> Optional[Paint]:
        """Get paint by name."""
        pass

    @abstractmethod
    def get_paints(self, db: Session, pagination: PaginationParams, filters: PaintFilters) -> PaginatedPaintResponse:
        """Get all paints with pagination and filters."""
        pass

    @abstractmethod
    def update_paint(self, db: Session, paint_id: int, paint_data: PaintUpdate) -> Optional[Paint]:
        """Update paint."""
        pass

    @abstractmethod
    def delete_paint(self, db: Session, paint_id: int) -> bool:
        """Soft delete paint."""
        pass

    @abstractmethod
    def get_paints_by_filters(self, db: Session, filters: PaintFilters) -> List[Paint]:
        """Get paints by specific filters without pagination."""
        pass


class CSVImportServiceInterface(ABC):
    """CSV import service interface."""

    @abstractmethod
    async def import_paints_from_csv(self, db: Session, import_request: CSVImportRequest) -> CSVImportResponse:
        """Import paints from CSV file."""
        pass

    @abstractmethod
    def validate_csv_file(self, csv_content: str) -> bool:
        """Validate CSV file structure and format."""
        pass

    @abstractmethod
    def parse_csv_content(self, csv_content: str) -> List[dict]:
        """Parse CSV content into list of dictionaries."""
        pass


class AIOrchestratorServiceInterface(ABC):
    """AI Orchestrator service interface for external communication."""

    @abstractmethod
    async def send_chat_message(self, chat_request, is_authenticated: bool):
        """Send chat message to AI Orchestrator."""
        pass

    @abstractmethod
    async def generate_visual_simulation(self, visual_request):
        """Generate visual simulation via AI Orchestrator."""
        pass

    @abstractmethod
    async def get_chat_history(self, history_request):
        """Get chat history from AI Orchestrator."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if AI Orchestrator is healthy."""
        pass


class ConversationServiceInterface(ABC):
    """Conversation service interface."""

    @abstractmethod
    def create_conversation(self, db: Session, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        pass

    @abstractmethod
    def get_conversation(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        pass

    @abstractmethod
    def get_conversation_by_id(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by conversation_id string."""
        pass

    @abstractmethod
    def get_user_conversations(self, db: Session, user_id: int, pagination: PaginationParams, filters: ConversationFilters) -> PaginatedConversationResponse:
        """Get conversations by user with pagination and filters."""
        pass

    @abstractmethod
    def update_conversation(self, db: Session, conversation_id: int, conversation_data: ConversationUpdate) -> Optional[Conversation]:
        """Update conversation."""
        pass

    @abstractmethod
    def delete_conversation(self, db: Session, conversation_id: int) -> bool:
        """Soft delete conversation."""
        pass


class ChatMessageServiceInterface(ABC):
    """Chat message service interface."""

    @abstractmethod
    def create_message(self, db: Session, message_data: ChatMessageCreate) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_message(self, db: Session, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        pass

    @abstractmethod
    def get_conversation_messages(self, db: Session, conversation_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages by conversation with pagination."""
        pass

    @abstractmethod
    def update_message(self, db: Session, message_id: int, message_data: ChatMessageUpdate) -> Optional[ChatMessage]:
        """Update chat message."""
        pass

    @abstractmethod
    def delete_message(self, db: Session, message_id: int) -> bool:
        """Soft delete chat message."""
        pass

    @abstractmethod
    def get_conversation_message_count(self, db: Session, conversation_id: str) -> int:
        """Get message count for conversation."""
        pass
