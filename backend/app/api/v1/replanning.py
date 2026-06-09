import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.replanning_service import ReplanningService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.progress_repository import ProgressRepository
from app.providers.failover_provider import FailoverProvider
from app.core.limiter import limiter
from app.core.logger import logger, update_log_context
from app.schemas.replan import (
    ReplanPreviewRequest,
    ReplanPreviewResponse,
    ReplanApplyRequest,
    ReplanApplyResponse
)

router = APIRouter()

def get_replanning_service(db: Session = Depends(get_db)) -> ReplanningService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    schedule_repo = ScheduleRepository(db)
    progress_repo = ProgressRepository(db)
    provider = FailoverProvider()
    return ReplanningService(user_repo, goal_repo, schedule_repo, progress_repo, provider)

@router.post("/preview", response_model=ReplanPreviewResponse)
@limiter.limit("10/minute")
def preview_replan(
    request: Request,
    data: ReplanPreviewRequest,
    current_user: User = Depends(get_current_user),
    service: ReplanningService = Depends(get_replanning_service)
):
    """
    Constructs adaptive reschedule timeline adjustment previews.
    """
    update_log_context({
        "event": "replan_preview_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "replanning"
    })
    logger.info(f"Generating replan preview for goal: {data.goal_id}")
    
    try:
        result = service.generate_replan_preview(
            goal_id=data.goal_id,
            user_id=current_user.id,
            new_hours_per_week=data.new_hours_per_week,
            replanning_mode=data.replanning_mode
        )
        update_log_context({"event": "replan_preview_success"})
        logger.info(f"Replan preview successfully generated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Replan preview generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply", response_model=ReplanApplyResponse)
def apply_replan(
    data: ReplanApplyRequest,
    current_user: User = Depends(get_current_user),
    service: ReplanningService = Depends(get_replanning_service)
):
    """
    Sets capacity, recalculates timelines, logs snapshots, and applies reschedules.
    """
    update_log_context({
        "event": "replan_apply_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "replanning"
    })
    logger.info(f"Applying replan for goal: {data.goal_id}")
    
    try:
        result = service.apply_replan(
            goal_id=data.goal_id,
            user_id=current_user.id,
            new_hours_per_week=data.new_hours_per_week,
            replanning_mode=data.replanning_mode
        )
        update_log_context({"event": "replan_apply_success"})
        logger.info(f"Replan successfully applied for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Replan apply error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
