"""Agent service for AI Orchestrator."""
import time
from typing import Dict, Any, List, Optional
from app.core.config import get_settings
from app.core.logging import AILogger
from app.models.schemas import ChatRequest, AgentResponse
from app.agents.paint_agent_simple import PaintAgentSimple

logger = AILogger(__name__)


class AgentService:
    """Main agent service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.agent = PaintAgentSimple()
    
    async def process_query(
        self,
        message: str,
        context: Dict[str, Any],
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AgentResponse:
        """Process user query with AI agent."""
        start_time = time.time()
        
        try:
            # Log processing start
            logger.logger.info(
                f"Starting agent processing - conversation_id: {conversation_id}, session_id: {session_id}, message: '{message[:50]}...'"
            )
            
            # Process with agent
            response = await self.agent.process_query(
                message=message,
                context=context,
                conversation_id=conversation_id,
                session_id=session_id
            )
            logger.logger.info(f"Agent processing completed - response: {len(response.response) if response.response else 0} chars")
            
            processing_time = time.time() - start_time
            
            logger.log_agent_decision(
                user_message=message,
                intent=response.intent if hasattr(response, 'intent') else "general_question",
                tools_used=response.tools_used,
                response=response.response,
                processing_time=processing_time,
                conversation_id=conversation_id,
                confidence=response.confidence,
                reasoning_steps=len(response.reasoning_steps) if hasattr(response, 'reasoning_steps') else 0
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.log_error(
                error=e,
                context={
                    "message": message,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "processing_time": processing_time
                }
            )
            raise
    
    
