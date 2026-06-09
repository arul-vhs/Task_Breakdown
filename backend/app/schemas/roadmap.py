import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RoadmapGenerateRequest(BaseModel):
    goal_id: uuid.UUID
    refinement_choice: str = "Standard"  # Minimalist, Standard, Comprehensive
    depth: str = "Detailed"

class TaskItem(BaseModel):
    phase_number: int
    phase_name: str
    task_id_alias: str
    name: str
    title: str
    description: str
    allocated_hours: float

class DependencyItem(BaseModel):
    task_id_alias: str
    depends_on_alias: str

class RoadmapGenerateResponse(BaseModel):
    execution_plan: Dict[str, Any]
    tasks: List[TaskItem]
    dependencies: List[DependencyItem]
