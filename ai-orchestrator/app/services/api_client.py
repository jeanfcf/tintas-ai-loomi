"""API client for communicating with the main backend API."""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.core.logging import AILogger

logger = AILogger(__name__)


class APIClient:
    """Client for communicating with the main backend API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = getattr(self.settings, 'api_base_url', 'http://api:8000')
        self.timeout = 30.0
    
    async def get_paints(
        self, 
        limit: int = 100, 
        offset: int = 0,
        environment: Optional[str] = None,
        color: Optional[str] = None,
        surface_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get paints from the main API."""
        try:
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if environment:
                params["environment"] = environment
            if color:
                params["color"] = color
            if surface_types:
                params["surface_types"] = surface_types
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/paints",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("items", [])
                
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "operation": "get_paints",
                    "params": {
                        "limit": limit,
                        "offset": offset,
                        "environment": environment,
                        "color": color
                    }
                }
            )
            return []
    
    async def search_paints(
        self, 
        query: str, 
        limit: int = 10,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search paints using the main API search endpoint."""
        try:
            params = {
                "q": query,
                "limit": limit
            }
            
            if environment:
                params["environment"] = environment
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/paints/search",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("items", [])
                
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "operation": "search_paints",
                    "query": query,
                    "limit": limit
                }
            )
            return []
    
    async def get_paint_by_id(self, paint_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific paint by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/paints/{paint_id}"
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "operation": "get_paint_by_id",
                    "paint_id": paint_id
                }
            )
            return None
    
    async def health_check(self) -> bool:
        """Check if the main API is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/health")
                response.raise_for_status()
                return True
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "health_check"}
            )
            return False
    
    async def search_similar_paints(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar paints using embeddings."""
        try:
            params = {
                "query": query,
                "limit": limit,
                "threshold": threshold
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/paints/search/similar",
                    params=params
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "operation": "search_similar_paints",
                    "query": query,
                    "limit": limit
                }
            )
            return []
    
    def search_similar_paints_sync(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar paints using embeddings (synchronous)."""
        try:
            import requests
            
            params = {
                "query": query,
                "limit": limit,
                "threshold": threshold
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/paints/search/similar",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={
                    "operation": "search_similar_paints_sync",
                    "query": query,
                    "limit": limit
                }
            )
            return []