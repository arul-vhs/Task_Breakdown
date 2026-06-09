import uuid
from pydantic import BaseModel
from typing import List, Dict, Any

class ReplanPreviewRequest(BaseModel):
    goal_id: uuid.UUID
    new_hours_per_week: float
    replanning_mode: str = "Balanced"  # Balanced, Catch Up, Low Stress, Aggressive

class ReplanPreviewResponse(BaseModel):
    replanning_mode: str
    new_hours_per_week: float
    roadmap_health_score: int
    completion_probability: int
    goal_completion_forecast: str
    risk_analysis: str
    recommended_adjustments: List[str]
    replanned_weekly_schedule: List[Dict[str, Any]]

class ReplanApplyRequest(BaseModel):
    goal_id: uuid.UUID
    new_hours_per_week: float
    replanning_mode: str = "Balanced"

class ReplanApplyResponse(BaseModel):
    status: str
    current_version: int
    schedule: Dict[str, Any]
