import { create } from 'zustand';

interface AuthState {
  token: string | null;
  userEmail: string | null;
  setToken: (token: string | null, email?: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  userEmail: typeof window !== 'undefined' ? localStorage.getItem('userEmail') : null,

  setToken: (token, email = null) => {
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
        if (email) localStorage.setItem('userEmail', email);
        
        // Sync with cookie for Next.js Middleware route guard
        // Set secure cookie expiring in 7 days
        const secure = window.location.protocol === 'https:' ? 'Secure;' : '';
        document.cookie = `access_token=${token}; Path=/; Max-Age=${7 * 24 * 3600}; SameSite=Lax; ${secure}`;
      } else {
        localStorage.removeItem('token');
        localStorage.removeItem('userEmail');
        document.cookie = 'access_token=; Path=/; Max-Age=0';
      }
    }
    set({ token, userEmail: email });
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('userEmail');
      document.cookie = 'access_token=; Path=/; Max-Age=0';
    }
    set({ token: null, userEmail: null });
  }
}));
