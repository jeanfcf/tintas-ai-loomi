import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { MessageCircle, Clock, User, Trash2, Eye, Download, Calendar } from 'lucide-react';
import apiClient from '../config/api';
import { useAuth } from '../contexts/AuthContext';

const HistoryContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
`;

const Title = styled.h2`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ConversationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ConversationItem = styled.div`
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
  }

  ${props => props.$selected && `
    background: #dbeafe;
    border-color: #3b82f6;
  `}
`;

const ConversationHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const ConversationTitle = styled.h3`
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ConversationDate = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
  font-size: 0.85rem;
`;

const ConversationMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const ConversationPreview = styled.p`
  margin: 0;
  color: #4b5563;
  font-size: 0.9rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ConversationActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s ease;

  ${ConversationItem}:hover & {
    opacity: 1;
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
  }

  &.danger:hover {
    background: #fef2f2;
    border-color: #fecaca;
    color: #dc2626;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
`;

const EmptyIcon = styled.div`
  width: 64px;
  height: 64px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: #9ca3af;
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #6b7280;
`;

const ErrorState = styled.div`
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Pagination = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
`;

const PageButton = styled.button`
  padding: 0.5rem 1rem;
  background: ${props => props.$active ? '#3b82f6' : 'white'};
  color: ${props => props.$active ? 'white' : '#374151'};
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: ${props => props.$active ? '#2563eb' : '#f3f4f6'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const PageInfo = styled.span`
  color: #6b7280;
  font-size: 0.9rem;
`;

function ChatHistory({ onSelectConversation, selectedConversationId }) {
  const { isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const loadConversations = async (page = 1) => {
    if (!isAuthenticated()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get('/api/v1/chat/conversations', {
        params: {
          limit: 10,
          offset: (page - 1) * 10
        }
      });

      setConversations(response.data || []);
      setTotalPages(Math.ceil((response.data?.length || 0) / 10));
      setTotalCount(response.data?.length || 0);
      setCurrentPage(page);
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Erro ao carregar histórico de conversas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated()) {
      loadConversations();
    }
  }, [isAuthenticated]);

  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta conversa?')) return;

    try {
      await apiClient.delete(`/api/v1/chat/conversations/${conversationId}`);
      setConversations(prev => prev.filter(conv => conv.conversation_id !== conversationId));
    } catch (err) {
      console.error('Error deleting conversation:', err);
      setError('Erro ao excluir conversa');
    }
  };

  const handleExportConversation = async (conversationId) => {
    try {
      const response = await apiClient.get(`/api/v1/chat/conversations/${conversationId}/export`);
      
      // Criar e baixar arquivo
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `conversa_${conversationId}_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting conversation:', err);
      setError('Erro ao exportar conversa');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Hoje';
    if (diffDays === 2) return 'Ontem';
    if (diffDays <= 7) return `${diffDays - 1} dias atrás`;
    
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated()) {
    return (
      <HistoryContainer>
        <EmptyState>
          <EmptyIcon>
            <User size={24} />
          </EmptyIcon>
          <h3>Faça login para ver seu histórico</h3>
          <p>Entre com sua conta para acessar suas conversas salvas</p>
        </EmptyState>
      </HistoryContainer>
    );
  }

  return (
    <HistoryContainer>
      <Header>
        <Title>
          <MessageCircle size={20} />
          Histórico de Conversas
        </Title>
        <RefreshButton onClick={() => loadConversations(currentPage)} disabled={loading}>
          {loading ? 'Carregando...' : 'Atualizar'}
        </RefreshButton>
      </Header>

      {error && (
        <ErrorState>
          <span>⚠️</span>
          {error}
        </ErrorState>
      )}

      {loading ? (
        <LoadingState>
          <div>Carregando conversas...</div>
        </LoadingState>
      ) : conversations.length === 0 ? (
        <EmptyState>
          <EmptyIcon>
            <MessageCircle size={24} />
          </EmptyIcon>
          <h3>Nenhuma conversa encontrada</h3>
          <p>Suas conversas aparecerão aqui quando você começar a usar o chat</p>
        </EmptyState>
      ) : (
        <>
          <ConversationsList>
            {conversations.map(conversation => (
              <ConversationItem
                key={conversation.conversation_id}
                $selected={selectedConversationId === conversation.conversation_id}
                onClick={() => onSelectConversation(conversation.conversation_id)}
              >
                <ConversationHeader>
                  <ConversationTitle>
                    <MessageCircle size={16} />
                    {conversation.title || 'Conversa sem título'}
                  </ConversationTitle>
                  <ConversationDate>
                    <Calendar size={14} />
                    {formatDate(conversation.created_at)}
                  </ConversationDate>
                </ConversationHeader>

                <ConversationMeta>
                  <MetaItem>
                    <Clock size={14} />
                    {formatTime(conversation.created_at)}
                  </MetaItem>
                  <MetaItem>
                    <MessageCircle size={14} />
                    {conversation.message_count || 0} mensagens
                  </MetaItem>
                  {conversation.has_images && (
                    <MetaItem>
                      <Download size={14} />
                      Com imagens
                    </MetaItem>
                  )}
                </ConversationMeta>

                <ConversationPreview>
                  {conversation.last_message || 'Nenhuma mensagem disponível'}
                </ConversationPreview>

                <ConversationActions>
                  <ActionButton onClick={(e) => {
                    e.stopPropagation();
                    onSelectConversation(conversation.conversation_id);
                  }}>
                    <Eye size={14} />
                    Ver
                  </ActionButton>
                  <ActionButton onClick={(e) => {
                    e.stopPropagation();
                    handleExportConversation(conversation.conversation_id);
                  }}>
                    <Download size={14} />
                    Exportar
                  </ActionButton>
                  <ActionButton 
                    className="danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conversation.conversation_id);
                    }}
                  >
                    <Trash2 size={14} />
                    Excluir
                  </ActionButton>
                </ConversationActions>
              </ConversationItem>
            ))}
          </ConversationsList>

          {totalPages > 1 && (
            <Pagination>
              <PageButton
                onClick={() => loadConversations(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Anterior
              </PageButton>
              
              <PageInfo>
                Página {currentPage} de {totalPages} ({totalCount} conversas)
              </PageInfo>
              
              <PageButton
                onClick={() => loadConversations(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Próxima
              </PageButton>
            </Pagination>
          )}
        </>
      )}
    </HistoryContainer>
  );
}

export default ChatHistory;
