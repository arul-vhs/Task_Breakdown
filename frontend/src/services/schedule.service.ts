import { apiClient } from './api-client';
import { ScheduleResponse } from '../types/api';

export const scheduleService = {
  async generateSchedule(goalId: string): Promise<ScheduleResponse> {
    const response = await apiClient.post<ScheduleResponse>('/api/v1/schedule/generate', {
      goal_id: goalId,
    });
    return response.data;
  },
};
