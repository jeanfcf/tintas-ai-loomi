"""AI Orchestrator service implementation."""
import httpx
import time
import uuid
from typing import Optional
from app.domain.services import AIOrchestratorServiceInterface
from app.domain.entities import ChatRequest, ChatResponse, VisualSimulationRequest, VisualSimulationResponse, ChatHistoryRequest, ChatHistoryResponse, ConversationCreate, ChatMessageCreate
from app.core.logging import get_logger
from app.core.settings import settings
from app.services.ai_auth_service import AIAuthService

logger = get_logger(__name__)


class AIOrchestratorService(AIOrchestratorServiceInterface):
    """Service for communication with AI Orchestrator microservice."""
    
    def __init__(self):
        self.base_url = settings.ai.ai_orchestrator_url
        self.timeout = 60.0
        self.max_retries = 3
        self.auth_service = AIAuthService()
    
    async def send_chat_message(self, chat_request: ChatRequest, is_authenticated: bool) -> ChatResponse:
        """Send chat message to AI Orchestrator."""
        start_time = time.time()
        
        try:
            endpoint = f"{self.base_url}/api/v1/chat"
            
            # Visitantes não podem gerar imagens
            context = chat_request.context or {}
            if not is_authenticated:
                context["disable_visual_generation"] = True
            
            payload = {
                "message": chat_request.message,
                "user_id": str(chat_request.user_id) if chat_request.user_id else None,
                "conversation_id": chat_request.conversation_id if is_authenticated else None,
                "session_id": chat_request.session_id if not is_authenticated else None,
                "context": context,
                "request_id": f"req_{int(time.time() * 1000)}"
            }
            
            # Get authentication headers
            auth_headers = self.auth_service.get_auth_headers()
            
            logger.info(f"Sending request to AI Orchestrator for user {chat_request.user_id or 'guest'}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=auth_headers)
                response.raise_for_status()
                
                data = response.json()
                processing_time = (time.time() - start_time) * 1000
                
                logger.info(f"AI response received in {processing_time:.0f}ms")
                
                return ChatResponse(
                    response=data.get("response", ""),
                    has_image=data.get("visual_url") is not None,
                    image_url=data.get("visual_url"),
                    recommendations=data.get("recommendations", []),
                    reasoning_steps=data.get("reasoning_steps", []),
                    confidence=data.get("confidence"),
                    processing_time_ms=data.get("processing_time_ms", processing_time),
                    request_id=data.get("request_id"),
                    response_id=data.get("response_id")
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"AI service HTTP error: {e.response.status_code}")
            raise Exception("AI service communication failed")
            
        except httpx.TimeoutException:
            logger.error("AI service timeout")
            raise Exception("AI service is taking too long to respond")
            
        except httpx.RequestError as e:
            logger.error(f"AI service connection error: {e}")
            raise Exception("Failed to connect to AI service")
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise Exception("AI service error occurred")
    
    async def generate_visual_simulation(self, visual_request: VisualSimulationRequest) -> VisualSimulationResponse:
        """Generate visual simulation via AI Orchestrator."""
        start_time = time.time()
        
        try:
            endpoint = f"{self.base_url}/api/v1/visual/generate"
            
            payload = {
                "prompt": visual_request.prompt,
                "user_id": visual_request.user_id,
                "paint_id": visual_request.paint_id,
                "room_type": visual_request.room_type,
                "style": visual_request.style,
                "request_id": f"req_{int(time.time() * 1000)}"
            }
            
            # Get authentication headers
            auth_headers = self.auth_service.get_auth_headers()
            
            async with httpx.AsyncClient(timeout=60.0) as client:  # Maior timeout para geração de imagem
                response = await client.post(endpoint, json=payload, headers=auth_headers)
                response.raise_for_status()
                
                data = response.json()
                processing_time = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Visual simulation generated successfully - "
                    f"user_id: {visual_request.user_id}, "
                    f"processing_time_ms: {processing_time:.2f}"
                )
                
                return VisualSimulationResponse(
                    image_url=data.get("image_url", ""),
                    prompt_used=data.get("prompt_used", visual_request.prompt),
                    processing_time_ms=data.get("processing_time_ms", processing_time),
                    request_id=data.get("request_id", ""),
                    response_id=data.get("response_id", "")
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"AI Orchestrator HTTP error: {e.response.status_code}"
            logger.error(
                f"{error_msg} - user_id: {visual_request.user_id}, "
                f"prompt: {visual_request.prompt[:50]}"
            )
            raise Exception(f"Failed to generate visual simulation: {error_msg}")
            
        except httpx.TimeoutException:
            error_msg = "Visual generation timeout"
            logger.error(
                f"{error_msg} - user_id: {visual_request.user_id}, "
                f"prompt: {visual_request.prompt[:50]}"
            )
            raise Exception("Visual generation is taking too long. Please try again.")
            
        except Exception as e:
            error_msg = f"Unexpected error generating visual: {str(e)}"
            logger.error(
                f"{error_msg} - user_id: {visual_request.user_id}, "
                f"prompt: {visual_request.prompt[:50]}"
            )
            raise Exception("Failed to generate visual simulation. Please try again.")
    
    async def get_chat_history(self, history_request: ChatHistoryRequest) -> ChatHistoryResponse:
        """Get chat history from AI Orchestrator."""
        try:
            endpoint = f"{self.base_url}/api/v1/chat/history/{history_request.user_id}"
            
            params = {
                "limit": history_request.limit
            }
            
            if history_request.conversation_id:
                params["conversation_id"] = history_request.conversation_id
            
            # Get authentication headers
            auth_headers = self.auth_service.get_auth_headers()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params, headers=auth_headers)
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(
                    f"Chat history retrieved successfully - "
                    f"user_id: {history_request.user_id}, "
                    f"count: {len(data.get('history', []))}"
                )
                
                from app.domain.entities import ChatMessage
                messages = []
                for msg in data.get("history", []):
                    messages.append(ChatMessage(
                        id=msg.get("id"),
                        user_id=history_request.user_id,
                        message=msg.get("message", ""),
                        response=msg.get("response"),
                        is_user=True,
                        has_image=False,
                        intent=msg.get("intent"),
                        confidence=msg.get("confidence"),
                        tools_used=msg.get("tools_used", []),
                        processing_time_ms=msg.get("processing_time_ms"),
                        conversation_id=msg.get("conversation_id"),
                        created_at=msg.get("created_at")
                    ))
                
                return ChatHistoryResponse(
                    messages=messages,
                    total=len(messages),
                    has_more=len(messages) >= history_request.limit
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"AI Orchestrator HTTP error: {e.response.status_code}"
            logger.error(
                f"{error_msg} - user_id: {history_request.user_id}"
            )
            raise Exception(f"Failed to get chat history: {error_msg}")
            
        except Exception as e:
            error_msg = f"Unexpected error getting chat history: {str(e)}"
            logger.error(
                f"{error_msg} - user_id: {history_request.user_id}"
            )
            raise Exception("Failed to get chat history. Please try again.")
    
    async def health_check(self) -> bool:
        """Check if AI Orchestrator is healthy."""
        try:
            endpoint = f"{self.base_url}/api/v1/health"
            
            # Get authentication headers
            auth_headers = self.auth_service.get_auth_headers()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint, headers=auth_headers)
                response.raise_for_status()
                
                logger.debug("AI Orchestrator health check successful")
                return True
                
        except Exception as e:
            logger.warning(f"AI Orchestrator health check failed: {str(e)}")
            return False
    
    

