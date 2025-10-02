"""Logging configuration."""
import logging
import sys
from typing import Any, Dict
import structlog
from app.core.config import get_settings


def setup_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure file handler
    try:
        file_handler = logging.FileHandler("logs/ai_orchestrator.log", mode='a', encoding='utf-8')
        file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
        file_handler = None
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)
    
    # Configure standard logging
    handlers = [console_handler]
    if file_handler:
        handlers.append(file_handler)
    
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
        handlers=handlers
    )
    
    # Test logging
    test_logger = logging.getLogger("ai_orchestrator_startup")
    test_logger.info("Logging initialized - logs saved to logs/ai_orchestrator.log")


def get_logger(name: str) -> structlog.BoundLogger:
    """Get structured logger."""
    return structlog.get_logger(name)


class AILogger:
    """AI-specific logger with context."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_agent_decision(
        self, 
        user_message: str, 
        intent: str, 
        tools_used: list, 
        response: str,
        processing_time: float,
        reasoning_steps: int = 0,
        confidence: float = 0.0,
        **kwargs
    ) -> None:
        """Log agent decision with context."""
        self.logger.info(
            "Agent processed request",
            intent=intent,
            tools_count=len(tools_used),
            response_length=len(response),
            processing_time_ms=round(processing_time * 1000, 2),
            confidence=round(confidence, 2),
            **kwargs
        )
    
    def log_tool_execution(
        self, 
        tool_name: str, 
        input_params: Dict[str, Any], 
        output: Any,
        execution_time: float,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log tool execution."""
        self.logger.info(
            f"Tool {tool_name} executed",
            success=success,
            execution_time_ms=round(execution_time * 1000, 2),
            **kwargs
        )
    
    def log_reasoning_step(
        self,
        step_name: str,
        tool_name: str,
        reasoning: str,
        input_params: Dict[str, Any],
        output: Any,
        execution_time_ms: float,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log reasoning step."""
        self.logger.debug(
            f"Step {step_name} completed",
            tool=tool_name,
            success=success,
            **kwargs
        )
    
    def log_visual_decision(
        self,
        user_message: str,
        color: str,
        environment: str,
        room_type: str,
        dalle_prompt: str,
        visual_url: str,
        execution_time_ms: float,
        **kwargs
    ) -> None:
        """Log visual generation."""
        self.logger.info(
            "Visual generated",
            color=color,
            environment=environment,
            execution_time_ms=round(execution_time_ms, 2),
            **kwargs
        )
    
    def log_error(
        self, 
        error: Exception, 
        context: Dict[str, Any],
        **kwargs
    ) -> None:
        """Log error."""
        self.logger.error(
            f"Error: {type(error).__name__}",
            message=str(error),
            **kwargs
        )
