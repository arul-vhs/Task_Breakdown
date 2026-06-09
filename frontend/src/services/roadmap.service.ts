import { apiClient } from './api-client';

export interface TaskItem {
  phase_number: number;
  phase_name: string;
  task_id_alias: string;
  name: string;
  title: string;
  description: string;
  allocated_hours: number;
}

export interface DependencyItem {
  task_id_alias: string;
  depends_on_alias: string;
}

export interface RoadmapGenerateResponse {
  execution_plan: Record<string, any>;
  tasks: TaskItem[];
  dependencies: DependencyItem[];
}

export const roadmapService = {
  /** Generates a phased roadmap with tasks and dependencies */
  async generateRoadmap(
    goalId: string,
    refinementChoice: string = 'Standard',
    depth: string = 'Detailed'
  ): Promise<RoadmapGenerateResponse> {
    const response = await apiClient.post<RoadmapGenerateResponse>(
      '/api/v1/roadmap/generate',
      {
        goal_id: goalId,
        refinement_choice: refinementChoice,
        depth,
      }
    );
    return response.data;
  },
};
