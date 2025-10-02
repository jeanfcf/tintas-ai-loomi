"""Embedding service for paint data - now using RAG service."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.services.rag_service import RAGService

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating and managing paint embeddings using RAG service."""
    
    def __init__(self):
        self.rag_service = RAGService()
    
    async def generate_and_store_embedding(self, db: Session, paint_id: int) -> None:
        """Generate and store embedding for a paint."""
        return await self.rag_service.generate_and_store_embedding(db, paint_id)
    
    async def search_similar_paints(
        self, 
        query: str, 
        db: Session, 
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar paints using embeddings."""
        return await self.rag_service.search_similar_paints(
            query=query,
            db=db,
            limit=limit,
            threshold=threshold
        )
    
    def get_embedding_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about embeddings in the database."""
        return self.rag_service.get_embedding_stats(db)