# Frontend - Tintas AI Loomi

**Desafio Back IA - Processo Seletivo Loomi**

Frontend React para o sistema de catálogo de tintas com IA, desenvolvido como parte do desafio técnico da Loomi. Interface moderna e responsiva para interação com o sistema de recomendação inteligente.

## 🚀 Funcionalidades

### Autenticação
- Login com username e senha
- Logout seguro
- Verificação automática de autenticação
- Diferenciação de roles (admin, user, visitor)

### Chat Inteligente com IA
- **Chat em tempo real** com IA especializada em tintas
- **Geração de imagens** com DALL-E para simulações visuais
- **Histórico de conversas** - acesse conversas anteriores
- **Interface responsiva** - funciona em desktop e mobile

### Gerenciamento de Usuários (Admin)
- Listar usuários
- Criar novos usuários
- Editar usuários existentes
- Deletar usuários
- Busca e filtros
- Controle de roles e status

### Interface Principal
- Chat com IA
- Busca de tintas
- Histórico de conversas
- Gerenciamento de usuários (admin)
- Gerenciamento de tintas (admin)

## 🛠️ Tecnologias

- **React 18** - Biblioteca principal
- **Styled Components** - Estilização
- **Axios** - Requisições HTTP
- **Lucide React** - Ícones
- **React Router DOM** - Roteamento

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do frontend:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Proxy da API

O `package.json` já está configurado com proxy para a API:

```json
{
  "proxy": "http://localhost:8000"
}
```

## 🎯 Estrutura do Projeto

```
src/
├── components/          # Componentes React
│   ├── ChatInterface.js      # Interface principal do chat
│   ├── ChatHistory.js        # Histórico de conversas
│   ├── Header.js
│   ├── LoginModal.js
│   ├── LoadingSpinner.js
│   ├── PaintManagement.js
│   ├── PaintSearch.js
│   └── UserManagement.js
├── contexts/           # Contextos React
│   ├── AuthContext.js
│   └── SessionContext.js
├── config/            # Configurações
│   └── api.js
├── App.js             # Componente principal
├── index.js           # Ponto de entrada
└── index.css          # Estilos globais
```

## 🔐 Autenticação

### Login
- Username: `admin`
- Senha: `Admin@2024!`

### Roles
- **admin**: Acesso completo ao sistema
- **user**: Acesso limitado às funcionalidades básicas
- **visitor**: Acesso sem autenticação (modo convidado)

## 📡 API Integration

O frontend se comunica com a API através dos seguintes endpoints:

### Autenticação
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Dados do usuário atual

### Usuários (Admin)
- `GET /api/v1/users/` - Listar usuários
- `POST /api/v1/users/` - Criar usuário
- `GET /api/v1/users/{id}` - Buscar usuário
- `PUT /api/v1/users/{id}` - Atualizar usuário
- `DELETE /api/v1/users/{id}` - Deletar usuário

## 🎨 Interface

### Design System
- **Cores**: Gradientes azul/roxo
- **Tipografia**: Inter, system fonts
- **Componentes**: Styled Components
- **Ícones**: Lucide React
- **Responsivo**: Mobile-first

### Componentes Principais
- **Header**: Navegação e informações do usuário
- **LoginModal**: Modal de autenticação
- **UserManagement**: CRUD de usuários (admin)
- **LoadingSpinner**: Indicador de carregamento

## 🚀 Scripts Disponíveis

```bash
# Desenvolvimento
npm start

# Build para produção
npm run build

# Testes
npm test

# Eject (não recomendado)
npm run eject
```

## 🔧 Desenvolvimento

### Estrutura de Componentes
Cada componente segue o padrão:
- Importações
- Styled Components
- Lógica do componente
- Export default

### Contextos
- **AuthContext**: Gerencia autenticação e estado do usuário

### Configuração da API
- **api.js**: Centraliza endpoints e configurações

## 📱 Responsividade

O frontend é totalmente responsivo e funciona em:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (até 767px)

## 🔒 Segurança

- Tokens JWT armazenados no localStorage
- Headers de autorização automáticos
- Validação de roles no frontend
- Logout automático em caso de token inválido

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de CORS**: Verifique se a API está rodando na porta 8000
2. **Token inválido**: Faça logout e login novamente
3. **Erro 401**: Verifique as credenciais
4. **Erro 403**: Verifique se o usuário tem permissão de admin

### Logs
- Console do navegador para erros de JavaScript
- Network tab para requisições HTTP
- Application tab para verificar localStorage

## 📊 Atendimento aos Critérios de Avaliação

### **Interface e Experiência do Usuário**
- ✅ **Design Responsivo**: Interface adaptável para desktop, tablet e mobile
- ✅ **Autenticação Intuitiva**: Login simples e seguro
- ✅ **Chat Interativo**: Interface de chat moderna para interação com IA
- ✅ **Gerenciamento de Usuários**: Interface admin para CRUD de usuários
- ✅ **Visualização de Dados**: Exibição clara de informações e simulações

### **Integração com Backend**
- ✅ **API Integration**: Comunicação robusta com backend via Axios
- ✅ **Error Handling**: Tratamento de erros de forma elegante
- ✅ **Loading States**: Indicadores de carregamento para melhor UX
- ✅ **Context Management**: Gerenciamento de estado com React Context

### **Qualidade do Código**
- ✅ **Componentes Reutilizáveis**: Arquitetura modular e limpa
- ✅ **Styled Components**: Estilização consistente e manutenível
- ✅ **Clean Code**: Código limpo e bem organizado
- ✅ **Responsive Design**: Mobile-first approach

## 📄 Licença

Este projeto foi desenvolvido como parte do processo seletivo da Loomi para a vaga de Back IA.
