import { create } from 'zustand';

interface UIState {
  theme: 'dark' | 'light';
  sidebarOpen: boolean;
  selectedGoalId: string | null;
  workflowResumePayload: Record<string, any> | null;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSelectedGoalId: (id: string | null) => void;
  setResumePayload: (payload: Record<string, any> | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  theme: 'dark',
  sidebarOpen: true,
  selectedGoalId: typeof window !== 'undefined' ? localStorage.getItem('selectedGoalId') : null,
  workflowResumePayload: null,

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  setSelectedGoalId: (id) => {
    if (typeof window !== 'undefined') {
      if (id) {
        localStorage.setItem('selectedGoalId', id);
      } else {
        localStorage.removeItem('selectedGoalId');
      }
    }
    set({ selectedGoalId: id });
  },

  setResumePayload: (payload) => set({ workflowResumePayload: payload })
}));
