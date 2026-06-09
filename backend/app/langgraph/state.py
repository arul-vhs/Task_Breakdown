from typing import TypedDict, List, Dict, Any, Optional, NotRequired

class GoalPilotState(TypedDict):
    # Identity & session tracking
    user_id: str
    goal_id: str
    goal_title: str
    thread_id: str                         # e.g. "user_{user_id}_goal_{goal_id}" — used for checkpoint recovery
    profile: Dict[str, Any]
    goal_context: Optional[Dict[str, Any]]
    
    # Checkpoint 1 & Stage Tracking
    current_stage: str
    error: Optional[str]
    
    strategies: List[Dict[str, Any]]
    selected_strategy_key: Optional[str]

    # Human-in-the-loop inputs
    validation_answers: Optional[List[Dict[str, str]]]  # Populated at Checkpoint 1.5 interrupt
    plan_approved: Optional[bool]                       # Populated at Checkpoint 2 interrupt
    
    # Checkpoint 2
    readiness: Optional[Dict[str, Any]]
    execution_plan: Optional[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]
    
    # Scheduling & Execution
    active_schedule: Optional[Dict[str, Any]]
    progress: Dict[str, Any]
    reflections: List[Dict[str, Any]]
    coach_insights: Optional[Dict[str, Any]]
    
    # Checkpoint 3
    apply_replanning: Optional[bool]
    new_hours_per_week: Optional[float]
    replanning_mode: Optional[str]
    replanned_preview: Optional[Dict[str, Any]]
    replanning_history: List[Dict[str, Any]]
