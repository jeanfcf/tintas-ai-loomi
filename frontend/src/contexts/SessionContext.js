import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import apiClient from '../config/api';
import { useAuth } from './AuthContext';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResponse, setLastResponse] = useState(null);
  const hasInitialized = useRef(false);

  // Gerar session_id único para visitantes (não persistente)
  useEffect(() => {
    if (!isAuthenticated() && !sessionId) {
      // Para visitantes, sempre gerar nova sessão a cada carregamento da página
      const newSessionId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
    }
  }, [isAuthenticated, sessionId]);

  // Para visitantes, não carregar sessão persistente - sempre começar limpo
  useEffect(() => {
    if (!isAuthenticated() && sessionId && !hasInitialized.current) {
      hasInitialized.current = true;
      // Visitantes sempre começam com conversa vazia
      setMessages([]);
      setCurrentConversationId(null);
    }
  }, [isAuthenticated, sessionId]);

  // Para visitantes, não usar localStorage - apenas estado em memória
  // A conversa persiste apenas durante a sessão atual (até atualizar a página)

  const loadConversationMessages = useCallback(async (conversationId) => {
    if (!conversationId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(`/api/v1/chat/conversations/${conversationId}/messages`);
      const conversationMessages = response.data || [];
      
      const formattedMessages = conversationMessages.map(msg => ({
        id: msg.id,
        text: msg.message || msg.response,
        isUser: msg.is_user,
        hasImage: msg.has_image || false,
        imageUrl: msg.image_url || null,
        timestamp: msg.created_at,
        processing_time_ms: msg.processing_time_ms
      }));

      setMessages(formattedMessages);
      setCurrentConversationId(conversationId);
    } catch (err) {
      console.error('Error loading conversation messages:', err);
      setError('Erro ao carregar mensagens da conversa');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadUserLastConversation = useCallback(async () => {
    if (!isAuthenticated() || !user) return;

    setIsLoading(true);
    setError(null);

    try {
      // Limpar conversa atual
      setMessages([]);
      setCurrentConversationId(null);
      setLastResponse(null);

      // Buscar conversas do usuário
      const response = await apiClient.get('/api/v1/chat/conversations?limit=1');
      const conversations = response.data || [];
      
      if (conversations.length > 0) {
        // Carregar a última conversa (primeira da lista, pois está ordenada por data desc)
        const lastConversation = conversations[0];
        console.log('Carregando última conversa:', lastConversation.conversation_id);
        await loadConversationMessages(lastConversation.conversation_id);
      } else {
        console.log('Usuário não possui conversas anteriores');
        // Usuário não tem conversas, manter conversa limpa
      }
    } catch (err) {
      console.error('Error loading user last conversation:', err);
      setError('Erro ao carregar última conversa');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user, loadConversationMessages]);

  // Sincronizar com backend quando usuário fizer login
  useEffect(() => {
    if (isAuthenticated() && user && hasInitialized.current) {
      // Usuário fez login, limpar conversa atual e carregar última conversa do usuário
      console.log('Usuário logado, limpando conversa atual e carregando última conversa');
      loadUserLastConversation();
    }
  }, [isAuthenticated, user, loadUserLastConversation]);

  // Limpar tudo quando usuário fizer logout
  useEffect(() => {
    if (!isAuthenticated() && hasInitialized.current) {
      // Usuário fez logout, limpar tudo
      console.log('Usuário deslogado, limpando chat e conversas');
      setMessages([]);
      setCurrentConversationId(null);
      setLastResponse(null);
      setError(null);
      // Gerar nova session_id para visitante
      const newSessionId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
    }
  }, [isAuthenticated]);

  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || isLoading) {
      console.log('Message send blocked - empty message or already loading');
      return;
    }

    setError(null);
    const userMessage = {
      id: Date.now(),
      text: messageText,
      isUser: true,
      hasImage: false,
      imageUrl: null,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    console.log('Starting message send request...');

    try {
      // Para visitantes: usar session_id gerado pelo frontend
      // Para usuários logados: não enviar session_id
      const requestData = {
        message: messageText,
        user_id: isAuthenticated() ? user.id : null,
        conversation_id: currentConversationId,
        context_id: null,
        session_id: isAuthenticated() ? null : sessionId, // Só enviar se visitante
        context: {}
      };

      console.log('Sending request to API...', requestData);
      const response = await apiClient.post('/api/v1/chat/message', requestData);
      console.log('Received response from API:', response.data);

      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false,
        hasImage: response.data.has_image || false,
        imageUrl: response.data.image_url || null,
        timestamp: new Date().toISOString(),
        processing_time_ms: response.data.processing_time_ms
      };

      setMessages(prev => [...prev, aiMessage]);
      setLastResponse(aiMessage);
      
      // Atualizar conversation_id se retornado
      if (response.data.conversation_id) {
        setCurrentConversationId(response.data.conversation_id);
        // Carregar histórico da conversa se for uma nova conversa
        if (response.data.conversation_id !== currentConversationId) {
          loadConversationMessages(response.data.conversation_id);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.');
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        isUser: false,
        hasImage: false,
        imageUrl: null,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user, currentConversationId, sessionId, isLoading, loadConversationMessages]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setCurrentConversationId(null);
    setLastResponse(null);
    setError(null);
  }, []);

  const selectConversation = useCallback((conversationId) => {
    if (conversationId !== currentConversationId) {
      loadConversationMessages(conversationId);
    }
  }, [currentConversationId, loadConversationMessages]);

  const regenerateResponse = useCallback(async () => {
    if (!lastResponse || isLoading) return;
    
    setIsLoading(true);
    setError(null);
    try {
      // Reenviar a última mensagem do usuário
      const lastUserMessage = messages[messages.length - 2];
      if (lastUserMessage && lastUserMessage.isUser) {
        const response = await apiClient.post('/api/v1/chat/message', {
          message: lastUserMessage.text,
          user_id: isAuthenticated() ? user.id : null,
          conversation_id: currentConversationId,
          context_id: null,
          session_id: sessionId,
          context: {}
        });

        const aiMessage = {
          id: Date.now(),
          text: response.data.response,
          isUser: false,
          hasImage: response.data.has_image || false,
          imageUrl: response.data.image_url || null,
          timestamp: new Date().toISOString(),
          processing_time_ms: response.data.processing_time_ms
        };

        // Substituir a última resposta
        setMessages(prev => prev.slice(0, -1).concat(aiMessage));
        setLastResponse(aiMessage);
      }
    } catch (error) {
      console.error('Error regenerating response:', error);
      setError('Erro ao regenerar resposta. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  }, [lastResponse, isLoading, messages, isAuthenticated, user, currentConversationId, sessionId]);

  const value = {
    // Estado da conversa
    currentConversationId,
    messages,
    sessionId,
    isLoading,
    error,
    lastResponse,
    
    // Ações
    sendMessage,
    clearConversation,
    selectConversation,
    regenerateResponse,
    loadUserLastConversation,
    setError,
    
    // Estado da sessão
    hasActiveConversation: messages.length > 0,
    isGuestSession: !isAuthenticated(),
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};
