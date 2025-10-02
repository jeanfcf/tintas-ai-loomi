"""AI Orchestrator authentication service for backend."""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIAuthService:
    """Service for authenticating with AI Orchestrator."""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'ai_jwt_secret_key', 'ai_orchestrator_secret_key_2024')
        self.algorithm = "HS256"
        self.service_name = "backend_api"
        self.permissions = ["read", "write", "rag", "chat", "mcp"]
    
    def create_service_token(self) -> str:
        """Create JWT token for AI Orchestrator authentication."""
        try:
            expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours
            to_encode = {
                "sub": f"service_{self.service_name}",
                "service_name": self.service_name,
                "permissions": self.permissions,
                "token_type": "service",
                "exp": expire,
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"Created service token for {self.service_name}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating service token: {e}")
            raise
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for AI Orchestrator requests."""
        try:
            token = self.create_service_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Service-Name": self.service_name
            }
        except Exception as e:
            logger.error(f"Error creating auth headers: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token (for testing purposes)."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                logger.warning("Service token expired")
                return None
            
            logger.info(f"Token verified for service: {payload.get('service_name')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Service token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid service token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
