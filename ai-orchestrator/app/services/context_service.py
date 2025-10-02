"""Context management service for user sessions and conversation history."""
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.logging import AILogger
from app.services.api_client import APIClient

logger = AILogger(__name__)


class ContextService:
    """Service for managing conversation context and user sessions."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.api_client = APIClient()
            self.context_cache = {}  # In-memory cache for active contexts
            self.session_timeout = 60 * 60  # 60 minutes (increased)
            self.max_context_size = 50  # Maximum number of contexts to keep in memory
            self.max_conversation_history = 30  # Maximum conversation history per context
            self._initialized = True
    
    async def get_or_create_context(
        self, 
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get or create context for user/session."""
        try:
            # Validação rigorosa: exatamente um ID deve ser fornecido
            if conversation_id and session_id:
                raise ValueError("Não é possível fornecer conversation_id e session_id simultaneamente")
            if not conversation_id and not session_id:
                raise ValueError("conversation_id ou session_id deve ser fornecido pelo backend")
            
            # Determine context key
            if conversation_id:
                context_key = f"conversation_{conversation_id}"
            else:  # session_id
                context_key = f"session_{session_id}"
            
            # Check if context exists in cache
            logger.logger.info(f"Looking for context with key: {context_key}")
            logger.logger.info(f"Cache has {len(self.context_cache)} contexts: {list(self.context_cache.keys())}")
            logger.logger.info(f"Input params - session_id: {session_id}, conversation_id: {conversation_id}")
            
            if context_key in self.context_cache:
                context = self.context_cache[context_key]
                logger.logger.info(f"Context found in cache: {context_key}")
                if self._is_context_valid(context):
                    # Update last accessed time
                    context["last_accessed"] = datetime.utcnow().isoformat()
                    logger.logger.info(f"Context found in cache: {context_key}, history: {len(context.get('conversation_history', []))} messages")
                    return context
                else:
                    # Remove expired context
                    del self.context_cache[context_key]
                    logger.logger.info(f"Expired context removed: {context_key}")
            else:
                logger.logger.info(f"Context not found in cache: {context_key}")
            
            # Create new context
            context = await self._create_new_context(
                session_id=session_id,
                conversation_id=conversation_id,
                context_key=context_key
            )
            
            # Cache the context with cleanup
            self.context_cache[context_key] = context
            await self._cleanup_contexts_if_needed()
            
            logger.logger.info(f"New context created: {context_key}, history: {len(context.get('conversation_history', []))} messages")
            
            logger.log_tool_execution(
                tool_name="get_or_create_context",
                input_params={
                    "session_id": session_id,
                    "conversation_id": conversation_id
                },
                output=f"Created context for {context_key}",
                execution_time=0.0
            )
            
            return context
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "session_id": session_id,
                    "conversation_id": conversation_id
                }
            )
            # Return minimal context on error
            return self._create_minimal_context()
    
    async def _create_new_context(
        self,
        session_id: Optional[str],
        conversation_id: Optional[str],
        context_key: str
    ) -> Dict[str, Any]:
        """Create a new context with proper initialization."""
        now = datetime.utcnow()
        
        context = {
            "context_key": context_key,
            "session_id": session_id,
            "conversation_id": conversation_id,
            "created_at": now.isoformat(),
            "last_accessed": now.isoformat(),
            "message_count": 0,
            "conversation_history": [],
            "user_preferences": {},
            "current_intent": None,
            "context_data": {
                "last_search_query": None,
                "last_recommendations": [],
                "preferred_environment": None,
                "preferred_colors": [],
                "preferred_features": []
            },
            "is_active": True
        }
        
        
        return context
    
    def _create_minimal_context(self) -> Dict[str, Any]:
        """Create minimal context for error cases."""
        return {
            "context_key": f"minimal_{uuid.uuid4()}",
            "session_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "message_count": 0,
            "conversation_history": [],
            "user_preferences": {},
            "current_intent": None,
            "context_data": {},
            "is_active": True
        }
    
    async def _load_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Load user preferences from API."""
        try:
            # This would call the API to get user preferences
            # For now, return empty preferences
            return {}
        except Exception as e:
            logger.log_error(
                error=e,
                context={"user_id": user_id, "operation": "load_user_preferences"}
            )
            return {}
    
    def _is_context_valid(self, context: Dict[str, Any]) -> bool:
        """Check if context is still valid (not expired)."""
        try:
            last_accessed = datetime.fromisoformat(context["last_accessed"])
            now = datetime.utcnow()
            return (now - last_accessed).seconds < self.session_timeout
        except:
            return False
    
    async def update_context(
        self,
        context: Dict[str, Any],
        message: str,
        response: str,
        intent: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update context with new conversation data."""
        try:
            # Update last accessed time
            context["last_accessed"] = datetime.utcnow().isoformat()
            context["message_count"] += 1
            
            # Add to conversation history
            conversation_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "response": response,
                "intent": intent,
                "tools_used": tools_used or [],
                "metadata": metadata or {}
            }
            
            context["conversation_history"].append(conversation_entry)
            
            # Update current intent
            if intent:
                context["current_intent"] = intent
            
            # Update context data based on conversation
            await self._update_context_data(context, message, response, intent)
            
            # Limit conversation history (keep last N exchanges)
            if len(context["conversation_history"]) > self.max_conversation_history:
                context["conversation_history"] = context["conversation_history"][-self.max_conversation_history:]
            
            # Update cache
            self.context_cache[context["context_key"]] = context
            
            logger.log_tool_execution(
                tool_name="update_context",
                input_params={
                    "context_key": context["context_key"],
                    "message_length": len(message),
                    "intent": intent
                },
                output=f"Updated context with {len(context['conversation_history'])} messages",
                execution_time=0.0
            )
            
            return context
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "context_key": context.get("context_key"),
                    "message": message[:100]
                }
            )
            return context
    
    async def _update_context_data(
        self,
        context: Dict[str, Any],
        message: str,
        response: str,
        intent: Optional[str]
    ):
        """Update context data based on conversation content."""
        try:
            # Extract preferences from conversation
            message_lower = message.lower()
            
            # Environment preferences
            if any(word in message_lower for word in ["quarto", "sala", "cozinha", "banheiro"]):
                if "quarto" in message_lower:
                    context["context_data"]["preferred_environment"] = "internal"
                elif "fachada" in message_lower or "externa" in message_lower:
                    context["context_data"]["preferred_environment"] = "external"
            
            # Color preferences
            color_keywords = ["azul", "vermelho", "verde", "amarelo", "branco", "preto", "cinza"]
            for color in color_keywords:
                if color in message_lower:
                    if color not in context["context_data"]["preferred_colors"]:
                        context["context_data"]["preferred_colors"].append(color)
            
            # Feature preferences
            feature_keywords = ["lavável", "anti-mofo", "sem odor", "resistente", "durabilidade"]
            for feature in feature_keywords:
                if feature in message_lower:
                    if feature not in context["context_data"]["preferred_features"]:
                        context["context_data"]["preferred_features"].append(feature)
            
            # Store last search query
            if intent in ["search_paint", "get_recommendation"]:
                context["context_data"]["last_search_query"] = message
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "update_context_data"}
            )
    
    async def get_conversation_summary(self, context: Dict[str, Any]) -> str:
        """Get a summary of the conversation for context."""
        try:
            if not context["conversation_history"]:
                return "Nova conversa iniciada."
            
            # Get last few messages for context (reduced from 5 to 3 for efficiency)
            recent_messages = context["conversation_history"][-3:]
            
            summary = "Contexto da conversa:\n"
            for msg in recent_messages:
                # Truncate message to 80 chars for efficiency
                message_preview = msg['message'][:80] + "..." if len(msg['message']) > 80 else msg['message']
                summary += f"- Usuário: {message_preview}\n"
                if msg.get('intent'):
                    summary += f"  Intenção: {msg['intent']}\n"
            
            # Add user preferences (only if they exist)
            context_data = context.get("context_data", {})
            if context_data.get("preferred_environment"):
                summary += f"\nAmbiente preferido: {context_data['preferred_environment']}\n"
            
            if context_data.get("preferred_colors"):
                colors = context_data['preferred_colors'][:3]  # Limit to 3 colors
                summary += f"Cores preferidas: {', '.join(colors)}\n"
            
            return summary
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"context_key": context.get("context_key")}
            )
            return "Erro ao gerar resumo da conversa."
    
    async def _cleanup_contexts_if_needed(self):
        """Clean up contexts if cache size exceeds limit."""
        try:
            if len(self.context_cache) <= self.max_context_size:
                return
            
            # Sort contexts by last accessed time (oldest first)
            sorted_contexts = sorted(
                self.context_cache.items(),
                key=lambda x: x[1].get("last_accessed", "1970-01-01T00:00:00")
            )
            
            # Remove oldest contexts until we're under the limit
            contexts_to_remove = len(self.context_cache) - self.max_context_size
            for i in range(contexts_to_remove):
                key, _ = sorted_contexts[i]
                del self.context_cache[key]
            
            logger.log_tool_execution(
                tool_name="cleanup_contexts_if_needed",
                input_params={"max_size": self.max_context_size},
                output=f"Cleaned up {contexts_to_remove} contexts",
                execution_time=0.0
            )
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "cleanup_contexts_if_needed"}
            )
    
    async def cleanup_expired_contexts(self):
        """Clean up expired contexts from cache."""
        try:
            now = datetime.utcnow()
            expired_keys = []
            
            for key, context in self.context_cache.items():
                if not self._is_context_valid(context):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.context_cache[key]
            
            if expired_keys:
                logger.log_tool_execution(
                    tool_name="cleanup_expired_contexts",
                    input_params={"total_contexts": len(self.context_cache)},
                    output=f"Cleaned up {len(expired_keys)} expired contexts",
                    execution_time=0.0
                )
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "cleanup_expired_contexts"}
            )
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about active contexts."""
        try:
            now = datetime.utcnow()
            active_contexts = 0
            expired_contexts = 0
            total_messages = 0
            
            for context in self.context_cache.values():
                if self._is_context_valid(context):
                    active_contexts += 1
                    total_messages += context.get("message_count", 0)
                else:
                    expired_contexts += 1
            
            return {
                "active_contexts": active_contexts,
                "expired_contexts": expired_contexts,
                "total_messages": total_messages,
                "cache_size": len(self.context_cache),
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "get_context_stats"}
            )
            return {"error": str(e)}
