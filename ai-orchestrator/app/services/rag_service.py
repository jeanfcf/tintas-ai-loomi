"""RAG service using Backend API with proper error handling."""
from typing import List, Dict, Any, Optional
from app.core.logging import AILogger
from app.services.api_client import APIClient

logger = AILogger(__name__)


class RAGService:
    """RAG service that uses Backend API for paint search with proper error handling."""
    
    def __init__(self):
        self.api_client = APIClient()
    
    def search_with_retrieval_sync(
        self,
        query: str,
        limit: int = 10,
        semantic_threshold: float = 0.7,
        keyword_boost: float = 0.3,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous version of retrieval."""
        try:
            results = self.api_client.search_similar_paints_sync(
                query=query,
                limit=limit,
                threshold=semantic_threshold
            )
            return self._filter_results_by_environment(results, environment, query, limit)
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "similar_paint_search", "query": query, "limit": limit}
            )
            return []

    async def search_with_retrieval(
        self,
        query: str,
        limit: int = 10,
        semantic_threshold: float = 0.7,
        keyword_boost: float = 0.3,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar paints using the Backend API."""
        try:
            results = await self.api_client.search_similar_paints(
                query=query,
                limit=limit,
                threshold=semantic_threshold
            )
            return self._filter_results_by_environment(results, environment, query, limit)
        except Exception as e:
            logger.log_error(
                error=e,
                context={"operation": "similar_paint_search", "query": query, "limit": limit}
            )
            return []
    
    def _filter_results_by_environment(
        self, 
        results: List[Dict[str, Any]], 
        environment: Optional[str], 
        query: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Filter results by environment and log the operation."""
        if environment and results:
            env_mapping = {
                "internal": "interno",
                "external": "externo",
                "interno": "interno",
                "externo": "externo"
            }
            target_env = env_mapping.get(environment, environment)
            filtered_results = []
            for paint in results:
                paint_env = paint.get("environment", "")
                if paint_env == target_env or "interno/externo" in paint_env or "externo/interno" in paint_env:
                    filtered_results.append(paint)
            results = filtered_results
        
        logger.log_tool_execution(
            tool_name="rag_search",
            input_params={"query": query, "limit": limit, "environment": environment},
            output=f"Found {len(results)} similar paints",
            execution_time=0.0
        )
        
        return results