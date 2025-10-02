"""JWT authentication for AI Orchestrator."""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import get_settings
from app.core.logging import AILogger

logger = AILogger(__name__)


class JWTService:
    """JWT service for AI Orchestrator authentication."""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = getattr(self.settings, 'jwt_secret_key', 'ai_orchestrator_secret_key_2024')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours for service tokens
    
    def create_service_token(self, service_name: str, permissions: list = None) -> str:
        """Create JWT token for service authentication."""
        try:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode = {
                "sub": f"service_{service_name}",
                "service_name": service_name,
                "permissions": permissions or ["read", "write", "rag", "chat"],
                "token_type": "service",
                "exp": expire,
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.log_tool_execution(
                tool_name="create_service_token",
                input_params={"service_name": service_name, "permissions": permissions},
                output=f"Created token for {service_name}",
                execution_time=0.0
            )
            
            return token
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"service_name": service_name, "operation": "create_service_token"}
            )
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                logger.log_error(
                    error=Exception("Token expired"),
                    context={"token_sub": payload.get("sub")}
                )
                return None
            
            # Validate token type
            if payload.get("token_type") != "service":
                logger.log_error(
                    error=Exception("Invalid token type"),
                    context={"token_type": payload.get("token_type")}
                )
                return None
            
            logger.log_tool_execution(
                tool_name="verify_token",
                input_params={"token_sub": payload.get("sub")},
                output="Token verified successfully",
                execution_time=0.0
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.log_error(
                error=Exception("Token expired"),
                context={"operation": "verify_token"}
            )
            return None
        except jwt.InvalidTokenError as e:
            logger.log_error(
                error=e,
                context={"operation": "verify_token"}
            )
            return None
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "verify_token"}
            )
            return None
    
    def has_permission(self, token_payload: Dict[str, Any], required_permission: str) -> bool:
        """Check if token has required permission."""
        try:
            permissions = token_payload.get("permissions", [])
            return required_permission in permissions
        except Exception as e:
            logger.log_error(
                error=e,
                context={"required_permission": required_permission}
            )
            return False
