import axios from 'axios';
import { useAuthStore } from '../store/auth.store';

const HOST_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: HOST_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to inject JWT token and generate request correlation trace IDs
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Injects a client-side request correlation ID for tracing support
    if (typeof window !== 'undefined') {
      config.headers['X-Request-ID'] = crypto.randomUUID();
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle correlation logging and session sweep on 401
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const status = error.response?.status;
    
    if (status === 401) {
      console.warn("Unauthorized API access detected, clearing session store...");
      useAuthStore.getState().logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    // Normalize FastAPI detail error message
    let errorMessage = 'An error occurred during request execution.';
    if (error.response?.data?.error?.message) {
      errorMessage = error.response.data.error.message;
    } else if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
    }
    
    return Promise.reject(new Error(errorMessage));
  }
);
