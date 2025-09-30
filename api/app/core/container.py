"""Dependency injection container."""
from typing import Dict, Any, Type, Optional
from app.domain.repositories import UserRepositoryInterface
from app.domain.services import AuthServiceInterface, UserServiceInterface, AuthApplicationServiceInterface
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
        from app.infrastructure.repositories import UserRepository
        from app.application.services import AuthService, UserService, AuthApplicationService
        
        self._implementations[UserRepositoryInterface] = UserRepository
        self._implementations[AuthServiceInterface] = AuthService
        self._implementations[UserServiceInterface] = UserService
        self._implementations[AuthApplicationServiceInterface] = AuthApplicationService
    
    def _initialize_services(self):
        """Initialize all services with dependency injection."""
        try:
            self._services['user_repository'] = self._implementations[UserRepositoryInterface]()
            self._services['auth_service'] = self._implementations[AuthServiceInterface]()
            
            self._services['user_service'] = self._implementations[UserServiceInterface](
                user_repo=self._services['user_repository'],
                auth_service=self._services['auth_service']
            )
            
            self._services['auth_application_service'] = self._implementations[AuthApplicationServiceInterface](
                auth_service=self._services['auth_service'],
                user_service=self._services['user_service']
            )
            
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
    
    def configure_from_settings(self, settings) -> None:
        """Configure container based on settings."""
        logger.info("Container configured from settings")


# Global container instance
container = Container()
