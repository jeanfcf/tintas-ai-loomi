"""Security utilities for AI Orchestrator."""
import re
from typing import Dict, Any
from pydantic import BaseModel, ValidationError


class ValidationResult(BaseModel):
    """Validation result model."""
    is_valid: bool
    reason: str = ""
    sanitized_input: str = ""


class PromptSecurity:
    """Prompt security and validation."""
    
    def __init__(self):
        self.injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"system\s*:",
            r"assistant\s*:",
            r"<\|.*?\|>",
            r"\[INST\].*?\[/INST\]",
            r"###\s*SYSTEM\s*###",
            r"###\s*INSTRUCTIONS\s*###"
        ]
        self.max_length = 4000
        self.dangerous_tags = ['script', 'iframe', 'object', 'embed']
    
    async def validate_prompt(self, prompt: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate prompt for security issues."""
        if not prompt or not isinstance(prompt, str):
            return ValidationResult(
                is_valid=False,
                reason="Empty or invalid prompt"
            )
        
        # Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    reason=f"Potential prompt injection detected: {pattern}"
                )
        
        # Check length
        if len(prompt) > self.max_length:
            return ValidationResult(
                is_valid=False,
                reason=f"Prompt too long: {len(prompt)} > {self.max_length}"
            )
        
        # Sanitize input
        sanitized = self._sanitize_prompt(prompt)
        
        return ValidationResult(
            is_valid=True,
            sanitized_input=sanitized
        )
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt input."""
        # Remove dangerous HTML tags
        for tag in self.dangerous_tags:
            pattern = rf"<{tag}[^>]*>.*?</{tag}>"
            prompt = re.sub(pattern, "", prompt, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive newlines
        prompt = re.sub(r'\n{3,}', '\n\n', prompt)
        
        # Remove leading/trailing whitespace
        prompt = prompt.strip()
        
        return prompt
    
    async def validate_context(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate context data."""
        if not isinstance(context, dict):
            return ValidationResult(
                is_valid=False,
                reason="Context must be a dictionary"
            )
        
        # Check for suspicious context keys
        suspicious_keys = ['system', 'instructions', 'prompt', 'template']
        for key in context.keys():
            if any(sus in key.lower() for sus in suspicious_keys):
                return ValidationResult(
                    is_valid=False,
                    reason=f"Suspicious context key: {key}"
                )
        
        return ValidationResult(is_valid=True)
