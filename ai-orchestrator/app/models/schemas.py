"""Pydantic schemas for AI Orchestrator."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Intent types for user queries."""
    SEARCH_PAINT = "search_paint"
    GET_RECOMMENDATION = "get_recommendation"
    PAINT_RECOMMENDATION = "paint_recommendation"
    VISUAL_SIMULATION = "visual_simulation"
    GENERAL_QUESTION = "general_question"


class EnvironmentType(str, Enum):
    """Environment types."""
    INTERNAL = "internal"
    EXTERNAL = "external"


class SurfaceType(str, Enum):
    """Surface types."""
    WALL = "wall"
    CEILING = "ceiling"
    FLOOR = "floor"
    WOOD = "wood"
    METAL = "metal"
    CONCRETE = "concrete"


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    request_id: Optional[str] = None


class IntentAnalysis(BaseModel):
    """Intent analysis result."""
    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    entities: List[str] = Field(default_factory=list)
    context_needed: List[str] = Field(default_factory=list)


class ToolExecution(BaseModel):
    """Tool execution result."""
    tool_name: str
    input_parameters: Optional[Union[Dict[str, Any], str]] = None
    raw_input: Optional[Any] = None
    output_result: Any = None
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class AgentResponse(BaseModel):
    """Unified response model for both agent and chat responses."""
    response: str
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    visual_url: Optional[str] = None
    reasoning_steps: List[ToolExecution] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float
    request_id: str
    response_id: str = Field(default_factory=lambda: f"resp_{datetime.utcnow().timestamp()}")
    intent: Optional["IntentType"] = None  # tip: pydantic vai coerir do str do seu código
    tools_used: List[str] = Field(default_factory=list)


class PaintRecommendation(BaseModel):
    """Paint recommendation model."""
    name: str
    color: str
    surface_type: SurfaceType
    environment: EnvironmentType
    finish_type: str
    features: List[str] = Field(default_factory=list)
    line: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime
    dependencies: Dict[str, str] = Field(default_factory=dict)


# Alias for backward compatibility
ChatResponse = AgentResponse


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
