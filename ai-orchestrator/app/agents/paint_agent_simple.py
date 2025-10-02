import time
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool

from app.core.config import get_settings
from app.core.logging import AILogger
from app.services.context_service import ContextService
from app.agents.tools.search_tool import PaintSearchTool
from app.agents.tools.visual_tool import VisualGenerationTool
from app.models.schemas import AgentResponse, ToolExecution  # IntentAnalysis não é usado aqui

logger = AILogger(__name__)


class PaintAgentSimple:
    """Simplified AI agent."""

    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.3,           
            api_key=self.settings.openai_api_key,
            max_tokens=1000,           
            timeout=60,
            request_timeout=60,
        )

        self.memory = ConversationBufferWindowMemory(
            k=10,  # mantém as últimas 10 mensagens literalmente
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output",
        )

        self.context_service = ContextService()
        self.tools = self._initialize_tools()  # Initialize with default tools
        self.agent = None  # Will be created dynamically based on context

    def _initialize_tools(self, context: Dict[str, Any] = None) -> List[BaseTool]:
        """Initialize available tools based on context."""
        tools = [PaintSearchTool()]
        
        # Only add visual generation tool if not disabled in context
        if not context or not context.get("disable_visual_generation", False):
            tools.append(VisualGenerationTool(context))
        
        return tools

    def _create_agent(self, tools: List[BaseTool], context: Dict[str, Any] = None) -> AgentExecutor:
        """Create the simplified agent with context-aware tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_simple_prompt(context)),
            MessagesPlaceholder(variable_name="chat_history"),   # ✅ histórico entra no prompt
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt,
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=False,
            handle_parsing_errors=True,
            return_intermediate_steps=True, 
            max_iterations=5,
            max_execution_time=60,  
        )

    def _get_simple_prompt(self, context: Dict[str, Any] = None) -> str:
        """Generate prompt for the agent."""
        visual_disabled = context and context.get("disable_visual_generation", False)
        conversation_count = len(context.get("conversation_history", [])) if context else 0
        
        context_type = "conversa" if context and context.get("conversation_id") else "sessão"
        context_id = context.get("conversation_id") or context.get("session_id", "não fornecido")
        
        prompt_parts = [
            "Você é um especialista em tintas Suvinil.",
            "",
            "CONTEXTO DA CONVERSA:",
            f"- Esta é uma {context_type} contínua (ID: {context_id[:8]}..., histórico: {conversation_count} mensagens)",
            "- Mantenha o contexto das mensagens anteriores",
            "- Se o usuário perguntar sobre mensagens anteriores, consulte o histórico",
            "",
            "FERRAMENTAS DISPONÍVEIS:",
            "- paint_search(query, environment): Busca tintas específicas usando busca semântica"
        ]
        
        if not visual_disabled:
            prompt_parts.append("- visual_generation(description, color, environment, room_type): Cria simulações visuais")
        
        prompt_parts.extend([
            "",
            "INSTRUÇÕES:",
            "1. Use paint_search para buscar tintas específicas",
            "2. Use os resultados das ferramentas para respostas precisas",
            "3. Seja direto e baseie suas respostas nos dados encontrados",
            "4. Lembre-se do contexto da conversa anterior",
            "5. Se perguntado sobre mensagens anteriores, consulte o histórico"
        ])
        
        if not visual_disabled:
            prompt_parts.append("6. Use visual_generation para simulações visuais quando apropriado")
        
        prompt_parts.extend([
            "7. Forneça TODOS os parâmetros nomeados exigidos pelo schema",
            "",
            "EXEMPLO:",
            'Usuário: "Quero tinta branca para quarto"',
            '1. Execute: paint_search(query="tinta branca quarto", environment="internal")',
            "2. Use os resultados para recomendar tintas específicas",
            "3. Responda com base nos dados encontrados"
        ])
        
        if visual_disabled:
            prompt_parts.extend([
                "",
                "RESTRIÇÃO: A geração de simulações visuais está desabilitada.",
                "Explique que esta funcionalidade não está disponível e ofereça alternativas."
            ])
        
        prompt_parts.append("\nIMPORTANTE: Sempre incorpore os resultados das ferramentas na sua resposta final e mantenha o contexto da conversa.")
        
        return "\n".join(prompt_parts)

    async def _load_conversation_history(self, context: Dict[str, Any]) -> None:
        """Load conversation history into LangChain memory."""
        try:
            conversation_history = context.get("conversation_history", [])
            logger.logger.info(f"Loading conversation history: {len(conversation_history)} messages")
            logger.logger.info(f"Conversation history: {conversation_history}") 
            if not conversation_history:
                logger.logger.info("No conversation history to load")
                return

            # Clear existing memory
            self.memory.clear()

            # Load recent conversation history into memory
            loaded_count = 0
            for entry in conversation_history[-10:]:  # Load last 10 exchanges
                user_message = entry.get("message", "")
                ai_response = entry.get("response", "")

                if user_message and ai_response:
                    # Add to memory
                    self.memory.save_context(
                        {"input": user_message},
                        {"output": ai_response}
                    )
                    loaded_count += 1

            logger.logger.info(f"Loaded {loaded_count} messages into memory from {len(conversation_history)} total")

        except Exception as e:
            logger.logger.error(f"Error loading conversation history: {e}")

    async def process_query(
        self,
        message: str,
        context: Dict[str, Any],
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AgentResponse:
        """Process query with proper tool tracking."""
        start_time = time.time()

        try:
            # Validação: exatamente um ID deve ser fornecido
            if conversation_id and session_id:
                raise ValueError("Não é possível fornecer conversation_id e session_id simultaneamente")
            if not conversation_id and not session_id:
                raise ValueError("conversation_id ou session_id deve ser fornecido")
            
            logger.logger.info(f"Processing query - conversation_id: {conversation_id}, session_id: {session_id}")
            
            # Get or create context based on ID type
            if conversation_id:
                # Usuário logado: usar conversation_id
                full_context = await self.context_service.get_or_create_context(
                    conversation_id=conversation_id
                )
            else:
                # Visitante: usar session_id
                full_context = await self.context_service.get_or_create_context(
                    session_id=session_id
                )

            disable_visual_generation = context.get("disable_visual_generation", False)
            full_context["disable_visual_generation"] = disable_visual_generation
            
            # Load conversation history into memory
            await self._load_conversation_history(full_context)
            
            # Initialize tools and agent based on context
            tools = self._initialize_tools(full_context)
            agent = self._create_agent(tools, full_context)
            
            # Log context information
            visual_disabled = full_context.get("disable_visual_generation", False)
            history_count = len(full_context.get("conversation_history", []))
            logger.logger.info(
                f"Agent initialized with {len(tools)} tools, visual_disabled: {visual_disabled}, "
                f"conversation_history: {history_count} messages"
            )
            
            # Execute agent
            logger.logger.info(f"Processing message: '{message[:50]}...'")
            try:
                result = await agent.ainvoke({"input": message})
                logger.logger.info("Agent execution completed")
            except Exception as agent_error:
                logger.logger.error(f"Agent execution failed: {agent_error}")
                raise agent_error

            # Debug result format
            logger.logger.debug(f"Result type: {type(result)}")

            # Extração segura
            if isinstance(result, dict):
                response_text = result.get("output", "") or ""
                intermediate_steps = result.get("intermediate_steps", []) or []
            else:
                response_text = str(result)
                intermediate_steps = []

            tools_used: List[str] = []
            reasoning_steps: List[ToolExecution] = []
            visual_url: Optional[str] = None

            for step in intermediate_steps:
                if not (isinstance(step, (list, tuple)) and len(step) >= 2):
                    continue

                action, observation = step[0], step[1]

                tool_name = None
                raw_params = None

                if hasattr(action, "tool"):
                    tool_name = getattr(action, "tool", None)
                    raw_params = getattr(action, "tool_input", None)
                elif isinstance(action, dict):
                    tool_name = action.get("tool")
                    raw_params = action.get("tool_input")

                if not tool_name:
                    continue

                tools_used.append(tool_name)

                reasoning_steps.append(
                    ToolExecution(
                        tool_name=tool_name,
                        input_parameters=raw_params,
                        raw_input=raw_params,   # se o schema tiver este campo
                        output_result=str(observation),
                        execution_time_ms=0.0,
                        success=True,
                    )
                )

                if tool_name == "visual_generation":
                    # Extract visual URL from tool execution result
                    try:
                        # Find the visual generation tool in our tools list
                        for tool in tools:
                            if hasattr(tool, 'name') and tool.name == 'visual_generation':
                                try:
                                    # Check if tool has stored visual URL
                                    if hasattr(tool, '_last_visual_url'):
                                        stored_url = getattr(tool, '_last_visual_url', None)
                                        if stored_url and isinstance(stored_url, str):
                                            visual_url = stored_url
                                            logger.logger.info(f"Visual URL captured: {len(visual_url)} chars")
                                        break
                                except Exception as e:
                                    logger.logger.error(f"Error accessing visual URL: {e}")
                                break
                    except Exception as e:
                        logger.logger.error(f"Error capturing visual URL: {e}")

            response_text = self._clean_response(response_text)

            intent = "general_question"
            if "paint_search" in tools_used:
                intent = "search_paint"
            elif "visual_generation" in tools_used:
                intent = "visual_simulation"

            confidence = 0.9 if tools_used else (0.6 if len(response_text) < 50 else 0.8)

            processing_time_ms = (time.time() - start_time) * 1000

            # Update context with new conversation data
            try:
                updated_context = await self.context_service.update_context(
                    context=full_context,
                    message=message,
                    response=response_text,
                    intent=intent,
                    tools_used=tools_used,
                    metadata={
                        "processing_time_ms": processing_time_ms,
                        "confidence": confidence,
                        "has_visual": visual_url is not None
                    }
                )
                logger.logger.info("Context updated with new conversation data")
            except Exception as e:
                logger.logger.error(f"Error updating context: {e}")

            # Log response
            logger.logger.info(
                f"Response ready: {len(response_text)} chars, tools: {len(tools_used)}, has_visual: {visual_url is not None}"
            )

            return AgentResponse(
                response=response_text,
                recommendations=[],
                visual_url=visual_url if isinstance(visual_url, str) else None,
                reasoning_steps=reasoning_steps,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                request_id=f"simple_{int(time.time())}",
                response_id=f"simple_resp_{int(time.time())}",
                intent=intent,           # Enum será coerido a partir do str
                tools_used=tools_used,
            )

        except Exception as e:
            logger.logger.error(f"Error in simple agent: {e}")
            logger.logger.error(f"Error type: {type(e).__name__}")
            logger.logger.error(f"Error details: {str(e)}")

            processing_time_ms = (time.time() - start_time) * 1000
            return AgentResponse(
                response="Desculpe, estou com dificuldades técnicas. Por favor, tente novamente mais tarde.",
                recommendations=[],
                visual_url=None,
                reasoning_steps=[],
                confidence=0.3,
                processing_time_ms=processing_time_ms,
                request_id=f"error_{int(time.time())}",
                response_id=f"error_resp_{int(time.time())}",
                intent="general_question",
                tools_used=[],
            )

    def _clean_response(self, text: str) -> str:
        """Clean response text."""
        if not text:
            return text

        import re
        debug_patterns = [
            r'\[Executando.*?\]',
            r'Executando.*?',
            r'Tool execution.*?',
            r'Using tool.*?',
        ]

        cleaned_text = text
        for pattern in debug_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)

        # Remove any base64 data URLs that might have leaked into the response
        base64_patterns = [
            r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+',
            r'URL da imagem:\s*data:image/[^;]+;base64,[A-Za-z0-9+/=]+',
        ]
        
        for pattern in base64_patterns:
            cleaned_text = re.sub(pattern, 'URL da imagem: [Imagem gerada com sucesso]', cleaned_text)
        
        # Remove fake URLs and placeholder links
        fake_url_patterns = [
            r'https://example\.com/[^\s\)]+',
            r'\(https://example\.com/[^\)]+\)',
            r'\[clicando aqui\]\s*\([^\)]+\)',
            r'visual/[^\s\)]+\.jpg',
        ]
        
        for pattern in fake_url_patterns:
            cleaned_text = re.sub(pattern, '[Imagem gerada com sucesso]', cleaned_text)

        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        return cleaned_text.strip()
