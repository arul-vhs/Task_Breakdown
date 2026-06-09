import { apiClient } from './api-client';
import { GoalPilotState } from '../types/api';

export const workflowService = {
  async getWorkflowSummary(threadId: string): Promise<any> {
    const response = await apiClient.get<any>(`/api/v1/workflows/${threadId}`);
    return response.data;
  },

  async getWorkflowState(threadId: string): Promise<{ success: boolean; data: GoalPilotState }> {
    const response = await apiClient.get<{ success: boolean; data: GoalPilotState }>(`/api/v1/workflows/${threadId}/state`);
    return response.data;
  },

  async getWorkflowHistory(threadId: string): Promise<{ stages: string[] }> {
    const response = await apiClient.get<{ stages: string[] }>(`/api/v1/workflows/${threadId}/history`);
    return response.data;
  },

  async resumeWorkflow(threadId: string, payload: Record<string, any>): Promise<any> {
    const response = await apiClient.post<any>(`/api/v1/workflows/${threadId}/resume`, payload);
    return response.data;
  },
};
export type WorkflowServiceType = typeof workflowService;
