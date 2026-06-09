import { apiClient } from './api-client';
import { CoachChatResponse, CoachInsightsResponseV2 } from '../types/api';

export const coachService = {
  async chatWithCoach(goalId: string, message: string, chatHistory?: any[]): Promise<CoachChatResponse> {
    const response = await apiClient.post<CoachChatResponse>('/api/v1/coach/chat', {
      goal_id: goalId,
      message,
      chat_history: chatHistory || [],
    });
    return response.data;
  },

  async generateInsights(goalId: string): Promise<CoachInsightsResponseV2> {
    const response = await apiClient.post<CoachInsightsResponseV2>('/api/v1/coach/insights', {
      goal_id: goalId,
    });
    return response.data;
  },
};
