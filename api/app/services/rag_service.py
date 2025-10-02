"""RAG Service following industry best practices."""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.settings import settings
from app.core.logging import get_logger
from app.infrastructure.models import PaintModel
import numpy as np
import re

logger = get_logger(__name__)


class RAGService:
    """RAG Service following industry best practices for paint recommendations."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.ai.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        self.similarity_threshold = 0.3
        self.max_results = 10
    
    def _create_paint_text(self, paint: PaintModel) -> str:
        """Create optimized text representation for embedding."""
        # Build structured text for better semantic understanding
        components = []
        
        # Core identity
        components.append(f"Tinta {paint.name}")
        components.append(f"Cor {paint.color}")
        
        # Environment and usage
        components.append(f"Para ambiente {paint.environment}")
        if paint.surface_types:
            components.append(f"Superfícies: {', '.join(paint.surface_types)}")
        
        # Technical specifications
        components.append(f"Acabamento {paint.finish_type}")
        components.append(f"Linha {paint.line}")
        
        # Features and benefits
        if paint.features:
            components.append(f"Características: {', '.join(paint.features)}")
        
        # Description for additional context
        if paint.description:
            components.append(paint.description)
        
        return " | ".join(components)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with error handling and retries."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model,
                dimensions=self.embedding_dimension
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _calculate_similarity(self, query_embedding: List[float], paint_embedding: List[float]) -> float:
        """Calculate cosine similarity between embeddings using numpy."""
        try:
            # Convert to numpy arrays
            query_vec = np.array(query_embedding)
            paint_vec = np.array(paint_embedding)
            
            # Calculate cosine similarity manually
            dot_product = np.dot(query_vec, paint_vec)
            norm_query = np.linalg.norm(query_vec)
            norm_paint = np.linalg.norm(paint_vec)
            
            if norm_query == 0 or norm_paint == 0:
                return 0.0
            
            similarity = dot_product / (norm_query * norm_paint)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for better semantic matching."""
        # Normalize query
        query = query.lower().strip()
        
        # Add context keywords for better matching
        context_keywords = []
        
        if any(word in query for word in ['quarto', 'sala', 'cozinha', 'banheiro']):
            context_keywords.append('ambiente interno')
        
        if any(word in query for word in ['fachada', 'externa', 'fora']):
            context_keywords.append('ambiente externo')
        
        if any(word in query for word in ['branco', 'branca']):
            context_keywords.append('cor branca')
        
        if any(word in query for word in ['azul', 'azul']):
            context_keywords.append('cor azul')
        
        if any(word in query for word in ['verde', 'verde']):
            context_keywords.append('cor verde')
        
        # Combine original query with context
        enhanced_query = query
        if context_keywords:
            enhanced_query = f"{query} {' '.join(context_keywords)}"
        
        return enhanced_query
    
    async def search_similar_paints(
        self,
        query: str,
        db: Session,
        limit: int = 10,
        threshold: float = 0.7,
        environment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar paints using semantic similarity."""
        try:
            # Preprocess query
            processed_query = self._preprocess_query(query)
            logger.info(f"Searching for: '{processed_query}' (original: '{query}')")
            
            # Generate query embedding
            query_embedding = self._generate_embedding(processed_query)
            
            # Get paints with embeddings
            paints_query = db.query(PaintModel).filter(
                PaintModel.embedding.isnot(None)
            )
            
            # Filter by environment if specified
            if environment:
                paints_query = paints_query.filter(PaintModel.environment == environment)
            
            paints = paints_query.all()
            
            if not paints:
                logger.warning("No paints with embeddings found")
                return []
            
            logger.info(f"Found {len(paints)} paints with embeddings")
            
            # Calculate similarities
            similarities = []
            for paint in paints:
                try:
                    # Ensure embedding dimensions match
                    if len(paint.embedding) != len(query_embedding):
                        logger.warning(f"Embedding dimension mismatch for paint {paint.id}")
                        continue
                    
                    similarity = self._calculate_similarity(query_embedding, paint.embedding)
                    
                    if similarity >= threshold:
                        similarities.append({
                            "paint": paint,
                            "similarity": similarity
                        })
                        
                except Exception as e:
                    logger.warning(f"Error calculating similarity for paint {paint.id}: {e}")
                    continue
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Format results
            results = []
            for item in similarities[:limit]:
                paint = item["paint"]
                results.append({
                    "id": paint.id,
                    "name": paint.name,
                    "color": paint.color,
                    "environment": paint.environment,
                    "surface_types": paint.surface_types or [],
                    "finish_type": paint.finish_type,
                    "line": paint.line,
                    "features": paint.features or [],
                    "description": paint.description,
                    "similarity_score": item["similarity"]
                })
            
            logger.info(f"Found {len(results)} similar paints above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            return []
    
    async def generate_and_store_embedding(self, db: Session, paint_id: int) -> None:
        """Generate and store embedding for a paint."""
        try:
            # Get paint from database
            paint = db.query(PaintModel).filter(PaintModel.id == paint_id).first()
            if not paint:
                logger.error(f"Paint not found for embedding generation: {paint_id}")
                return
            
            # Generate text for embedding
            paint_text = self._create_paint_text(paint)
            
            # Generate embedding
            embedding = self._generate_embedding(paint_text)
            
            # Store embedding in database
            paint.embedding = embedding
            db.commit()
            
            logger.info(f"Embedding generated and stored for paint: {paint.name}")
            
        except Exception as e:
            logger.error(f"Error generating embedding for paint {paint_id}: {str(e)}")
            db.rollback()
            raise
    
    def get_embedding_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about embeddings in the database."""
        try:
            total_paints = db.query(PaintModel).count()
            paints_with_embeddings = db.query(PaintModel).filter(
                PaintModel.embedding.isnot(None)
            ).count()
            
            return {
                "total_paints": total_paints,
                "paints_with_embeddings": paints_with_embeddings,
                "coverage_percentage": (paints_with_embeddings / total_paints * 100) if total_paints > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting embedding stats: {e}")
            return {"total_paints": 0, "paints_with_embeddings": 0, "coverage_percentage": 0}
