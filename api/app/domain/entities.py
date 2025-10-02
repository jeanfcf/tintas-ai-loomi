"""Domain entities."""
from enum import Enum
from typing import List, Optional, Dict, Any
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


# Paint-related enums and entities
class SurfaceType(str, Enum):
    """Surface types for paint application."""
    ALVENARIA = "alvenaria"
    MADEIRA = "madeira"
    FERRO = "ferro"
    CONCRETE = "concrete"
    METAL = "metal"
    PLASTIC = "plastic"


class Environment(str, Enum):
    """Environment types."""
    INTERNO = "interno"
    EXTERNO = "externo"
    INTERNO_EXTERNO = "interno/externo"


class FinishType(str, Enum):
    """Finish types."""
    FOSCO = "fosco"
    ACETINADO = "acetinado"
    BRILHANTE = "brilhante"
    SEMI_BRILHANTE = "semi-brilhante"


class PaintLine(str, Enum):
    """Paint lines."""
    PREMIUM = "premium"
    STANDARD = "standard"
    ECONOMIC = "economic"


class Paint(BaseModel):
    """Paint entity."""
    id: Optional[int] = None
    name: str
    color: str
    surface_types: List[SurfaceType] = []
    environment: Environment
    finish_type: FinishType
    features: List[str] = []
    line: PaintLine
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaintCreate(BaseModel):
    """Paint creation model."""
    name: str
    color: str
    surface_types: List[SurfaceType] = []
    environment: Environment
    finish_type: FinishType
    features: List[str] = []
    line: PaintLine
    description: Optional[str] = None

    def model_post_init(self, __context):
        from app.domain.validators import PaintValidator
        PaintValidator.validate_paint_data(self)


class PaintUpdate(BaseModel):
    """Paint update model."""
    name: Optional[str] = None
    color: Optional[str] = None
    surface_types: Optional[List[SurfaceType]] = None
    environment: Optional[Environment] = None
    finish_type: Optional[FinishType] = None
    features: Optional[List[str]] = None
    line: Optional[PaintLine] = None
    description: Optional[str] = None

    def model_post_init(self, __context):
        from app.domain.validators import PaintValidator
        PaintValidator.validate_paint_update(self)


class PaintResponse(BaseModel):
    """Paint response model."""
    id: int
    name: str
    color: str
    surface_types: List[SurfaceType]
    environment: Environment
    finish_type: FinishType
    features: List[str]
    line: PaintLine
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaintFilters(BaseModel):
    """Paint filters model."""
    search: Optional[str] = None
    color: Optional[str] = None
    surface_types: Optional[List[SurfaceType]] = None
    environment: Optional[Environment] = None
    finish_type: Optional[FinishType] = None
    line: Optional[PaintLine] = None
    features: Optional[List[str]] = None
    
    def model_post_init(self, __context):
        from app.domain.validators import FilterValidator
        FilterValidator.validate_filters(self)
    
    def is_empty(self) -> bool:
        return not any([
            self.search, self.color, self.surface_types, 
            self.environment, self.finish_type, self.line, self.features
        ])


class PaginatedPaintResponse(BaseModel):
    """Paginated paint response model."""
    items: List[PaintResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool


# CSV Import related entities
class CSVImportResult(BaseModel):
    """CSV import result model."""
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: List[str] = []
    imported_paints: List[PaintResponse] = []


class CSVRowError(BaseModel):
    """CSV row error model."""
    row_number: int
    field: str
    value: str
    error_message: str


class CSVImportRequest(BaseModel):
    """CSV import request model."""
    file_content: str  # Base64 encoded CSV content
    file_name: str
    skip_duplicates: bool = True
    update_existing: bool = False


class CSVImportResponse(BaseModel):
    """CSV import response model."""
    success: bool
    message: str
    result: Optional[CSVImportResult] = None
    errors: List[CSVRowError] = []


# Chat and AI Orchestrator related entities
class ChatMessage(BaseModel):
    """Chat message entity."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    message: str
    response: Optional[str] = None
    is_user: bool = True
    has_image: bool = False
    image_url: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    tools_used: List[str] = []
    processing_time_ms: Optional[float] = None
    conversation_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: Optional[int] = None
    conversation_id: Optional[str] = None
    context_id: Optional[str] = None  # ID do contexto no AI Orchestrator
    session_id: Optional[str] = None  # ID da sessão (para visitantes)
    context: Optional[dict] = None    # Contexto adicional

    def model_post_init(self, __context):
        from app.domain.validators import ChatValidator
        ChatValidator.validate_message(self.message)


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    has_image: bool = False
    image_url: Optional[str] = None
    recommendations: List[str] = []
    reasoning_steps: List[Dict[str, Any]] = []
    confidence: Optional[float] = None
    processing_time_ms: Optional[float] = None
    intent: Optional[str] = None
    tools_used: Optional[List[str]] = []
    request_id: Optional[str] = None
    response_id: Optional[str] = None
    conversation_id: Optional[str] = None


class VisualSimulationRequest(BaseModel):
    """Visual simulation request model."""
    prompt: str
    user_id: int
    paint_id: Optional[int] = None
    room_type: Optional[str] = None
    style: Optional[str] = None

    def model_post_init(self, __context):
        from app.domain.validators import ChatValidator
        ChatValidator.validate_message(self.prompt)


class VisualSimulationResponse(BaseModel):
    """Visual simulation response model."""
    image_url: str
    prompt_used: str
    processing_time_ms: float
    request_id: str
    response_id: str


class ChatHistoryRequest(BaseModel):
    """Chat history request model."""
    user_id: int
    limit: int = 10
    conversation_id: Optional[str] = None

    def model_post_init(self, __context):
        from app.domain.validators import PaginationValidator
        PaginationValidator.validate(0, self.limit)


class ChatHistoryResponse(BaseModel):
    """Chat history response model."""
    messages: List[ChatMessage]
    total: int
    has_more: bool


# Database entities for chat persistence
class Conversation(BaseModel):
    """Conversation entity for database."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    conversation_id: str
    title: Optional[str] = None
    consent_given: bool = False
    retention_days: Optional[int] = 90
    expires_at: Optional[datetime] = None  # Data de expiração automática
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Conversation creation model."""
    user_id: Optional[int] = None
    conversation_id: str
    title: Optional[str] = None
    consent_given: bool = False  # Consentimento para armazenamento
    retention_days: Optional[int] = 90  # Dias de retenção (padrão 90)


class ConversationUpdate(BaseModel):
    """Conversation update model."""
    title: Optional[str] = None
    is_active: Optional[bool] = None


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: int
    user_id: Optional[int] = None
    conversation_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Chat message creation model."""
    user_id: Optional[int] = None
    conversation_id: str
    message: str
    response: Optional[str] = None
    is_user: bool = True
    has_image: bool = False
    image_url: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    tools_used: List[str] = []
    processing_time_ms: Optional[float] = None

    def model_post_init(self, __context):
        from app.domain.validators import ChatValidator
        ChatValidator.validate_message(self.message)


class ChatMessageUpdate(BaseModel):
    """Chat message update model."""
    response: Optional[str] = None
    has_image: Optional[bool] = None
    image_url: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    tools_used: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None


class ConversationFilters(BaseModel):
    """Conversation filters model."""
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    
    def is_empty(self) -> bool:
        return not any([self.user_id, self.is_active, self.search])


class PaginatedConversationResponse(BaseModel):
    """Paginated conversation response model."""
    items: List[ConversationResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
