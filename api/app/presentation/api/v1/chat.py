"""Chat endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.entities import ChatRequest, ChatResponse, VisualSimulationRequest, VisualSimulationResponse, ChatHistoryRequest, ChatHistoryResponse
from app.infrastructure.middleware import get_current_user, get_current_user_optional
from app.infrastructure.database import get_db
from app.infrastructure.models import ConversationModel, ChatMessageModel
from app.core.logging import get_logger
from app.core.container import container

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_or_create_conversation(
    db: Session, 
    user_id: Optional[int], 
    conversation_id: Optional[str],
    session_id: Optional[str] = None
) -> ConversationModel:
    """Get or create conversation for user or guest."""
    if conversation_id:
        # Try to find existing conversation
        conversation = db.query(ConversationModel).filter(
            ConversationModel.conversation_id == conversation_id
        ).first()
        if conversation:
            return conversation
    
    # Create new conversation
    import uuid
    new_conversation_id = conversation_id or str(uuid.uuid4())
    
    conversation = ConversationModel(
        user_id=user_id,
        conversation_id=new_conversation_id,
        title=f"Conversa {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        is_active=True
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    logger.info(f"Created new conversation - id: {new_conversation_id}, user_id: {user_id}")
    return conversation


def save_chat_message(
    db: Session,
    user_id: Optional[int],
    conversation_id: str,
    message: str,
    response: str,
    is_user: bool = True,
    has_image: bool = False,
    image_url: Optional[str] = None,
    intent: Optional[str] = None,
    confidence: Optional[float] = None,
    tools_used: Optional[List[str]] = None,
    processing_time_ms: Optional[float] = None
) -> ChatMessageModel:
    """Save chat message to database."""
    chat_message = ChatMessageModel(
        user_id=user_id,
        conversation_id=conversation_id,
        message=message if is_user else response,
        response=response if not is_user else None,
        is_user=is_user,
        has_image=has_image,
        image_url=image_url,
        intent=intent,
        confidence=str(confidence) if confidence else None,
        tools_used=tools_used,
        processing_time_ms=str(processing_time_ms) if processing_time_ms else None
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    logger.info(f"Saved chat message - conversation_id: {conversation_id}, is_user: {is_user}")
    return chat_message


@router.post("/message", response_model=ChatResponse, summary="Send Chat Message")
async def send_chat_message(
    request: ChatRequest,
    current_user = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Send chat message to AI Orchestrator.
    
    - Authenticated users: Can generate images and get full features
    - Guest users: Can chat but without image generation
    - Context is managed by AI Orchestrator
    - All messages are saved to database
    """
    try:
        # Se o usuário estiver autenticado, use seu ID
        is_authenticated = current_user is not None
        if is_authenticated:
            request.user_id = current_user.id
        
        # Validar se visitantes têm session_id
        if not is_authenticated and not request.session_id:
            raise HTTPException(
                status_code=400,
                detail="session_id é obrigatório para visitantes"
            )
        
        # Get or create conversation
        conversation = get_or_create_conversation(
            db=db,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            session_id=request.session_id
        )
        
        # Update request with actual conversation_id
        request.conversation_id = conversation.conversation_id
        
        logger.info(f"Chat request from user {request.user_id or 'guest'}")
        
        # Save user message to database
        save_chat_message(
            db=db,
            user_id=request.user_id,
            conversation_id=conversation.conversation_id,
            message=request.message,
            response="",  # User message, no response
            is_user=True
        )
        
        # Get AI service and send message
        ai_service = container.get_ai_orchestrator_service()
        
        try:
            response = await ai_service.send_chat_message(request, is_authenticated)
        except Exception as ai_error:
            logger.error(f"AI service error: {ai_error}")
            raise ai_error
        
        # Save AI response to database
        try:
            save_chat_message(
                db=db,
                user_id=request.user_id,
                conversation_id=conversation.conversation_id,
                message="",  # AI response, no user message
                response=response.response,
                is_user=False,
                has_image=response.has_image,
                image_url=response.image_url,
                intent=response.intent,
                confidence=response.confidence,
                tools_used=response.tools_used,
                processing_time_ms=response.processing_time_ms
            )
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            raise db_error
        
        logger.info(f"Chat processed for user {request.user_id or 'guest'}")
        
        # Add conversation_id to response
        response.conversation_id = conversation.conversation_id
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/conversations", response_model=List[dict], summary="Get User Conversations")
async def get_user_conversations(
    current_user = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get conversations for authenticated user or guest session."""
    try:
        if current_user:
            # Authenticated user - get their conversations
            conversations = db.query(ConversationModel).filter(
                ConversationModel.user_id == current_user.id,
                ConversationModel.is_active == True
            ).order_by(ConversationModel.created_at.desc()).offset(offset).limit(limit).all()
        else:
            # Guest user - return empty list (no persistent history)
            conversations = []
        
        result = []
        for conv in conversations:
            # Get message count
            message_count = db.query(ChatMessageModel).filter(
                ChatMessageModel.conversation_id == conv.conversation_id
            ).count()
            
            result.append({
                "conversation_id": conv.conversation_id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "message_count": message_count,
                "is_active": conv.is_active
            })
        
        logger.info(f"Retrieved {len(result)} conversations for user_id: {current_user.id if current_user else 'guest'}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[dict], summary="Get Conversation Messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get messages for a specific conversation."""
    try:
        # Verify conversation exists and user has access
        conversation = db.query(ConversationModel).filter(
            ConversationModel.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Check access permissions
        if current_user and conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        # Get messages
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.conversation_id == conversation_id
        ).order_by(ChatMessageModel.created_at.asc()).offset(offset).limit(limit).all()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "message": msg.message,
                "response": msg.response,
                "is_user": msg.is_user,
                "has_image": msg.has_image,
                "image_url": msg.image_url,
                "intent": msg.intent,
                "confidence": float(msg.confidence) if msg.confidence else None,
                "tools_used": msg.tools_used,
                "processing_time_ms": float(msg.processing_time_ms) if msg.processing_time_ms else None,
                "created_at": msg.created_at.isoformat()
            })
        
        logger.info(f"Retrieved {len(result)} messages for conversation: {conversation_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation messages"
        )


@router.delete("/conversations/{conversation_id}", summary="Delete Conversation")
async def delete_conversation(
    conversation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation (authenticated users only)."""
    try:
        # Find conversation
        conversation = db.query(ConversationModel).filter(
            ConversationModel.conversation_id == conversation_id,
            ConversationModel.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Soft delete - mark as inactive
        conversation.is_active = False
        db.commit()
        
        logger.info(f"Deleted conversation: {conversation_id} for user: {current_user.id}")
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.post("/message/guest", response_model=ChatResponse, summary="Send Chat Message (Guest)")
async def send_chat_message_guest(
    request: ChatRequest
):
    """
    Send chat message as guest (no authentication required).
    
    - No image generation
    - Limited features
    - No chat history
    """
    try:
        # Força user_id como None para visitantes
        request.user_id = None
        
        # Garante que não haverá geração de imagem
        if request.context is None:
            request.context = {}
        request.context["disable_visual_generation"] = True
        
        ai_service = container.get_ai_orchestrator_service()
        response = await ai_service.send_chat_message(request, is_authenticated=False)
        
        logger.info("Chat message processed for guest user")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Guest chat message validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error processing guest chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again."
        )


@router.post("/visual/generate", response_model=VisualSimulationResponse, summary="Generate Visual Simulation")
async def generate_visual_simulation(
    request: VisualSimulationRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate visual simulation (requires authentication).
    
    - Only available for authenticated users
    - Can take longer due to image generation
    """
    try:
        # Usa o ID do usuário autenticado
        request.user_id = current_user.id
        
        ai_service = container.get_ai_orchestrator_service()
        response = await ai_service.generate_visual_simulation(request)
        
        logger.info(
            f"Visual simulation generated - "
            f"user_id: {current_user.id}, "
            f"paint_id: {request.paint_id}"
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Visual simulation validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating visual simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate visual simulation. Please try again."
        )


@router.get("/history", response_model=ChatHistoryResponse, summary="Get Chat History")
async def get_chat_history(
    limit: int = 10,
    conversation_id: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get chat history for authenticated user.
    
    - Returns recent chat messages
    - Can filter by conversation_id
    - Limited to authenticated users
    """
    try:
        history_request = ChatHistoryRequest(
            user_id=current_user.id,
            limit=limit,
            conversation_id=conversation_id
        )
        
        ai_service = container.get_ai_orchestrator_service()
        response = await ai_service.get_chat_history(history_request)
        
        logger.info(
            f"Chat history retrieved - "
            f"user_id: {current_user.id}, "
            f"count: {response.total}"
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Chat history validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history. Please try again."
        )




@router.get("/health", summary="Check AI Orchestrator Health")
async def check_ai_health():
    """Check if AI Orchestrator is healthy and available."""
    try:
        ai_service = container.get_ai_orchestrator_service()
        is_healthy = await ai_service.health_check()
        
        if is_healthy:
            return {"status": "healthy", "message": "AI Orchestrator is available"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Orchestrator is not available"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking AI health: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to check AI service health"
        )


@router.get("/health/full", summary="Full Health Check with Context Stats")
async def full_health_check():
    """Comprehensive health check including context statistics."""
    try:
        # Verificar AI Orchestrator
        ai_service = container.get_ai_orchestrator_service()
        ai_healthy = await ai_service.health_check()
        
        # Context management is now handled by AI Orchestrator
        context_stats = {"managed_by": "ai_orchestrator"}
        
        return {
            "status": "healthy" if ai_healthy else "degraded",
            "ai_orchestrator": {
                "status": "healthy" if ai_healthy else "unhealthy",
                "available": ai_healthy
            },
            "context_management": {
                "status": "healthy",
                "managed_by": "ai_orchestrator",
                "note": "Context management delegated to AI Orchestrator"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in full health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

