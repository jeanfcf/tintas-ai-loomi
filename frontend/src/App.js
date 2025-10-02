import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { MessageCircle, Search, Sparkles, Users, History, Package } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import ChatHistory from './components/ChatHistory';
import PaintSearch from './components/PaintSearch';
import PaintManagement from './components/PaintManagement';
import UserManagement from './components/UserManagement';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SessionProvider, useSession } from './contexts/SessionContext';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const MainContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const TabContainer = styled.div`
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.5rem;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
`;

const Tab = styled.button`
  flex: 1;
  padding: 1rem;
  border: none;
  background: ${props => props.$active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  position: relative;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }
`;

const ConversationIndicator = styled.div`
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const ContentArea = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
`;

function AppContent() {
  const { isAdmin, isLoading, isAuthenticated } = useAuth();
  const { hasActiveConversation, currentConversationId } = useSession();
  const [activeTab, setActiveTab] = useState('chat');

  const baseTabs = [
    { id: 'chat', label: 'Chat com IA', icon: MessageCircle },
    { id: 'search', label: 'Buscar Tintas', icon: Search },
  ];

  const authenticatedTabs = [
    { id: 'history', label: 'Histórico', icon: History },
  ];

  const adminTabs = [
    { id: 'management', label: 'Gerenciar Tintas', icon: Package },
    { id: 'users', label: 'Gerenciar Usuários', icon: Users },
  ];

  const isAdminUser = useMemo(() => isAdmin(), [isAdmin]);
  const isAuthUser = useMemo(() => isAuthenticated(), [isAuthenticated]);
  
  const tabs = useMemo(() => {
    let allTabs = [...baseTabs];
    if (isAuthUser) {
      allTabs = [...allTabs, ...authenticatedTabs];
    }
    if (isAdminUser) {
      allTabs = [...allTabs, ...adminTabs];
    }
    return allTabs;
  }, [isAdminUser, isAuthUser]);

  const { selectConversation } = useSession();
  
  const handleSelectConversation = (conversationId) => {
    selectConversation(conversationId);
    setActiveTab('chat');
  };

  if (isLoading) {
    return (
      <AppContainer>
        <Header />
        <MainContent>
          <ContentArea>
            <LoadingSpinner text="Carregando aplicação..." />
          </ContentArea>
        </MainContent>
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <Header />
      <MainContent>
        <TabContainer>
          {tabs.map(tab => {
            const Icon = tab.icon;
            const showIndicator = tab.id === 'chat' && hasActiveConversation;
            return (
              <Tab
                key={tab.id}
                $active={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={20} />
                {tab.label}
                {showIndicator && <ConversationIndicator />}
              </Tab>
            );
          })}
        </TabContainer>

        <ContentArea>
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'history' && <ChatHistory onSelectConversation={handleSelectConversation} selectedConversationId={currentConversationId} />}
          {activeTab === 'search' && <PaintSearch />}
          {activeTab === 'management' && <PaintManagement />}
          {activeTab === 'users' && <UserManagement />}
        </ContentArea>
      </MainContent>
    </AppContainer>
  );
}

function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <AppContent />
      </SessionProvider>
    </AuthProvider>
  );
}

export default App;
