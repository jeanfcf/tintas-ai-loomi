import React, { useState } from 'react';
import styled from 'styled-components';
import { Sparkles, Palette, User, LogOut, Settings, Crown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import LoginModal from './LoginModal';

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
`;

const LogoIcon = styled.div`
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  border-radius: 12px;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Tagline = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin: 0;
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const LoginButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(45deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
`;

const UserDetails = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
`;

const UserName = styled.div`
  font-weight: 500;
  font-size: 0.9rem;
`;

const UserRole = styled.div`
  font-size: 0.8rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleGuestLogin = () => {
    // Guest mode - no authentication needed
    console.log('Guest mode activated');
  };

  const handleLogout = () => {
    logout();
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Crown size={12} />;
      case 'user':
        return <User size={12} />;
      default:
        return <User size={12} />;
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'admin':
        return 'Administrador';
      case 'user':
        return 'Usuário';
      default:
        return 'Visitante';
    }
  };

  return (
    <>
      <HeaderContainer>
        <HeaderContent>
          <Logo>
            <LogoIcon>
              <Palette size={24} />
            </LogoIcon>
            <div>
              <div>Tintas AI</div>
              <Tagline>Catálogo Inteligente Suvinil</Tagline>
            </div>
          </Logo>
          
          <UserSection>
            {isAuthenticated() ? (
              <>
                <UserInfo>
                  <UserAvatar>
                    {getInitials(user.full_name || user.username)}
                  </UserAvatar>
                  <UserDetails>
                    <UserName>{user.full_name || user.username}</UserName>
                    <UserRole>
                      {getRoleIcon(user.role)}
                      {getRoleLabel(user.role)}
                    </UserRole>
                  </UserDetails>
                </UserInfo>
                <LogoutButton onClick={handleLogout}>
                  <LogOut size={16} />
                  Sair
                </LogoutButton>
              </>
            ) : (
              <LoginButton onClick={() => setShowLoginModal(true)}>
                <User size={16} />
                Entrar
              </LoginButton>
            )}
            
            <StatusIndicator>
              <StatusDot />
              <span>Sistema Ativo</span>
              <Sparkles size={16} />
            </StatusIndicator>
          </UserSection>
        </HeaderContent>
      </HeaderContainer>

      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          onGuestLogin={handleGuestLogin}
        />
      )}
    </>
  );
}

export default Header;
