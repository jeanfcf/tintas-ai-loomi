"""Session management middleware for automatic session handling."""
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically manage session IDs for guest users."""
    
    def __init__(self, app, session_cookie_name: str = "guest_session_id"):
        super().__init__(app)
        self.session_cookie_name = session_cookie_name
        self.session_max_age = 30 * 60  # 30 minutos em segundos
    
    async def dispatch(self, request: Request, call_next):
        """Process request and manage session ID."""
        
        # Verificar se é uma requisição de chat
        if not self._is_chat_request(request):
            response = await call_next(request)
            return response
        
        # Obter ou criar session_id
        session_id = self._get_or_create_session_id(request)
        
        # Adicionar session_id ao request state para uso nos endpoints
        request.state.guest_session_id = session_id
        
        # Processar requisição
        response = await call_next(request)
        
        # Definir cookie se necessário
        if session_id and not request.cookies.get(self.session_cookie_name):
            response.set_cookie(
                key=self.session_cookie_name,
                value=session_id,
                max_age=self.session_max_age,
                httponly=True,
                secure=False,  # Em produção, usar True com HTTPS
                samesite="lax"
            )
            logger.debug(f"Set session cookie for guest: {session_id}")
        
        return response
    
    def _is_chat_request(self, request: Request) -> bool:
        """Check if request is for chat endpoints."""
        return (
            request.url.path.startswith("/api/v1/chat/") and
            request.method in ["POST", "GET", "PUT", "DELETE"]
        )
    
    def _get_or_create_session_id(self, request: Request) -> str:
        """Get existing session ID or create new one."""
        
        # 1. Tentar obter do cookie
        session_id = request.cookies.get(self.session_cookie_name)
        if session_id:
            logger.debug(f"Found existing session cookie: {session_id}")
            return session_id
        
        # 2. Tentar obter do header (para APIs que não usam cookies)
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            logger.debug(f"Found session header: {session_id}")
            return session_id
        
        # 3. Tentar obter do query parameter
        session_id = request.query_params.get("session_id")
        if session_id:
            logger.debug(f"Found session query param: {session_id}")
            return session_id
        
        # 4. Criar novo session_id
        session_id = str(uuid.uuid4())
        logger.info(f"Created new guest session: {session_id}")
        return session_id


