import { apiClient } from './api-client';
import { ProgressMetrics, ProgressUpdateResponse } from '../types/api';

export const progressService = {
  async updateProgress(
    goalId: string,
    taskAlias: string,
    isCompleted: boolean,
    timeSpent?: number
  ): Promise<ProgressUpdateResponse> {
    const response = await apiClient.post<ProgressUpdateResponse>('/api/v1/progress/update', {
      goal_id: goalId,
      task_alias: taskAlias,
      is_completed: isCompleted,
      time_spent: timeSpent,
    });
    return response.data;
  },

  async getProgressMetrics(goalId: string): Promise<ProgressMetrics> {
    const response = await apiClient.get<ProgressMetrics>(`/api/v1/progress/${goalId}`);
    return response.data;
  },
};
