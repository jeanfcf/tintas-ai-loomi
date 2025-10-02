"""Paint search tool for the agent."""
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.logging import AILogger
from app.services.rag_service import RAGService

logger = AILogger(__name__)


class PaintSearchInput(BaseModel):
    """Input for paint search tool."""
    query: str = Field(..., description="What paint do you need? Describe the requirements")
    environment: str = Field(default="internal", description="Where will it be used? internal or external")


# Global RAG service instance
_rag_service = RAGService()

class PaintSearchTool(BaseTool):
    """Tool for searching paint recommendations using RAG."""
    
    name: str = "paint_search"
    description: str = "Search for paint recommendations based on user requirements using semantic search"
    args_schema = PaintSearchInput
    
    def __init__(self):
        super().__init__()
    
    @property
    def rag_service(self):
        return _rag_service
    
    def _run(self, query: str, environment: str = "internal") -> str:
        """Execute the tool."""
        try:
            logger.log_tool_execution(
                tool_name=self.name,
                input_params={"query": query, "environment": environment},
                output="Searching paints with RAG...",
                execution_time=0.0
            )
            
            # Use RAG to find similar paints (synchronous call)
            similar_paints = self.rag_service.search_with_retrieval_sync(
                query=query,
                limit=10,
                semantic_threshold=0.3,
                environment=environment
            )
            
            if not similar_paints:
                return "Nenhuma tinta encontrada com os critérios especificados."
            
            # Format response with top recommendations
            top_paints = similar_paints[:3]  # Top 3 most relevant
            
            response = f"Encontrei {len(similar_paints)} tinta(s) relevantes. Aqui estão as melhores opções:\n\n"
            
            for i, paint in enumerate(top_paints, 1):
                response += f"**{i}. {paint['name']}**\n"
                response += f"   • Cor: {paint['color']}\n"
                response += f"   • Ambiente: {paint['environment']}\n"
                response += f"   • Acabamento: {paint['finish_type']}\n"
                response += f"   • Linha: {paint['line']}\n"
                if paint.get('features'):
                    response += f"   • Características: {', '.join(paint['features'])}\n"
                if paint.get('description'):
                    response += f"   • Descrição: {paint['description']}\n"
                if 'similarity_score' in paint:
                    response += f"   • Relevância: {paint['similarity_score']:.1%}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"tool": self.name, "query": query, "environment": environment}
            )
            return f"Erro ao buscar tintas: {str(e)}"
    
    async def _arun(self, query: str, environment: str = "internal") -> str:
        """Async version of the tool."""
        return self._run(query, environment)