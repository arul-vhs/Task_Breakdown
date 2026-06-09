import { apiClient } from './api-client';

export interface ValidationQuestionsResponse {
  validation_questions: string[];
}

export interface ReadinessEvaluateResponse {
  overall_readiness_score: number;
  dimension_scores: Record<string, number>;
  identified_gaps: string[];
  remediation_steps: string[];
}

export const validationService = {
  /** Generates 3 dynamic validation audit questions for a goal */
  async getValidationQuestions(goalId: string): Promise<ValidationQuestionsResponse> {
    const response = await apiClient.post<ValidationQuestionsResponse>(
      '/api/v1/validation/questions',
      { goal_id: goalId }
    );
    return response.data;
  },

  /** Evaluates the user's answers and returns a readiness score */
  async evaluateReadiness(
    goalId: string,
    answers: { question: string; answer: string }[]
  ): Promise<ReadinessEvaluateResponse> {
    const response = await apiClient.post<ReadinessEvaluateResponse>(
      '/api/v1/validation/evaluate',
      { goal_id: goalId, answers }
    );
    return response.data;
  },
};
