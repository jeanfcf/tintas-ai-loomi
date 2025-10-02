import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import apiClient, { API_ENDPOINTS } from '../config/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => {
    const storedToken = localStorage.getItem('token');
    return storedToken;
  });
  const [isLoading, setIsLoading] = useState(true);
  const hasInitialized = useRef(false);

  // Token is now handled by axios interceptor

  const logout = useCallback(async () => {
    try {
      if (token) {
        await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    // Prevent double execution in React StrictMode
    if (hasInitialized.current) {
      return;
    }
    hasInitialized.current = true;

    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          // Clear invalid token
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []); // Run only once on mount

  const login = async (username, password) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
        username,
        password
      });

      const { access_token } = response.data;
      
      setToken(access_token);
      localStorage.setItem('token', access_token);
      
      // Get user data after successful login
      try {
        const userResponse = await apiClient.get(API_ENDPOINTS.AUTH.ME);
        setUser(userResponse.data);
      } catch (userError) {
        console.error('Failed to get user data:', userError);
        // Don't fail login if user data fetch fails
      }
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      
      // Improved error handling
      let errorMessage = 'Erro ao fazer login';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 401) {
          errorMessage = 'Usuário ou senha incorretos';
        } else if (status === 422) {
          errorMessage = data.detail || 'Dados inválidos';
        } else if (status === 500) {
          errorMessage = 'Erro interno do servidor. Tente novamente.';
        } else if (data && data.detail) {
          errorMessage = data.detail;
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Erro de conexão. Verifique sua internet.';
      } else {
        // Other error
        errorMessage = error.message || 'Erro desconhecido';
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const isAuthenticated = useCallback(() => {
    return !!token && !!user;
  }, [token, user]);

  const isAdmin = useCallback(() => {
    return user?.role === 'admin';
  }, [user]);

  const value = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated,
    isAdmin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
