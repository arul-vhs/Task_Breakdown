import { useQuery } from '@tanstack/react-query';
import { workflowService } from '../services/workflow.service';

export function useWorkflowState(threadId: string | null) {
  return useQuery({
    queryKey: ['workflowState', threadId],
    queryFn: async () => {
      if (!threadId) throw new Error("Thread ID is required");
      return workflowService.getWorkflowState(threadId);
    },
    enabled: !!threadId,
    refetchInterval: (query) => {
      const stage = query.state.data?.data?.current_stage;
      // No stage yet — workflow still initializing, poll fast
      if (!stage || stage === 'goal_analysis') return 4000;
      // At human-in-the-loop checkpoints — user is deciding, poll slowly
      if (stage === 'strategy_selection') return 15000;
      // Active execution phases — relax polling
      if (stage === 'execution' || stage === 'coaching') return 10000;
      // All other phases (validation, roadmap, etc.) — moderate polling
      return 5000;
    },
    retry: 3,
    retryDelay: 2000,
  });
}

