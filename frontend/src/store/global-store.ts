import { create } from 'zustand';

interface UserProfile {
  role: string;
  work_style: string;
  weekly_hours_available: number;
  biggest_challenge?: string;
  full_name?: string;
}

interface GlobalState {
  token: string | null;
  userEmail: string | null;
  activeGoalId: string | null;
  profile: UserProfile | null;
  activeTab: string;
  
  // Actions
  setToken: (token: string | null, email?: string | null) => void;
  setActiveGoalId: (goalId: string | null) => void;
  setProfile: (profile: UserProfile | null) => void;
  setActiveTab: (tab: string) => void;
  logout: () => void;
}

export const useGlobalStore = create<GlobalState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  userEmail: typeof window !== 'undefined' ? localStorage.getItem('userEmail') : null,
  activeGoalId: null,
  profile: null,
  activeTab: 'dashboard',

  setToken: (token, email = null) => {
    if (token) {
      localStorage.setItem('token', token);
      if (email) localStorage.setItem('userEmail', email);
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('userEmail');
    }
    set({ token, userEmail: email });
  },
  
  setActiveGoalId: (goalId) => set({ activeGoalId: goalId }),
  
  setProfile: (profile) => set({ profile }),
  
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    set({ token: null, userEmail: null, activeGoalId: null, profile: null, activeTab: 'dashboard' });
  }
}));
