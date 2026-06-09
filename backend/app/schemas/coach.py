import uuid
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class CoachChatRequest(BaseModel):
    goal_id: uuid.UUID
    message: str
    chat_history: List[Dict[str, str]] = []

class CoachChatResponse(BaseModel):
    reply: str

class CoachInsightsRequest(BaseModel):
    goal_id: uuid.UUID

class CoachInsightsResponse(BaseModel):
    risk_level: str
    critical_risks: List[str]
    action_items: List[str]
    coaching_summary: str

class AdaptiveReplanningPayload(BaseModel):
    risk_level: str
    velocity_status: str
    at_risk_tasks: List[str]
    critical_delay_reason: str
    recommended_timeline_adjustment: str

class MemoryPayload(BaseModel):
    key_learnings: List[str]
    user_strengths_noted: List[str]
    sentiment_reflection: str
    session_summary: str

class CoachInsightsResponseV2(BaseModel):
    daily_briefing: str
    weekly_summary: str
    progress_analysis: str
    risk_assessment: str
    motivation_message: str
    recommended_actions: Any  # Can be markdown String or List[str]
    adaptive_replanning_payload: AdaptiveReplanningPayload
    memory_payload: MemoryPayload

