import { apiClient } from './api-client';

export interface StrategyItem {
  strategy_key: string;
  title: string;
  description: string;
  pros: string[];
  cons: string[];
  is_recommended: boolean;
  is_selected: boolean;
}

export interface StrategyGenerateResponse {
  strategies: StrategyItem[];
  recommended_strategy_key: string;
  recommendation_explanation: string;
}

export const strategyService = {
  /** Calls LLM to generate 3 strategy options for a goal */
  async generateStrategies(goalId: string): Promise<StrategyGenerateResponse> {
    const response = await apiClient.post<StrategyGenerateResponse>(
      '/api/v1/strategies/generate',
      { goal_id: goalId }
    );
    return response.data;
  },

  /** Persists the user's chosen strategy */
  async selectStrategy(goalId: string, strategyKey: string): Promise<{ status: string; strategy_key: string }> {
    const response = await apiClient.post('/api/v1/strategies/select', {
      goal_id: goalId,
      strategy_key: strategyKey,
    });
    return response.data;
  },
};
