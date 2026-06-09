import { apiClient } from './api-client';
import { GoalResponse, GoalCreate, GoalDetailsResponse } from '../types/api';

export const goalService = {
  async listGoals(): Promise<GoalResponse[]> {
    const response = await apiClient.get<GoalResponse[]>('/api/v1/goals/');
    return response.data;
  },

  async createGoal(payload: GoalCreate): Promise<GoalResponse> {
    const response = await apiClient.post<GoalResponse>('/api/v1/goals/', payload);
    return response.data;
  },

  /** Runs LLM analysis and returns dynamic intake questions */
  async analyzeGoal(goalId: string): Promise<{
    goal_id: string;
    status: string;
    category: string;
    difficulty: string;
    estimated_duration: string;
    required_skills: string[];
    risks: string[];
    questions: string[];
  }> {
    const response = await apiClient.post(`/api/v1/goals/${goalId}/analyze`);
    return response.data;
  },

  /** Submits answers to the dynamic intake questions */
  async submitContextAnswers(
    goalId: string,
    answers: { question: string; answer: string }[]
  ): Promise<{ status: string }> {
    const response = await apiClient.post(`/api/v1/goals/${goalId}/context`, { answers });
    return response.data;
  },

  async getGoalDetails(goalId: string): Promise<GoalDetailsResponse> {
    const response = await apiClient.get<GoalDetailsResponse>(`/api/v1/goals/${goalId}`);
    return response.data;
  },
};
