"""Repository implementations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.entities import (
    User, UserCreate, UserUpdate, UserFilters, PaginationParams,
    Paint, PaintCreate, PaintUpdate, PaintFilters,
    Conversation, ConversationCreate, ConversationUpdate, ConversationFilters,
    ChatMessage, ChatMessageCreate, ChatMessageUpdate
)
from app.domain.repositories import UserRepositoryInterface, PaintRepositoryInterface, ConversationRepositoryInterface, ChatMessageRepositoryInterface
from app.infrastructure.models import UserModel, PaintModel, ConversationModel, ChatMessageModel
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


class PaintRepository(PaintRepositoryInterface):
    """Paint repository implementation."""

    def create(self, db: Session, paint_data: PaintCreate) -> Paint:
        """Create a new paint."""
        try:
            db_paint = PaintModel(
                name=paint_data.name,
                color=paint_data.color,
                surface_types=paint_data.surface_types,
                environment=paint_data.environment,
                finish_type=paint_data.finish_type,
                features=paint_data.features,
                line=paint_data.line,
                description=paint_data.description
            )
            
            db.add(db_paint)
            db.commit()
            db.refresh(db_paint)
            
            return self._model_to_entity(db_paint)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error creating paint: {e}"
            logger.error(f"{error_msg} - name: {paint_data.name}, color: {paint_data.color}")
            raise Exception(error_msg)

    def _get_active_paint_query(self, db: Session):
        """Get base query for active paints."""
        return db.query(PaintModel).filter(PaintModel.deleted_at.is_(None))

    def get_by_id(self, db: Session, paint_id: int) -> Optional[Paint]:
        """Get paint by ID."""
        db_paint = self._get_active_paint_query(db).filter(PaintModel.id == paint_id).first()
        return self._model_to_entity(db_paint) if db_paint else None

    def get_by_name(self, db: Session, name: str) -> Optional[Paint]:
        """Get paint by name."""
        db_paint = self._get_active_paint_query(db).filter(PaintModel.name == name).first()
        return self._model_to_entity(db_paint) if db_paint else None

    def get_all(self, db: Session, pagination: PaginationParams, filters: PaintFilters) -> List[Paint]:
        """Get all paints with pagination and filters."""
        query = self._get_active_paint_query(db)
        query = self._apply_filters(query, filters)
        
        db_paints = query.offset(pagination.skip).limit(pagination.limit).all()
        return [self._model_to_entity(db_paint) for db_paint in db_paints]

    def count_all(self, db: Session, filters: PaintFilters) -> int:
        """Count all paints matching filters."""
        query = self._get_active_paint_query(db)
        query = self._apply_filters(query, filters)
        return query.count()

    def _apply_filters(self, query, filters: PaintFilters):
        """Apply filters to query with error handling."""
        try:
            if not filters.is_empty():
                if filters.search:
                    search_term = f"%{filters.search.lower()}%"
                    query = query.filter(
                        or_(
                            PaintModel.name.ilike(search_term),
                            PaintModel.color.ilike(search_term),
                            PaintModel.description.ilike(search_term)
                        )
                    )
                
                if filters.color:
                    query = query.filter(PaintModel.color.ilike(f"%{filters.color}%"))
                
                if filters.surface_types and len(filters.surface_types) > 0:
                    try:
                        if hasattr(PaintModel, 'surface_types'):
                            query = query.filter(PaintModel.surface_types.op('&&')(filters.surface_types))

                    except Exception as e:
                        logger.warning(f"Error applying surface_types filter: {e}")
                
                if filters.environment:
                    query = query.filter(PaintModel.environment == filters.environment)
                
                if filters.finish_type:
                    query = query.filter(PaintModel.finish_type == filters.finish_type)
                
                if filters.line:
                    query = query.filter(PaintModel.line == filters.line)
                
                if filters.features and len(filters.features) > 0:
                    # Filter by features using array overlap with validation
                    try:
                        query = query.filter(PaintModel.features.overlap(filters.features))
                    except Exception as e:
                        logger.warning(f"Error applying features filter: {e}")
                        # Fallback: don't apply features filter if it fails
                        pass
            
            return query
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            # Return query without filters if there's an error
            return query

    def update(self, db: Session, paint_id: int, paint_data: PaintUpdate) -> Optional[Paint]:
        """Update paint."""
        db_paint = self._get_active_paint_query(db).filter(PaintModel.id == paint_id).first()
        if not db_paint:
            return None

        update_data = paint_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_paint, field, value)

        db.commit()
        db.refresh(db_paint)
        return self._model_to_entity(db_paint)

    def delete(self, db: Session, paint_id: int) -> bool:
        """Soft delete paint."""
        db_paint = self._get_active_paint_query(db).filter(PaintModel.id == paint_id).first()
        if not db_paint:
            return False

        from datetime import datetime
        db_paint.deleted_at = datetime.utcnow()
        db.commit()
        return True

    def exists_by_name(self, db: Session, name: str) -> bool:
        """Check if paint exists by name."""
        db_paint = db.query(PaintModel).filter(PaintModel.name == name).first()
        return db_paint is not None

    def exists_active_by_name(self, db: Session, name: str) -> bool:
        """Check if active paint exists by name."""
        db_paint = self._get_active_paint_query(db).filter(PaintModel.name == name).first()
        return db_paint is not None

    def get_by_filters(self, db: Session, filters: PaintFilters) -> List[Paint]:
        """Get paints by specific filters without pagination."""
        query = self._get_active_paint_query(db)
        query = self._apply_filters(query, filters)
        
        db_paints = query.all()
        return [self._model_to_entity(db_paint) for db_paint in db_paints]

    def _model_to_entity(self, db_paint: PaintModel) -> Paint:
        """Convert model to entity."""
        return Paint(
            id=db_paint.id,
            name=db_paint.name,
            color=db_paint.color,
            surface_types=db_paint.surface_types or [],
            environment=db_paint.environment,
            finish_type=db_paint.finish_type,
            features=db_paint.features,
            line=db_paint.line,
            description=db_paint.description,
            created_at=db_paint.created_at,
            updated_at=db_paint.updated_at,
            deleted_at=db_paint.deleted_at
        )


class ConversationRepository(ConversationRepositoryInterface):
    """Conversation repository implementation."""

    def create(self, db: Session, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        try:
            db_conversation = ConversationModel(
                user_id=conversation_data.user_id,
                conversation_id=conversation_data.conversation_id,
                title=conversation_data.title
            )
            
            db.add(db_conversation)
            db.commit()
            db.refresh(db_conversation)
            
            return self._model_to_entity(db_conversation)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error creating conversation: {e}"
            logger.error(f"{error_msg} - conversation_id: {conversation_data.conversation_id}")
            raise Exception(error_msg)

    def _get_active_conversation_query(self, db: Session):
        """Get base query for active conversations."""
        return db.query(ConversationModel).filter(ConversationModel.deleted_at.is_(None))

    def get_by_id(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        db_conversation = self._get_active_conversation_query(db).filter(ConversationModel.id == conversation_id).first()
        return self._model_to_entity(db_conversation) if db_conversation else None

    def get_by_conversation_id(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by conversation_id string."""
        db_conversation = self._get_active_conversation_query(db).filter(ConversationModel.conversation_id == conversation_id).first()
        return self._model_to_entity(db_conversation) if db_conversation else None

    def get_by_user(self, db: Session, user_id: int, pagination: PaginationParams, filters: ConversationFilters) -> List[Conversation]:
        """Get conversations by user with pagination and filters."""
        query = self._get_active_conversation_query(db).filter(ConversationModel.user_id == user_id)
        
        # Apply filters
        if filters.is_active is not None:
            query = query.filter(ConversationModel.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    ConversationModel.title.ilike(search_term),
                    ConversationModel.conversation_id.ilike(search_term)
                )
            )
        
        # Apply pagination
        query = query.order_by(ConversationModel.updated_at.desc())
        query = query.offset(pagination.skip).limit(pagination.limit)
        
        db_conversations = query.all()
        return [self._model_to_entity(conv) for conv in db_conversations]

    def count_by_user(self, db: Session, user_id: int, filters: ConversationFilters) -> int:
        """Count conversations by user matching filters."""
        query = self._get_active_conversation_query(db).filter(ConversationModel.user_id == user_id)
        
        # Apply filters
        if filters.is_active is not None:
            query = query.filter(ConversationModel.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    ConversationModel.title.ilike(search_term),
                    ConversationModel.conversation_id.ilike(search_term)
                )
            )
        
        return query.count()

    def update(self, db: Session, conversation_id: int, conversation_data: ConversationUpdate) -> Optional[Conversation]:
        """Update conversation."""
        try:
            db_conversation = self._get_active_conversation_query(db).filter(ConversationModel.id == conversation_id).first()
            
            if not db_conversation:
                return None
            
            # Update fields
            if conversation_data.title is not None:
                db_conversation.title = conversation_data.title
            if conversation_data.is_active is not None:
                db_conversation.is_active = conversation_data.is_active
            
            db.commit()
            db.refresh(db_conversation)
            
            return self._model_to_entity(db_conversation)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error updating conversation: {e}"
            logger.error(f"{error_msg} - conversation_id: {conversation_id}")
            raise Exception(error_msg)

    def delete(self, db: Session, conversation_id: int) -> bool:
        """Soft delete conversation."""
        try:
            from sqlalchemy import func
            
            db_conversation = self._get_active_conversation_query(db).filter(ConversationModel.id == conversation_id).first()
            
            if not db_conversation:
                return False
            
            db_conversation.deleted_at = func.now()
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error deleting conversation: {e}"
            logger.error(f"{error_msg} - conversation_id: {conversation_id}")
            raise Exception(error_msg)

    def exists_by_conversation_id(self, db: Session, conversation_id: str) -> bool:
        """Check if conversation exists by conversation_id."""
        return self._get_active_conversation_query(db).filter(ConversationModel.conversation_id == conversation_id).first() is not None

    def _model_to_entity(self, db_conversation: ConversationModel) -> Conversation:
        """Convert database model to domain entity."""
        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            conversation_id=db_conversation.conversation_id,
            title=db_conversation.title,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            is_active=db_conversation.is_active
        )


class ChatMessageRepository(ChatMessageRepositoryInterface):
    """Chat message repository implementation."""

    def create(self, db: Session, message_data: ChatMessageCreate) -> ChatMessage:
        """Create a new chat message."""
        try:
            db_message = ChatMessageModel(
                user_id=message_data.user_id,
                conversation_id=message_data.conversation_id,
                message=message_data.message,
                response=message_data.response,
                is_user=message_data.is_user,
                has_image=message_data.has_image,
                image_url=message_data.image_url,
                intent=message_data.intent,
                confidence=str(message_data.confidence) if message_data.confidence is not None else None,
                tools_used=message_data.tools_used,
                processing_time_ms=str(message_data.processing_time_ms) if message_data.processing_time_ms is not None else None
            )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            return self._model_to_entity(db_message)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error creating chat message: {e}"
            logger.error(f"{error_msg} - conversation_id: {message_data.conversation_id}")
            raise Exception(error_msg)

    def _get_active_message_query(self, db: Session):
        """Get base query for active messages."""
        return db.query(ChatMessageModel).filter(ChatMessageModel.deleted_at.is_(None))

    def get_by_id(self, db: Session, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        db_message = self._get_active_message_query(db).filter(ChatMessageModel.id == message_id).first()
        return self._model_to_entity(db_message) if db_message else None

    def get_by_conversation(self, db: Session, conversation_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages by conversation with pagination."""
        query = self._get_active_message_query(db).filter(ChatMessageModel.conversation_id == conversation_id)
        query = query.order_by(ChatMessageModel.created_at.asc())
        query = query.offset(offset).limit(limit)
        
        db_messages = query.all()
        return [self._model_to_entity(msg) for msg in db_messages]

    def count_by_conversation(self, db: Session, conversation_id: str) -> int:
        """Count messages in conversation."""
        return self._get_active_message_query(db).filter(ChatMessageModel.conversation_id == conversation_id).count()

    def update(self, db: Session, message_id: int, message_data: ChatMessageUpdate) -> Optional[ChatMessage]:
        """Update chat message."""
        try:
            db_message = self._get_active_message_query(db).filter(ChatMessageModel.id == message_id).first()
            
            if not db_message:
                return None
            
            # Update fields
            if message_data.response is not None:
                db_message.response = message_data.response
            if message_data.has_image is not None:
                db_message.has_image = message_data.has_image
            if message_data.image_url is not None:
                db_message.image_url = message_data.image_url
            if message_data.intent is not None:
                db_message.intent = message_data.intent
            if message_data.confidence is not None:
                db_message.confidence = str(message_data.confidence)
            if message_data.tools_used is not None:
                db_message.tools_used = message_data.tools_used
            if message_data.processing_time_ms is not None:
                db_message.processing_time_ms = str(message_data.processing_time_ms)
            
            db.commit()
            db.refresh(db_message)
            
            return self._model_to_entity(db_message)
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error updating chat message: {e}"
            logger.error(f"{error_msg} - message_id: {message_id}")
            raise Exception(error_msg)

    def delete(self, db: Session, message_id: int) -> bool:
        """Soft delete chat message."""
        try:
            from sqlalchemy import func
            
            db_message = self._get_active_message_query(db).filter(ChatMessageModel.id == message_id).first()
            
            if not db_message:
                return False
            
            db_message.deleted_at = func.now()
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error deleting chat message: {e}"
            logger.error(f"{error_msg} - message_id: {message_id}")
            raise Exception(error_msg)

    def get_latest_by_conversation(self, db: Session, conversation_id: str, limit: int = 1) -> List[ChatMessage]:
        """Get latest messages by conversation."""
        query = self._get_active_message_query(db).filter(ChatMessageModel.conversation_id == conversation_id)
        query = query.order_by(ChatMessageModel.created_at.desc())
        query = query.limit(limit)
        
        db_messages = query.all()
        return [self._model_to_entity(msg) for msg in db_messages]

    def _model_to_entity(self, db_message: ChatMessageModel) -> ChatMessage:
        """Convert database model to domain entity."""
        return ChatMessage(
            id=db_message.id,
            user_id=db_message.user_id,
            message=db_message.message,
            response=db_message.response,
            is_user=db_message.is_user,
            has_image=db_message.has_image,
            image_url=db_message.image_url,
            intent=db_message.intent,
            confidence=float(db_message.confidence) if db_message.confidence else None,
            tools_used=db_message.tools_used or [],
            processing_time_ms=float(db_message.processing_time_ms) if db_message.processing_time_ms else None,
            conversation_id=db_message.conversation_id,
            created_at=db_message.created_at
        )


