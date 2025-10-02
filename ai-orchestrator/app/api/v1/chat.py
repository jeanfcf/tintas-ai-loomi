"""Chat endpoints for AI Orchestrator."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.core.logging import AILogger
from app.core.security import PromptSecurity
from app.services.agent_service import AgentService

router = APIRouter()
logger = AILogger(__name__)
security = PromptSecurity()


async def get_agent_service() -> AgentService:
    """Dependency to get agent service."""
    return AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Chat with AI agent for paint recommendations."""
    start_time = time.time()
    
    try:
        # Validate prompt security
        validation_result = await security.validate_prompt(
            request.message, 
            request.context or {}
        )
        
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt: {validation_result.reason}"
            )
        
        # Use sanitized input
        sanitized_message = validation_result.sanitized_input
        
        # Validar se os IDs necessários foram fornecidos
        # Para usuários logados: conversation_id é obrigatório
        # Para visitantes: session_id é obrigatório
        if request.conversation_id and request.session_id:
            raise HTTPException(
                status_code=400,
                detail="Não é possível fornecer conversation_id e session_id simultaneamente"
            )
        if not request.conversation_id and not request.session_id:
            raise HTTPException(
                status_code=400,
                detail="conversation_id ou session_id deve ser fornecido"
            )
        
        # Log request with detailed debugging
        logger.logger.info(f"Raw request data: {request.dict()}")
        logger.logger.info(
            f"Request received -  conversation_id: {request.conversation_id}, session_id: {request.session_id}, message: '{sanitized_message[:50]}...'"
        )
        
        # Process with agent
        logger.logger.info("Processing with agent service")
        response = await agent_service.process_query(
            message=sanitized_message,
            context=request.context or {},
            conversation_id=request.conversation_id,
            session_id=request.session_id
        )
        logger.logger.info(f"Agent processing completed - has_image: {response.visual_url is not None}")
        
        processing_time = time.time() - start_time
        
        # Log the interaction
        logger.log_agent_decision(
            user_message=request.message,
            intent=response.intent,
            tools_used=response.tools_used,
            response=response.response,
            processing_time=processing_time,
            request_id=request.request_id
        )
        
        # Log response
        logger.logger.info(
            f"Response sent - {len(response.response)} chars, confidence: {response.confidence:.2f}, "
            f"processing_time: {processing_time * 1000:.0f}ms"
        )
        
        return ChatResponse(
            response=response.response,
            recommendations=response.recommendations,
            visual_url=response.visual_url,
            reasoning_steps=response.reasoning_steps,
            confidence=response.confidence,
            processing_time_ms=processing_time * 1000,
            request_id=request.request_id or f"req_{int(time.time())}",
            response_id=response.response_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        
        logger.log_error(
            error=e,
            context={
                "user_message": request.message,
                "processing_time": processing_time
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


