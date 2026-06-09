import uuid
import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GoalCreate(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None

class GoalResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class GoalDetailsResponse(GoalResponse):
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[str] = None
    required_skills: List[str] = []
    risks: List[str] = []
    qa_context: List[Dict[str, Any]] = []

class AnswerInput(BaseModel):
    question: str
    answer: str

class IngestionAnswers(BaseModel):
    answers: List[AnswerInput]
