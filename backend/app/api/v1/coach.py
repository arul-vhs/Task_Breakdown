import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.coach_service import CoachService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.progress_repository import ProgressRepository
from app.providers.failover_provider import FailoverProvider
from app.core.limiter import limiter
from app.core.logger import logger, update_log_context
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
    CoachInsightsRequest,
    CoachInsightsResponse,
    CoachInsightsResponseV2
)

router = APIRouter()

def get_coach_service(db: Session = Depends(get_db)) -> CoachService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    schedule_repo = ScheduleRepository(db)
    progress_repo = ProgressRepository(db)
    provider = FailoverProvider()
    return CoachService(user_repo, goal_repo, schedule_repo, progress_repo, provider)

@router.post("/chat", response_model=CoachChatResponse)
@limiter.limit("30/minute")
def chat_with_coach(
    request: Request,
    data: CoachChatRequest,
    current_user: User = Depends(get_current_user),
    service: CoachService = Depends(get_coach_service)
):
    """
    Direct coach chat conversational loops.
    """
    update_log_context({
        "event": "coach_chat_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "coaching"
    })
    logger.info(f"Coach chat message received for goal: {data.goal_id}")
    
    try:
        reply = service.chat_with_coach(
            goal_id=data.goal_id,
            user_id=current_user.id,
            message=data.message,
            chat_history=data.chat_history
        )
        update_log_context({"event": "coach_chat_success"})
        logger.info(f"Coach chat reply generated for goal: {data.goal_id}")
        return {"reply": reply}
    except ValueError as e:
        logger.warning(f"Coach chat validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/insights", response_model=CoachInsightsResponseV2)
@limiter.limit("15/minute")
def generate_insights(
    request: Request,
    data: CoachInsightsRequest,
    current_user: User = Depends(get_current_user),
    service: CoachService = Depends(get_coach_service)
):
    """
    Gathers telemetry to compute coaching guidance insights.
    """
    update_log_context({
        "event": "coach_insights_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "coaching"
    })
    logger.info(f"Generating coach insights for goal: {data.goal_id}")
    
    try:
        result = service.generate_daily_coaching_insights(goal_id=data.goal_id, user_id=current_user.id)
        update_log_context({"event": "coach_insights_success"})
        logger.info(f"Coach insights successfully generated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Coach insights generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
