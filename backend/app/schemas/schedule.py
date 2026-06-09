import uuid
from pydantic import BaseModel
from typing import List, Dict, Any

class ScheduleGenerateRequest(BaseModel):
    goal_id: uuid.UUID

class TimeBlockItem(BaseModel):
    task_id: str
    name: str
    time_slot: str
    duration_hours: float
    type: str

class DailyScheduleItem(BaseModel):
    week_number: int
    day_number: int
    day_name: str
    total_hours: float
    time_blocks: List[TimeBlockItem]

class TaskAllocationItem(BaseModel):
    task_id: str
    name: str
    allocated_hours: float

class WeeklyScheduleItem(BaseModel):
    week_number: int
    focus: str
    allocated_hours: float
    tasks: List[TaskAllocationItem]

class ScheduleAnalysis(BaseModel):
    confidence_score: int
    goal_completion_forecast: str
    buffer_time_allocation: str
    deadline_feasibility_analysis: str
    rescheduling_suggestions: List[Dict[str, Any]] = []

class ScheduleResponse(BaseModel):
    weekly_schedule: List[WeeklyScheduleItem]
    daily_schedule: List[DailyScheduleItem]
    schedule_analysis: ScheduleAnalysis
