import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProgressUpdateRequest(BaseModel):
    goal_id: uuid.UUID
    task_alias: str
    is_completed: bool
    time_spent: float = 0.0

class ProgressMetrics(BaseModel):
    total_tasks_count: int
    completed_tasks_count: int
    completion_percentage: float
    health_score: int
    overdue_tasks_count: int
    overdue_tasks_names: List[str] = []
    streak_count: int
    time_spent_total: float
    allocated_hours_total: float

class ProgressUpdateResponse(BaseModel):
    task_id_alias: str
    is_completed: bool
    time_spent: float
    metrics: ProgressMetrics
