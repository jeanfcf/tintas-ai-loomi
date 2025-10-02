// API Configuration
import axios from 'axios';

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for image generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle 401 errors for authenticated requests (not login attempts)
    if (error.response?.status === 401 && error.config?.url?.includes('/me')) {
      // Token expired or invalid, clear auth
      localStorage.removeItem('token');
      // Only reload if not already on login page to avoid infinite loops
      if (!window.location.pathname.includes('login')) {
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    ME: '/api/v1/auth/me',
  },
  USERS: {
    LIST: '/api/v1/users/',
    CREATE: '/api/v1/users/',
    GET: (id) => `/api/v1/users/${id}`,
    UPDATE: (id) => `/api/v1/users/${id}`,
    DELETE: (id) => `/api/v1/users/${id}`,
  },
  PAINTS: {
    LIST: '/api/v1/paints/',
    LIST_PUBLIC: '/api/v1/paints/public',
    CREATE: '/api/v1/paints/',
    GET: (id) => `/api/v1/paints/${id}`,
    UPDATE: (id) => `/api/v1/paints/${id}`,
    DELETE: (id) => `/api/v1/paints/${id}`,
    SEARCH: '/api/v1/paints/search/filters',
    BY_NAME: (name) => `/api/v1/paints/by-name/${name}`,
    IMPORT_CSV: '/api/v1/paints/import-csv',
  },
  HEALTH: '/api/v1/health/',
};

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
};

export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  VISITOR: 'visitor',
};

export const USER_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  SUSPENDED: 'suspended',
};
