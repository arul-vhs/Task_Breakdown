export const WorkflowStages = {
  GOAL_ANALYSIS: "goal_analysis",
  STRATEGY_SELECTION: "strategy_selection",
  VALIDATION: "validation",
  ROADMAP_GENERATION: "roadmap_generation",
  SCHEDULING: "scheduling",
  EXECUTION: "execution",
  COACHING: "coaching",
  REPLANNING: "replanning",
} as const;

export type WorkflowStageType = typeof WorkflowStages[keyof typeof WorkflowStages];
