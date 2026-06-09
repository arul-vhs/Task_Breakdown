import { apiClient } from './api-client';
import { ReplanPreviewResponse, ReplanApplyResponse } from '../types/api';

export const replanningService = {
  async previewReplan(goalId: string, newHours: number, mode?: string): Promise<ReplanPreviewResponse> {
    const response = await apiClient.post<ReplanPreviewResponse>('/api/v1/replan/preview', {
      goal_id: goalId,
      new_hours_per_week: newHours,
      replanning_mode: mode || 'Balanced',
    });
    return response.data;
  },

  async applyReplan(goalId: string, newHours: number, mode?: string): Promise<ReplanApplyResponse> {
    const response = await apiClient.post<ReplanApplyResponse>('/api/v1/replan/apply', {
      goal_id: goalId,
      new_hours_per_week: newHours,
      replanning_mode: mode || 'Balanced',
    });
    return response.data;
  },
};
