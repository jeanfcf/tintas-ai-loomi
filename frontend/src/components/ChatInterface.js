import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Send, Bot, User, Sparkles, Image as ImageIcon, Clock, RefreshCw, Download, Trash2, Plus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useSession } from '../contexts/SessionContext';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f9fafb;
`;

const Message = styled.div`
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: flex-start;
`;

const MessageAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.$isUser ? '#3b82f6' : '#10b981'};
  color: white;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  flex: 1;
  background: ${props => props.$isUser ? '#3b82f6' : 'white'};
  color: ${props => props.$isUser ? 'white' : '#374151'};
  padding: 0.75rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  max-width: 80%;
`;

const MessageText = styled.p`
  margin: 0;
  line-height: 1.5;
  white-space: pre-wrap;
`;

const MessageImage = styled.img`
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.02);
  }
`;

const ImagePlaceholder = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f3f4f6;
  border-radius: 8px;
  margin-top: 0.5rem;
  color: #6b7280;
  font-size: 0.9rem;
`;


const MetricsPanel = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 0.8rem;
  flex-wrap: wrap;
`;

const Metric = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #475569;
`;


const SessionInfo = styled.div`
  background: #fef3c7;
  color: #92400e;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SessionId = styled.code`
  background: rgba(146, 64, 14, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.75rem;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #475569;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #e2e8f0;
    color: #1e293b;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ClearButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #fecaca;
    color: #b91c1c;
  }
`;

const NewConversationButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 7rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }
`;

const AuthNotice = styled.div`
  background: #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border: 1px solid #fbbf24;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border-top: 1px solid #e5e7eb;
`;

const Input = styled.input`
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const SendButton = styled.button`
  padding: 0.75rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: background-color 0.2s ease;

  &:hover:not(:disabled) {
    background: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const LoadingMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-style: italic;
`;

const TypingIndicator = styled.div`
  display: flex;
  gap: 0.25rem;
  margin-left: 0.5rem;

  div {
    width: 4px;
    height: 4px;
    background: #6b7280;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }

  @keyframes typing {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border: 1px solid #fecaca;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

function ChatInterface() {
  const { isAuthenticated } = useAuth();
  const { 
    messages, 
    isLoading, 
    error, 
    lastResponse, 
    sessionId, 
    sendMessage, 
    clearConversation, 
    regenerateResponse 
  } = useSession();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const messageText = inputValue;
    setInputValue('');
    await sendMessage(messageText);
  };

  const handleClearChat = () => {
    clearConversation();
  };

  const handleNewConversation = () => {
    clearConversation();
  };

  const handleDownloadImage = (imageUrl) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `simulacao_visual_${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleRegenerateResponse = async () => {
    await regenerateResponse();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };


  return (
    <ChatContainer>
      {isAuthenticated() && (
        <NewConversationButton onClick={handleNewConversation} title="Nova conversa">
          <Plus size={14} />
          Nova Conversa
        </NewConversationButton>
      )}
      
      <ClearButton onClick={handleClearChat} title="Limpar conversa">
        <Trash2 size={14} />
        Limpar
      </ClearButton>

      <MessagesContainer>
        {!isAuthenticated() && sessionId && (
          <SessionInfo>
            <Sparkles size={16} />
            Sessão visitante: <SessionId>{sessionId}</SessionId>
          </SessionInfo>
        )}

        {!isAuthenticated() && (
          <AuthNotice>
            <Sparkles size={16} />
            Você está usando o modo visitante. Faça login para gerar imagens e acessar recursos completos.
          </AuthNotice>
        )}

        {error && (
          <ErrorMessage>
            <span>⚠️</span>
            {error}
          </ErrorMessage>
        )}
        
        {messages.map(message => (
          <Message key={message.id}>
            <MessageAvatar $isUser={message.isUser}>
              {message.isUser ? <User size={16} /> : <Bot size={16} />}
            </MessageAvatar>
            <MessageContent $isUser={message.isUser}>
              <MessageText>{message.text}</MessageText>
              
              {message.hasImage && message.imageUrl && (
                <div>
                  <MessageImage 
                    src={message.imageUrl} 
                    alt="Simulação visual gerada pela IA"
                    onClick={() => window.open(message.imageUrl, '_blank')}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                  <ActionButtons>
                    <ActionButton onClick={() => handleDownloadImage(message.imageUrl)}>
                      <Download size={14} />
                      Baixar
                    </ActionButton>
                  </ActionButtons>
                </div>
              )}
              
              {message.hasImage && !message.imageUrl && (
                <ImagePlaceholder>
                  <ImageIcon size={16} />
                  Imagem sendo gerada...
                </ImagePlaceholder>
              )}

              {/* Dados básicos */}
              {!message.isUser && !message.isError && (
                <div>
                  {message.processing_time_ms && (
                    <MetricsPanel>
                      <Metric>
                        <Clock size={14} />
                        {message.processing_time_ms}ms
                      </Metric>
                    </MetricsPanel>
                  )}

                  <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.5rem' }}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              )}
            </MessageContent>
          </Message>
        ))}
        
        {isLoading && (
          <Message>
            <MessageAvatar $isUser={false}>
              <Bot size={16} />
            </MessageAvatar>
            <MessageContent $isUser={false}>
              <LoadingMessage>
                <Sparkles size={16} />
                IA está pensando
                <TypingIndicator>
                  <div></div>
                  <div></div>
                  <div></div>
                </TypingIndicator>
              </LoadingMessage>
            </MessageContent>
          </Message>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Digite sua mensagem..."
          disabled={isLoading}
        />
        <SendButton onClick={handleSendMessage} disabled={isLoading || !inputValue.trim()}>
          <Send size={16} />
          {isLoading ? 'Enviando...' : 'Enviar'}
        </SendButton>
      </InputContainer>

      {lastResponse && !isLoading && (
        <ActionButtons style={{ padding: '0.5rem 1rem', background: '#f8fafc', borderTop: '1px solid #e5e7eb' }}>
          <ActionButton onClick={handleRegenerateResponse}>
            <RefreshCw size={14} />
            Regenerar Resposta
          </ActionButton>
        </ActionButtons>
      )}
    </ChatContainer>
  );
}

export default ChatInterface;