export interface UserRegister {
  email: string;
  password?: string;
}

export interface UserResponse {
  id: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

export interface ProfileResponse {
  id: string;
  user_id: string;
  role: string;
  work_style: string;
  weekly_hours_available: number;
  biggest_challenge?: string;
  full_name?: string;
}

export interface ProfileUpdate {
  role: string;
  work_style: string;
  weekly_hours_available: number;
  biggest_challenge?: string;
  full_name?: string;
}

export interface GoalResponse {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export interface GoalCreate {
  title: string;
  description?: string;
}

export interface AnswerInput {
  question: string;
  answer: string;
}

export interface IngestionAnswers {
  answers: AnswerInput[];
}

export interface GoalDetailsResponse {
  id: string;
  title: string;
  status: string;
  created_at: string;
  description?: string;
  category?: string;
  difficulty?: string;
  estimated_duration?: string;
  required_skills?: string[];
  risks?: string[];
  qa_context?: Array<{ question: string; answer?: string }>;
}

export interface StrategyItem {
  strategy_key: string;
  title: string;
  description: string;
  pros?: string[];
  cons?: string[];
  is_recommended?: boolean;
  is_selected?: boolean;
}

export interface StrategyGenerateResponse {
  strategies: StrategyItem[];
  recommended_strategy_key: string;
  recommendation_explanation: string;
}

export interface ReadinessEvaluateResponse {
  overall_readiness_score: number;
  dimension_scores: Record<string, number>;
  identified_gaps: string[];
  remediation_steps: string[];
  validation_questions?: string[];
  answers?: AnswerInput[];
}

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
  execution_plan: any;
  tasks: TaskItem[];
  dependencies: DependencyItem[];
}

export interface TaskAllocationItem {
  task_id: string;
  name: string;
  allocated_hours: number;
}

export interface WeeklyScheduleItem {
  week_number: number;
  focus: string;
  allocated_hours: number;
  tasks: TaskAllocationItem[];
}

export interface TimeBlockItem {
  task_id: string;
  name: string;
  time_slot: string;
  duration_hours: number;
  type: string;
}

export interface DailyScheduleItem {
  week_number: number;
  day_number: number;
  day_name: string;
  total_hours: number;
  time_blocks: TimeBlockItem[];
}

export interface ScheduleAnalysis {
  confidence_score: number;
  goal_completion_forecast: string;
  buffer_time_allocation: string;
  deadline_feasibility_analysis: string;
}

export interface ScheduleResponse {
  weekly_schedule: WeeklyScheduleItem[];
  daily_schedule: DailyScheduleItem[];
  schedule_analysis: ScheduleAnalysis;
}

export interface ProgressMetrics {
  total_tasks_count: number;
  completed_tasks_count: number;
  completion_percentage: number;
  health_score: number;
  overdue_tasks_count: number;
  overdue_tasks_names?: string[];
  streak_count: number;
  time_spent_total: number;
  allocated_hours_total: number;
}

export interface ProgressUpdateResponse {
  task_id_alias: string;
  is_completed: boolean;
  time_spent: number;
  metrics: ProgressMetrics;
}

export interface AdaptiveReplanningPayload {
  risk_level: string;
  velocity_status: string;
  at_risk_tasks: string[];
  critical_delay_reason: string;
  recommended_timeline_adjustment: string;
}

export interface MemoryPayload {
  key_learnings: string[];
  user_strengths_noted: string[];
  sentiment_reflection: string;
  session_summary: string;
}

export interface CoachInsightsResponseV2 {
  daily_briefing: string;
  weekly_summary: string;
  progress_analysis: string;
  risk_assessment: string;
  motivation_message: string;
  recommended_actions: any;
  adaptive_replanning_payload: AdaptiveReplanningPayload;
  memory_payload: MemoryPayload;
}

export interface ReplanPreviewResponse {
  replanning_mode: string;
  new_hours_per_week: number;
  roadmap_health_score: number;
  completion_probability: number;
  goal_completion_forecast: string;
  risk_analysis: string;
  recommended_adjustments: string[];
  replanned_weekly_schedule: any[];
}

export interface GoalPilotState {
  user_id: string;
  goal_id: string;
  goal_title: string;
  thread_id: string;
  profile: Record<string, any>;
  goal_context?: Record<string, any>;
  current_stage: string;
  error?: string;
  strategies: StrategyItem[];
  selected_strategy_key?: string;
  validation_answers?: Record<string, string>[];
  plan_approved?: boolean;
  readiness?: ReadinessEvaluateResponse;
  execution_plan?: any;
  tasks: TaskItem[];
  dependencies: DependencyItem[];
  active_schedule?: ScheduleResponse;
  progress: Record<string, any>;
  reflections: any[];
  coach_insights?: CoachInsightsResponseV2;
  apply_replanning?: boolean;
  new_hours_per_week?: number;
  replanning_mode?: string;
  replanned_preview?: ReplanPreviewResponse;
  replanning_history: any[];
}

export interface CoachChatResponse {
  reply: string;
}

export interface ReplanApplyResponse {
  status: string;
  current_version: number;
  schedule: any;
}

export interface ValidationQuestionsResponse {
  validation_questions: string[];
}
