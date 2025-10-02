# AI Orchestrator - Paint Recommendations

**Desafio Back IA - Processo Seletivo Loomi**

Serviço de orquestração de IA para recomendações inteligentes de tintas Suvinil, implementando conceitos modernos de IA conforme especificação do desafio.

## 🚀 Funcionalidades Implementadas

- **Agente Orquestrador**: IA especializada em tintas com raciocínio explicável
- **RAG (Retrieval-Augmented Generation)**: Busca semântica de produtos com embeddings OpenAI
- **DALL-E Integration**: Geração real de imagens para simulação visual
- **Ferramentas Especializadas**: Paint Search Tool e Visual Generation Tool
- **Observabilidade**: Logs estruturados para monitoramento completo
- **Memória de Conversa**: Contexto mantido entre interações
- **Prompt Engineering**: Prompts otimizados para especialização em tintas

## 🏗️ Arquitetura

```
ai-orchestrator/
├── app/
│   ├── core/              # Configurações e infraestrutura
│   ├── agents/            # Agentes de IA e ferramentas
│   ├── services/          # Serviços de negócio
│   ├── models/            # Modelos de dados
│   ├── api/               # Endpoints da API
│   └── utils/             # Utilitários
├── tests/                 # Testes automatizados
├── scripts/               # Scripts utilitários
└── requirements.txt       # Dependências
```

## 🛠️ Stack Tecnológica

### **IA e Machine Learning**
- **LangChain 0.1.0**: Framework para agentes de IA
- **OpenAI GPT-4**: Modelo de linguagem para processamento
- **text-embedding-3-small**: Embeddings semânticos para RAG
- **DALL-E 3**: Geração de imagens para simulações visuais

### **Backend e Infraestrutura**
- **Python 3.11** + FastAPI
- **Pydantic 2.5.0**: Validação de dados
- **SQLAlchemy 2.0.23**: ORM para banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Docker** + Docker Compose

### **Observabilidade e Logging**
- **Structlog 23.2.0**: Logging estruturado
- **Python JSON Logger**: Formatação de logs
- **AILogger**: Logger customizado para IA

## 🚀 Como Executar

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <seu-repositorio>
cd ai-orchestrator

# Configure as variáveis de ambiente
cp env.example .env
# Edite o .env com sua chave da OpenAI
```

### 2. Execução com Docker Compose

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f ai-orchestrator

# Parar serviços
docker-compose down
```

### 3. Execução Manual (Desenvolvimento)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📊 Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Chat com IA
```bash
POST /api/v1/chat
{
  "message": "Quero pintar meu quarto de azul",
  "conversation_id": "user123"
}
```



## 🧪 Testes

```bash
# Testar health check
curl -X GET "http://localhost:8001/api/v1/health"

# Testar chat com IA
curl -X POST "http://localhost:8001/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quero pintar meu quarto de azul",
    "conversation_id": "test-123"
  }'
```

## 📈 Monitoramento

- **Logs**: Estruturados em JSON com contexto
- **Health Checks**: Verificação de dependências
- **Observabilidade**: Rastreamento de decisões do agente

## 🔧 Configuração

### Variáveis de Ambiente

- `OPENAI_API_KEY`: Chave da API OpenAI
- `DATABASE_URL`: URL do banco PostgreSQL
- `DEBUG`: Modo debug (true/false)
- `LOG_LEVEL`: Nível de log (INFO, DEBUG, ERROR)

## 📚 Documentação da API

Acesse `/docs` para documentação interativa da API (Swagger UI).

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📊 Atendimento aos Critérios de Avaliação

### **Implementação do Agente**
- ✅ **LangChain Framework**: Agente com ferramentas especializadas implementado
- ✅ **Raciocínio Explícito**: Processo de decisão transparente e auditável
- ✅ **Ferramentas Especializadas**: Paint Search Tool e Visual Generation Tool
- ✅ **Memória de Conversa**: Contexto mantido entre interações

### **Clareza do Raciocínio (Observabilidade)**
- ✅ **Logs Estruturados**: Cada decisão é logada com contexto completo
- ✅ **Métricas de Performance**: Tempo de processamento e confiança
- ✅ **Rastreamento de Ferramentas**: Quais ferramentas foram usadas e por quê
- ✅ **Debugging Facilitado**: Logs detalhados para troubleshooting

### **Robustez e Segurança do Prompt**
- ✅ **System Prompts Otimizados**: Prompts especializados para tintas Suvinil
- ✅ **Validação de Input**: Validação de entrada do usuário
- ✅ **Error Handling**: Tratamento robusto de erros da API OpenAI

### **Conceitos Modernos de IA Implementados**
- ✅ **LLMs**: GPT-4 para processamento de linguagem natural
- ✅ **LangChain**: Framework para facilitar implementação de agentes
- ✅ **Agentes com Ferramentas**: Seleção inteligente de ferramentas baseada em contexto
- ✅ **Prompt Engineering**: Prompts otimizados para especialização
- ✅ **Embedding + RAG**: Busca contextual com text-embedding-3-small
- ✅ **Geração Visual**: DALL-E 3 para simulações realistas

## 🤖 Uso de Ferramentas de IA no Desenvolvimento

### **Ferramentas Utilizadas**
- **Cursor**: Desenvolvimento principal com IA contextual
- **ChatGPT**: Brainstorming e arquitetura de agentes

### **Prompts Reais Implementados**

#### **1. System Prompt do Agente (Código Real)**
```
Você é um especialista em tintas Suvinil.

CONTEXTO DA CONVERSA:
- Esta é uma {context_type} contínua (ID: {context_id[:8]}..., histórico: {conversation_count} mensagens)
- Mantenha o contexto das mensagens anteriores
- Se o usuário perguntar sobre mensagens anteriores, consulte o histórico

FERRAMENTAS DISPONÍVEIS:
- paint_search(query, environment): Busca tintas específicas usando busca semântica
- visual_generation(description, color, environment, room_type): Cria simulações visuais

INSTRUÇÕES:
1. Use paint_search para buscar tintas específicas
2. Use os resultados das ferramentas para respostas precisas
3. Seja direto e baseie suas respostas nos dados encontrados
4. Lembre-se do contexto da conversa anterior
5. Se perguntado sobre mensagens anteriores, consulte o histórico
6. Use visual_generation para simulações visuais quando apropriado
7. Forneça TODOS os parâmetros nomeados exigidos pelo schema

IMPORTANTE: Sempre incorpore os resultados das ferramentas na sua resposta final e mantenha o contexto da conversa.
```

#### **2. Prompts DALL-E Implementados (Código Real)**
```
# Para ambientes externos:
"Modern building exterior painted {clean_color}, architectural photo"

# Para ambientes internos:
"Modern {room_term} with {clean_color} walls, interior design photo"
```

## 📄 Licença

Este projeto foi desenvolvido como parte do processo seletivo da Loomi para a vaga de Back IA.
