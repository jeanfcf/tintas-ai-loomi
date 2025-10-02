"""Dependency injection container."""
from typing import Dict, Any, Type, Optional
from app.domain.repositories import UserRepositoryInterface, PaintRepositoryInterface
from app.domain.services import AuthServiceInterface, UserServiceInterface, AuthApplicationServiceInterface, PaintServiceInterface, CSVImportServiceInterface, AIOrchestratorServiceInterface
from app.services.embedding_service import EmbeddingService
from app.core.logging import get_logger

logger = get_logger(__name__)


class Container:
    """Dependency injection container with configurable implementations."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._implementations: Dict[Type, Type] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialize_default_implementations()
        self._initialize_services()
    
    def register(self, interface: Type, implementation: Type) -> None:
        """Register an interface with its implementation."""
        self._implementations[interface] = implementation
        logger.info(f"Registered {interface.__name__} -> {implementation.__name__}")
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance."""
        self._singletons[name] = instance
        logger.info(f"Registered singleton: {name}")
    
    def _initialize_default_implementations(self):
        """Map interfaces to default implementations."""
        from app.infrastructure.repositories import UserRepository, PaintRepository
        from app.application.services import AuthService, UserService, AuthApplicationService, PaintService, CSVImportService
        from app.application.ai_orchestrator_service import AIOrchestratorService
        
        self._implementations[UserRepositoryInterface] = UserRepository
        self._implementations[PaintRepositoryInterface] = PaintRepository
        self._implementations[AuthServiceInterface] = AuthService
        self._implementations[UserServiceInterface] = UserService
        self._implementations[AuthApplicationServiceInterface] = AuthApplicationService
        self._implementations[PaintServiceInterface] = PaintService
        self._implementations[CSVImportServiceInterface] = CSVImportService
        self._implementations[AIOrchestratorServiceInterface] = AIOrchestratorService
    
    def _initialize_services(self):
        """Initialize all services with dependency injection."""
        try:
            self._services['user_repository'] = self._implementations[UserRepositoryInterface]()
            self._services['paint_repository'] = self._implementations[PaintRepositoryInterface]()
            self._services['auth_service'] = self._implementations[AuthServiceInterface]()
            
            self._services['user_service'] = self._implementations[UserServiceInterface](
                user_repo=self._services['user_repository'],
                auth_service=self._services['auth_service']
            )
            
            self._services['paint_service'] = self._implementations[PaintServiceInterface](
                paint_repo=self._services['paint_repository']
            )
            
            self._services['csv_import_service'] = self._implementations[CSVImportServiceInterface](
                paint_service=self._services['paint_service']
            )
            
            self._services['auth_application_service'] = self._implementations[AuthApplicationServiceInterface](
                auth_service=self._services['auth_service'],
                user_service=self._services['user_service']
            )
            
            # Initialize AI Orchestrator service
            self._services['ai_orchestrator_service'] = self._implementations[AIOrchestratorServiceInterface]()
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    def get(self, service_name: str) -> Any:
        """Get service by name."""
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        if service_name in self._services:
            return self._services[service_name]
        
        raise KeyError(f"Service '{service_name}' not found")
    
    def get_user_repository(self) -> UserRepositoryInterface:
        """Get user repository instance."""
        return self._services['user_repository']
    
    def get_auth_service(self) -> AuthServiceInterface:
        """Get auth service instance."""
        return self._services['auth_service']
    
    def get_user_service(self) -> UserServiceInterface:
        """Get user service instance."""
        return self._services['user_service']
    
    def get_auth_application_service(self) -> AuthApplicationServiceInterface:
        """Get auth application service instance."""
        return self._services['auth_application_service']
    
    def get_paint_repository(self) -> PaintRepositoryInterface:
        """Get paint repository instance."""
        return self._services['paint_repository']
    
    def get_paint_service(self) -> PaintServiceInterface:
        """Get paint service instance."""
        return self._services['paint_service']
    
    def get_csv_import_service(self) -> CSVImportServiceInterface:
        """Get CSV import service instance."""
        return self._services['csv_import_service']
    
    def get_ai_orchestrator_service(self) -> AIOrchestratorServiceInterface:
        """Get AI Orchestrator service instance."""
        return self._services['ai_orchestrator_service']
    
    def get_embedding_service(self) -> EmbeddingService:
        """Get Embedding service instance."""
        if 'embedding_service' not in self._services:
            self._services['embedding_service'] = EmbeddingService()
        return self._services['embedding_service']
    
    
    def configure_from_settings(self, settings) -> None:
        """Configure container based on settings."""
        logger.info("Container configured from settings")


# Global container instance
container = Container()
