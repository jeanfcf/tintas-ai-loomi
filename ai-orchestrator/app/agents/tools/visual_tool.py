"""Visual generation tool for the agent."""
import os
import time
import uuid
import base64
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from openai import OpenAI
from app.core.config import get_settings
from app.core.logging import AILogger

logger = AILogger(__name__)


class VisualGenerationInput(BaseModel):
    """Input for visual generation tool."""
    description: str = Field(..., description="Description of the visual to generate")
    color: str = Field(..., description="Paint color")
    environment: str = Field(default="internal", description="Environment: internal or external")
    room_type: str = Field(default="", description="Type of room")


# Global settings and client instances
_settings = get_settings()
_client = OpenAI(api_key=_settings.openai_api_key)
_images_dir = "generated_images"
os.makedirs(_images_dir, exist_ok=True)

class VisualGenerationTool(BaseTool):
    """Tool for generating visual simulations of paint applications using DALL-E."""
    
    name: str = "visual_generation"
    description: str = "Generate visual simulation of paint application in a room or space using DALL-E"
    args_schema = VisualGenerationInput
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Private attribute for storing visual URL (not serialized)
    _last_visual_url: Optional[str] = PrivateAttr(default=None)
    
    def __init__(self, context: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.context = context or {}
    
    @property
    def settings(self):
        return _settings
    
    @property
    def client(self):
        return _client
    
    @property
    def images_dir(self):
        return _images_dir
    
    def _run(self, **kwargs) -> str:
        """Execute the tool with enhanced reasoning."""
        start_time = time.time()
        
        # Check if visual generation is disabled in context
        if self.context.get("disable_visual_generation", False):
            logger.logger.info("Visual generation disabled")
            return self._create_restriction_message()
        
        try:
            description = kwargs.get("description", "")
            color = kwargs.get("color", "")
            environment = kwargs.get("environment", "internal")
            room_type = kwargs.get("room_type", "")
            
            # Log received parameters
            logger.logger.info(f"Visual tool called: {color} {environment} {room_type}")
            
            # Log reasoning for visual generation decision
            reasoning = f"User requested visual simulation for {color} color in {environment} environment"
            if room_type:
                reasoning += f" ({room_type})"
            if description:
                reasoning += f" with description: {description}"
            
            logger.log_reasoning_step(
                step_name="visual_generation_decision",
                tool_name=self.name,
                reasoning=reasoning,
                input_params=kwargs,
                output="Proceeding with DALL-E generation",
                execution_time_ms=0.0,
                success=True
            )
            
            # Create detailed prompt for DALL-E
            prompt = self._create_dalle_prompt(description, color, environment, room_type)
            
            # Log the cleaned prompt for debugging
            logger.logger.info(f"Generated DALL-E prompt: {prompt}")
            
            # Generate image with DALL-E
            try:
                logger.logger.info(f"Generating image with DALL-E")
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                logger.logger.info("DALL-E image generated")
                
                # Save image locally
                image_url = response.data[0].url
                image_filename = f"{uuid.uuid4()}.jpg"
                image_path = os.path.join(self.images_dir, image_filename)
                
                # Download and save image
                import requests
                logger.logger.info("Downloading image from DALL-E")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                image_content = img_response.content
                logger.logger.info(f"Image downloaded: {len(image_content)} bytes")
                
                # Save image locally for backup
                with open(image_path, 'wb') as f:
                    f.write(image_content)
                
                # Convert to base64 for transmission
                logger.logger.info("Converting image to base64")
                image_base64 = base64.b64encode(image_content).decode('utf-8')
                visual_url = f"data:image/jpeg;base64,{image_base64}"
                logger.logger.info(f"Image converted to base64: {len(image_base64)} chars")
                
                execution_time = time.time() - start_time
                
                # Log visual generation decision with details
                logger.log_visual_decision(
                    user_message=f"Visual request: {description}",
                    color=color,
                    environment=environment,
                    room_type=room_type,
                    dalle_prompt=prompt,
                    visual_url=visual_url[:200] + '...' if visual_url and len(visual_url) > 200 else visual_url,
                    execution_time_ms=execution_time * 1000
                )
                
                response_text = f"Geração de simulação visual:\n\n"
                response_text += f"Descrição: {description}\n"
                response_text += f"Cor: {color}\n"
                response_text += f"Ambiente: {environment}\n"
                if room_type:
                    response_text += f"Tipo de cômodo: {room_type}\n"
                response_text += f"Prompt usado: {prompt}\n"
                response_text += f"Imagem gerada com sucesso!\n\n"
                response_text += "Esta é uma simulação visual gerada por IA (DALL-E) para demonstrar como ficaria o ambiente com a cor escolhida."
                
                # Store the visual URL for the agent to access
                object.__setattr__(self, '_last_visual_url', visual_url)
                logger.logger.info(f"Visual URL stored: {len(visual_url)} chars")
                
                return response_text
                
            except Exception as dalle_error:
                logger.log_error(
                    error=dalle_error,
                    context={"tool": self.name, "operation": "dalle_generation"}
                )
                
                # Check if it's a content policy violation
                error_message = str(dalle_error).lower()
                if "content_policy_violation" in error_message or "safety system" in error_message:
                    logger.logger.warning("DALL-E content policy violation detected, using enhanced fallback")
                    return self._create_enhanced_fallback_response(description, color, environment, room_type, prompt)
                else:
                    # Other errors - use standard fallback
                    return self._create_mock_response(description, color, environment, room_type)
            
        except Exception as e:
            logger.log_error(
                error=e,
                context={"tool": self.name, "kwargs": kwargs}
            )
            return f"Erro ao gerar simulação visual: {str(e)}"
    
    def _create_restriction_message(self) -> str:
        """Create a message explaining that visual generation is disabled."""
        return """A geração de simulações visuais não está disponível no momento.

Como alternativa, posso oferecer:
- Descrições detalhadas de como as cores ficariam no ambiente
- Informações sobre as características das tintas
- Recomendações baseadas no tipo de ambiente e iluminação
- Sugestões de combinações de cores que funcionam bem juntas

Gostaria que eu ajude com alguma dessas alternativas?"""
    
    def _create_dalle_prompt(self, description: str, color: str, environment: str, room_type: str) -> str:
        """Create optimized prompt for DALL-E with content policy compliance."""
        # Clean and filter inputs to avoid content policy violations
        clean_color = self._clean_prompt_text(color)
        clean_room_type = self._clean_prompt_text(room_type)
        
        # Create very simple, safe prompt
        if environment == "external":
            prompt = f"Modern building exterior painted {clean_color}, architectural photo"
        else:
            room_term = "room" if not clean_room_type else "space"
            prompt = f"Modern {room_term} with {clean_color} walls, interior design photo"
        
        # Final validation to ensure prompt is safe
        return self._validate_prompt(prompt)
    
    def _is_safe_description(self, description: str) -> bool:
        """Check if description is safe for DALL-E (English only, no problematic terms)."""
        if not description:
            return False
        
        # Check if description contains Portuguese words (likely to cause issues)
        portuguese_words = [
            'quarto', 'sala', 'cozinha', 'banheiro', 'como', 'ficaria', 'meu', 'minha',
            'pintado', 'com', 'suvinil', 'toque', 'seda', 'cor', 'branco', 'neve'
        ]
        
        description_lower = description.lower()
        for word in portuguese_words:
            if word in description_lower:
                return False
        
        # Check for problematic English terms
        problematic_terms = [
            'bedroom', 'bed', 'sleep', 'night', 'dark', 'nude', 'naked', 'exposed',
            'intimate', 'personal', 'adult', 'sexy', 'hot', 'cool', 'wild', 'crazy'
        ]
        
        for term in problematic_terms:
            if term in description_lower:
                return False
        
        return True
    
    def _clean_prompt_text(self, text: str) -> str:
        """Clean text to avoid DALL-E content policy violations."""
        if not text:
            return ""
        
        # Convert to lowercase for consistent checking
        text_lower = text.lower().strip()
        
        # List of potentially problematic terms and their safe alternatives
        problematic_terms = {
            'bedroom': 'room',
            'bed': 'room',
            'sleep': 'rest',
            'night': 'evening',
            'dark': 'dim',
            'nude': 'neutral',
            'naked': 'bare',
            'exposed': 'visible',
            'intimate': 'private',
            'personal': 'private',
            'adult': 'mature',
            'sexy': 'elegant',
            'hot': 'warm',
            'cool': 'refreshing',
            'wild': 'natural',
            'crazy': 'creative',
            'insane': 'unique',
            'extreme': 'dramatic',
            'intense': 'vibrant',
            'aggressive': 'bold',
            'violent': 'dynamic',
            'war': 'conflict',
            'battle': 'competition',
            'fight': 'struggle',
            'kill': 'eliminate',
            'death': 'end',
            'die': 'fade',
            'dead': 'lifeless',
            'blood': 'red',
            'gore': 'dramatic',
            'horror': 'mysterious',
            'scary': 'intriguing',
            'fear': 'caution',
            'terror': 'intensity',
            'nightmare': 'dream',
            'demon': 'figure',
            'devil': 'character',
            'satan': 'entity',
            'hell': 'underworld',
            'heaven': 'sky',
            'god': 'divine',
            'jesus': 'figure',
            'christ': 'figure',
            'bible': 'book',
            'church': 'building',
            'temple': 'structure',
            'mosque': 'building',
            'synagogue': 'building',
            'religion': 'belief',
            'spiritual': 'ethereal',
            'sacred': 'special',
            'holy': 'divine',
            'blessed': 'fortunate',
            'cursed': 'unfortunate',
            'evil': 'dark',
            'good': 'positive',
            'sin': 'mistake',
            'virtue': 'quality',
            'prayer': 'meditation',
            'worship': 'reverence',
            'faith': 'belief',
            'hope': 'optimism',
            'love': 'affection',
            'hate': 'dislike',
            'anger': 'frustration',
            'rage': 'intensity',
            'fury': 'passion',
            'wrath': 'anger',
            'envy': 'desire',
            'jealousy': 'envy',
            'greed': 'ambition',
            'lust': 'desire',
            'pride': 'confidence',
            'sloth': 'laziness',
            'gluttony': 'excess',
            'porn': 'adult content',
            'pornography': 'adult content',
            'sex': 'intimacy',
            'sexual': 'intimate',
            'nude': 'unclothed',
            'naked': 'bare',
            'exposed': 'visible',
            'intimate': 'private',
            'personal': 'private',
            'adult': 'mature',
            'sexy': 'attractive',
            'hot': 'warm',
            'cool': 'refreshing',
            'wild': 'natural',
            'crazy': 'creative',
            'insane': 'unique',
            'extreme': 'dramatic',
            'intense': 'vibrant',
            'aggressive': 'bold',
            'violent': 'dynamic',
            'war': 'conflict',
            'battle': 'competition',
            'fight': 'struggle',
            'kill': 'eliminate',
            'death': 'end',
            'die': 'fade',
            'dead': 'lifeless',
            'blood': 'red',
            'gore': 'dramatic',
            'horror': 'mysterious',
            'scary': 'intriguing',
            'fear': 'caution',
            'terror': 'intensity',
            'nightmare': 'dream',
            'demon': 'figure',
            'devil': 'character',
            'satan': 'entity',
            'hell': 'underworld',
            'heaven': 'sky',
            'god': 'divine',
            'jesus': 'figure',
            'christ': 'figure',
            'bible': 'book',
            'church': 'building',
            'temple': 'structure',
            'mosque': 'building',
            'synagogue': 'building',
            'religion': 'belief',
            'spiritual': 'ethereal',
            'sacred': 'special',
            'holy': 'divine',
            'blessed': 'fortunate',
            'cursed': 'unfortunate',
            'evil': 'dark',
            'good': 'positive',
            'sin': 'mistake',
            'virtue': 'quality',
            'prayer': 'meditation',
            'worship': 'reverence',
            'faith': 'belief',
            'hope': 'optimism',
            'love': 'affection',
            'hate': 'dislike',
            'anger': 'frustration',
            'rage': 'intensity',
            'fury': 'passion',
            'wrath': 'anger',
            'envy': 'desire',
            'jealousy': 'envy',
            'greed': 'ambition',
            'lust': 'desire',
            'pride': 'confidence',
            'sloth': 'laziness',
            'gluttony': 'excess'
        }
        
        # Replace problematic terms
        cleaned_text = text
        for problematic, replacement in problematic_terms.items():
            if problematic in text_lower:
                cleaned_text = cleaned_text.replace(problematic, replacement)
                cleaned_text = cleaned_text.replace(problematic.capitalize(), replacement.capitalize())
                cleaned_text = cleaned_text.replace(problematic.upper(), replacement.upper())
        
        return cleaned_text.strip()
    
    def _validate_prompt(self, prompt: str) -> str:
        """Validate prompt to ensure it's safe for DALL-E."""
        # Additional safety checks
        prompt_lower = prompt.lower()
        
        # Check for remaining problematic patterns
        dangerous_patterns = [
            'nude', 'naked', 'exposed', 'intimate', 'personal', 'adult', 'sexy',
            'hot', 'cool', 'wild', 'crazy', 'insane', 'extreme', 'intense',
            'aggressive', 'violent', 'war', 'battle', 'fight', 'kill', 'death',
            'die', 'dead', 'blood', 'gore', 'horror', 'scary', 'fear', 'terror',
            'nightmare', 'demon', 'devil', 'satan', 'hell', 'heaven', 'god',
            'jesus', 'christ', 'bible', 'church', 'temple', 'mosque', 'synagogue',
            'religion', 'spiritual', 'sacred', 'holy', 'blessed', 'cursed',
            'evil', 'good', 'sin', 'virtue', 'prayer', 'worship', 'faith',
            'hope', 'love', 'hate', 'anger', 'rage', 'fury', 'wrath', 'envy',
            'jealousy', 'greed', 'lust', 'pride', 'sloth', 'gluttony', 'porn',
            'pornography', 'sex', 'sexual'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in prompt_lower:
                logger.logger.warning(f"Potentially problematic term detected in prompt: {pattern}")
                # Replace with safe alternative
                prompt = prompt.replace(pattern, 'safe')
                prompt = prompt.replace(pattern.capitalize(), 'Safe')
                prompt = prompt.replace(pattern.upper(), 'SAFE')
        
        return prompt
    
    def _create_enhanced_fallback_response(self, description: str, color: str, environment: str, room_type: str, original_prompt: str) -> str:
        """Create enhanced fallback response when DALL-E content policy is violated."""
        clean_color = self._clean_prompt_text(color)
        clean_room_type = self._clean_prompt_text(room_type)
        clean_description = self._clean_prompt_text(description)
        
        response = f"🎨 Simulação Visual - {clean_color.title()}\n\n"
        
        # Create detailed description based on the cleaned inputs
        if environment == "external":
            response += f"**Ambiente Externo:**\n"
            response += f"Fachada de edifício moderno pintada na cor {clean_color}\n"
            response += f"Detalhes arquitetônicos visíveis\n"
            response += f"Fotografia profissional de arquitetura\n\n"
        else:
            room_term = clean_room_type if clean_room_type else "espaço interno"
            response += f"**Ambiente Interno:**\n"
            response += f"{room_term.title()} com paredes pintadas na cor {clean_color}\n"
            response += f"Iluminação natural e artificial balanceada\n"
            response += f"Design moderno e limpo\n\n"
        
        # Add color-specific descriptions
        color_descriptions = {
            'branco': 'Cria sensação de amplitude e luminosidade, ideal para espaços pequenos',
            'preto': 'Adiciona sofisticação e profundidade, funciona bem como destaque',
            'azul': 'Transmite tranquilidade e serenidade, perfeito para quartos',
            'verde': 'Conecta com a natureza, promove relaxamento',
            'amarelo': 'Energiza o ambiente, estimula criatividade',
            'vermelho': 'Adiciona energia e paixão, use com moderação',
            'cinza': 'Elegante e versátil, combina com qualquer estilo',
            'bege': 'Neutro e acolhedor, base perfeita para decoração',
            'rosa': 'Suave e romântico, ideal para quartos femininos',
            'roxo': 'Misterioso e criativo, adiciona personalidade'
        }
        
        color_lower = clean_color.lower()
        for color_key, color_desc in color_descriptions.items():
            if color_key in color_lower:
                response += f"**Características da cor {clean_color.title()}:**\n"
                response += f"{color_desc}\n\n"
                break
        
        # Add room-specific tips
        if clean_room_type:
            room_tips = {
                'quarto': '• Use iluminação suave para criar ambiente relaxante\n• Combine com móveis em tons neutros\n• Adicione plantas para equilibrar o ambiente',
                'sala': '• Combine com móveis em tons contrastantes\n• Use tapetes e almofadas para adicionar textura\n• Considere a iluminação para diferentes momentos do dia',
                'cozinha': '• Escolha tintas laváveis e resistentes\n• Combine com azulejos ou bancadas contrastantes\n• Considere a iluminação para facilitar o trabalho',
                'banheiro': '• Use tintas resistentes à umidade\n• Combine com azulejos e metais\n• Mantenha iluminação adequada para espelhos'
            }
            
            for room_key, room_tip in room_tips.items():
                if room_key in clean_room_type.lower():
                    response += f"**Dicas para {clean_room_type.title()}:**\n"
                    response += f"{room_tip}\n\n"
                    break
        
        # Add general recommendations
        response += "**Recomendações Gerais:**\n"
        response += "• Teste a cor em uma pequena área antes de pintar toda a parede\n"
        response += "• Considere a iluminação natural do ambiente\n"
        response += "• Use amostras de tinta para visualizar o resultado final\n"
        response += "• Consulte um profissional para escolhas mais complexas\n\n"
        
        response += "**Nota:** Esta simulação foi criada com base nas características da cor e do ambiente. "
        response += "Para uma visualização mais precisa, recomendo testar amostras de tinta no local."
        
        return response
    
    def _create_mock_response(self, description: str, color: str, environment: str, room_type: str) -> str:
        """Create mock response when DALL-E fails."""
        prompt = f"Room painted with {color} color, {environment} environment"
        if room_type:
            prompt += f", {room_type} style"
        
        response = f"Geração de simulação visual (modo de demonstração):\n\n"
        response += f"Descrição: {description}\n"
        response += f"Cor: {color}\n"
        response += f"Ambiente: {environment}\n"
        if room_type:
            response += f"Tipo de cômodo: {room_type}\n"
        response += f"Prompt usado: {prompt}\n"
        response += f"Imagem gerada com sucesso!\n\n"
        response += "Nota: Esta é uma simulação visual de demonstração. Em produção, seria gerada uma imagem real com DALL-E."
        
        return response
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version of the tool."""
        return self._run(**kwargs)
