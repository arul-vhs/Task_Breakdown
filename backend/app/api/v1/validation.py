import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.validation_service import ValidationService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.failover_provider import FailoverProvider
from app.core.logger import logger, update_log_context
from app.schemas.validation import (
    ValidationQuestionsRequest,
    ValidationQuestionsResponse,
    ReadinessEvaluateRequest,
    ReadinessEvaluateResponse
)

router = APIRouter()

def get_validation_service(db: Session = Depends(get_db)) -> ValidationService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    strategy_repo = StrategyRepository(db)
    provider = FailoverProvider()
    return ValidationService(user_repo, goal_repo, strategy_repo, provider)

@router.post("/questions", response_model=ValidationQuestionsResponse)
def get_validation_questions(
    data: ValidationQuestionsRequest,
    current_user: User = Depends(get_current_user),
    service: ValidationService = Depends(get_validation_service)
):
    """
    Generates 3 dynamic strategy validation audit questions.
    """
    update_log_context({
        "event": "validation_questions_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "validation"
    })
    logger.info(f"Generating validation questions for goal: {data.goal_id}")
    
    try:
        result = service.generate_validation_questions(goal_id=data.goal_id, user_id=current_user.id)
        update_log_context({"event": "validation_questions_success"})
        logger.info(f"Validation questions successfully generated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Validation questions generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate", response_model=ReadinessEvaluateResponse)
def evaluate_readiness(
    data: ReadinessEvaluateRequest,
    current_user: User = Depends(get_current_user),
    service: ValidationService = Depends(get_validation_service)
):
    """
    Grades validation answers and calculates overall score & dimension score indexes.
    """
    update_log_context({
        "event": "validation_evaluate_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "validation"
    })
    logger.info(f"Evaluating validation readiness for goal: {data.goal_id}")
    
    try:
        qa_list = [{"question": a.question, "answer": a.answer} for a in data.answers]
        result = service.evaluate_readiness(goal_id=data.goal_id, user_id=current_user.id, qa_list=qa_list)
        update_log_context({"event": "validation_evaluate_success"})
        logger.info(f"Validation readiness successfully evaluated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Validation evaluation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
