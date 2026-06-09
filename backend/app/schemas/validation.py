import uuid
from pydantic import BaseModel
from typing import List, Dict

class ValidationQuestionsRequest(BaseModel):
    goal_id: uuid.UUID

class ValidationQuestionsResponse(BaseModel):
    validation_questions: List[str]

class AnswerInput(BaseModel):
    question: str
    answer: str

class ReadinessEvaluateRequest(BaseModel):
    goal_id: uuid.UUID
    answers: List[AnswerInput]

class ReadinessEvaluateResponse(BaseModel):
    overall_readiness_score: int
    dimension_scores: Dict[str, int]
    identified_gaps: List[str]
    remediation_steps: List[str]
