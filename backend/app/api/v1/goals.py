import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.goal_service import GoalService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.providers.failover_provider import FailoverProvider
from app.core.logger import logger, update_log_context
from app.schemas.goal import (
    GoalCreate,
    GoalResponse,
    GoalDetailsResponse,
    IngestionAnswers
)

router = APIRouter()

def get_goal_service(db: Session = Depends(get_db)) -> GoalService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    provider = FailoverProvider()
    return GoalService(user_repo, goal_repo, provider)

# ==========================================
# Phase 4 Specific Routes
# ==========================================

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new goal in the database (POST /goals).
    """
    update_log_context({
        "event": "goal_create_attempt",
        "user_id": str(current_user.id),
        "workflow_stage": "goal_discovery"
    })
    logger.info(f"Creating goal with title: {data.title}")
    
    goal_repo = GoalRepository(db)
    goal = goal_repo.create(title=data.title, user_id=current_user.id, description=data.description)
    
    update_log_context({"event": "goal_create_success", "goal_id": str(goal.id)})
    logger.info(f"Goal successfully created: {goal.id}")
    return goal

@router.post("/{goal_id}/analyze", response_model=Dict[str, Any])
def analyze_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service)
):
    """
    Runs intake analysis on a goal to construct context dynamic questions.
    """
    update_log_context({
        "event": "goal_analyze_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(goal_id),
        "workflow_stage": "goal_discovery"
    })
    logger.info(f"Analyzing goal onboarding intake: {goal_id}")
    
    try:
        result = service.analyze_goal_and_initialize_context(goal_id=goal_id, user_id=current_user.id)
        update_log_context({"event": "goal_analyze_success"})
        logger.info(f"Goal analysis successfully completed: {goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Goal analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{goal_id}/context", response_model=Dict[str, Any])
def submit_context_answers(
    goal_id: uuid.UUID,
    data: IngestionAnswers,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service)
):
    """
    Ingests responses to onboarding questionnaire context.
    """
    update_log_context({
        "event": "goal_context_submit_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(goal_id),
        "workflow_stage": "goal_discovery"
    })
    logger.info(f"Submitting ingestion answers for goal: {goal_id}")
    
    try:
        answers_list = [{"question": a.question, "answer": a.answer} for a in data.answers]
        result = service.submit_ingestion_answers(goal_id=goal_id, user_id=current_user.id, answers=answers_list)
        update_log_context({"event": "goal_context_submit_success"})
        logger.info(f"Ingestion answers successfully submitted for goal: {goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Ingestion answers submission error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# Legacy / Backward Compatibility Routes
# ==========================================

@router.get("/", response_model=List[GoalResponse])
def read_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal_repo = GoalRepository(db)
    return goal_repo.get_by_user(current_user.id)

@router.get("/{goal_id}", response_model=GoalDetailsResponse)
def read_goal_details(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal_repo = GoalRepository(db)
    goal = goal_repo.get_by_id(goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
        
    ctx = goal.goal_context
    return {
        "id": str(goal.id),
        "title": goal.title,
        "description": goal.description,
        "status": goal.status,
        "created_at": goal.created_at,
        "category": ctx.category if ctx else None,
        "difficulty": ctx.difficulty if ctx else None,
        "estimated_duration": ctx.estimated_duration if ctx else None,
        "required_skills": ctx.required_skills if ctx else [],
        "risks": ctx.risks if ctx else [],
        "qa_context": ctx.qa_context if ctx else []
    }
