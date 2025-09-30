# Tintas AI Loomi - Sistema de Recomendação Inteligente de Tintas

Sistema backend para catálogo inteligente de tintas com IA, desenvolvido como parte do desafio técnico para vaga de Back AI da Loomi.

## Arquitetura e Decisões Técnicas

### Stack Tecnológica
- **Backend**: Python 3.11+ com FastAPI
- **Banco de Dados**: PostgreSQL 15 com SQLAlchemy ORM
- **Autenticação**: JWT com RBAC (Role-Based Access Control)
- **Containerização**: Docker e Docker Compose
- **Migrações**: Alembic
- **Documentação**: Swagger UI / ReDoc / OpenAPI 3.1

### Arquitetura de Software
Implementada seguindo os princípios da **Clean Architecture** com separação clara de responsabilidades:

```
api/
├── app/
│   ├── core/           # Configurações e infraestrutura base
│   ├── domain/         # Entidades, regras de negócio e interfaces
│   ├── application/    # Casos de uso e serviços de aplicação
│   ├── infrastructure/ # Implementações concretas (DB, middleware)
│   └── presentation/   # Controllers e rotas da API
```

### Decisões de Design

#### 1. Clean Architecture
**Decisão**: Adotar Clean Architecture para garantir baixo acoplamento e alta coesão.
**Justificativa**: Facilita manutenção, testes e evolução do sistema, separando claramente as responsabilidades entre camadas.

#### 2. Dependency Injection Container
**Decisão**: Implementar container de injeção de dependência customizado.
**Justificativa**: Permite inversão de controle e facilita testes unitários, mantendo o código desacoplado.

#### 3. Soft Delete
**Decisão**: Implementar soft delete para usuários ao invés de remoção física.
**Justificativa**: Preserva histórico de dados e permite auditoria, essencial para sistemas de produção.

#### 4. Validação Centralizada
**Decisão**: Centralizar validações de negócio em classes específicas no domínio.
**Justificativa**: Mantém as regras de negócio próximas às entidades e facilita reutilização.

#### 5. Logging Estruturado
**Decisão**: Implementar logging estruturado em JSON com rotação de arquivos.
**Justificativa**: Facilita monitoramento e análise de logs em ambientes de produção.

#### 6. Segurança Robusta
**Decisão**: Implementar PBKDF2-SHA256 com 290.000 rounds para hash de senhas.
**Justificativa**: Segue recomendações OWASP para segurança de senhas, garantindo proteção adequada.

## Funcionalidades Implementadas

### Sistema de Autenticação e Autorização
- Login com JWT
- Controle de acesso baseado em roles (USER/ADMIN)
- Middleware de autenticação automática
- Proteção de rotas sensíveis

### Gerenciamento de Usuários
- CRUD completo de usuários
- Paginação e filtros
- Validação de dados robusta
- Soft delete para preservação de dados

### Health Check e Monitoramento
- Endpoint de health check com verificação de banco
- Logs estruturados para todas as operações
- Middleware de logging de requisições
- Tratamento centralizado de exceções

### Documentação da API
- Swagger UI interativo
- ReDoc para documentação alternativa
- Schema OpenAPI 3.1 completo
- Exemplos de requisições e respostas

## Configuração e Execução

### Pré-requisitos
- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)

### Execução com Docker
```bash
cd api
docker compose up -d
```

### Acesso aos Serviços
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Usuário Admin Padrão
- **Email**: admin@tintas-ai-loomi.com
- **Username**: admin
- **Password**: Admin@2024!

## Estrutura do Banco de Dados

### Tabela Users
- `id`: Chave primária
- `email`: Email único (com índice para soft delete)
- `username`: Username único (com índice para soft delete)
- `full_name`: Nome completo
- `hashed_password`: Senha criptografada
- `role`: Role do usuário (USER/ADMIN)
- `status`: Status do usuário (ACTIVE/INACTIVE/SUSPENDED)
- `created_at`, `updated_at`, `deleted_at`: Timestamps
- `last_login`: Último login

## API Endpoints

### Autenticação
- `POST /api/v1/auth/login` - Login de usuário
- `GET /api/v1/auth/me` - Informações do usuário logado
- `POST /api/v1/auth/logout` - Logout (estateless)

### Usuários (Admin)
- `GET /api/v1/users/` - Listar usuários com paginação
- `POST /api/v1/users/` - Criar usuário
- `GET /api/v1/users/{id}` - Buscar usuário por ID
- `PUT /api/v1/users/{id}` - Atualizar usuário
- `DELETE /api/v1/users/{id}` - Soft delete de usuário

### Sistema
- `GET /` - Informações da API
- `GET /api/v1/health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc
- `GET /openapi.json` - Schema OpenAPI

## Qualidade de Código

### Padrões Seguidos
- **PEP 8**: Formatação de código Python
- **Type Hints**: Tipagem estática em todas as funções
- **Docstrings**: Documentação de funções e classes
- **Clean Code**: Código limpo e legível
- **SOLID**: Princípios de design orientado a objetos

### Testes e Validação
- Validação automática de dados com Pydantic
- Tratamento robusto de exceções
- Logs detalhados para debugging
- Health checks para monitoramento

## Próximos Passos

### Implementação da IA
1. **Integração com OpenAI/Anthropic**: Para processamento de linguagem natural
2. **Sistema de Embeddings**: Para busca semântica de produtos
3. **Agente Orquestrador**: Para interpretação de intenções do usuário
4. **RAG (Retrieval-Augmented Generation)**: Para busca contextual de tintas
5. **Base de Dados de Tintas**: Implementação do catálogo de produtos

### Melhorias Planejadas
1. **Testes Automatizados**: Cobertura completa com pytest
2. **Cache**: Redis para otimização de performance
3. **Rate Limiting**: Proteção contra abuso da API
4. **Métricas**: Prometheus/Grafana para monitoramento
5. **CI/CD**: Pipeline de integração e deploy contínuo

## Decisões de Desenvolvimento

### Uso de Ferramentas de IA
- **Cursor**: Edição contextual e geração de código
- **ChatGPT**: Revisão de arquitetura e brainstorming
- **Claude**: Análise de código e sugestões de melhoria

### Prompts Utilizados
- "Implementar sistema de autenticação JWT com FastAPI seguindo Clean Architecture"
- "Criar validações robustas para entidades de usuário com Pydantic"
- "Implementar logging estruturado para aplicação FastAPI"
- "Configurar Docker Compose para aplicação Python com PostgreSQL"

### Critérios de Decisão
- **Simplicidade**: Priorizar soluções simples e manuteníveis
- **Segurança**: Implementar práticas de segurança desde o início
- **Escalabilidade**: Arquitetura preparada para crescimento
- **Manutenibilidade**: Código limpo e bem documentado
- **Performance**: Otimizações sem comprometer legibilidade

## Conclusão

O sistema foi desenvolvido com foco em qualidade, segurança e manutenibilidade, seguindo as melhores práticas de engenharia de software. A arquitetura implementada fornece uma base sólida para a implementação das funcionalidades de IA que serão desenvolvidas na próxima fase do projeto.

A separação clara de responsabilidades e o uso de padrões estabelecidos facilitarão a integração com sistemas de IA e a evolução contínua da solução.