import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.scheduling_service import SchedulingService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    ScheduleGenerateRequest,
    ScheduleResponse
)

router = APIRouter()

def get_scheduling_service(db: Session = Depends(get_db)) -> SchedulingService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    schedule_repo = ScheduleRepository(db)
    return SchedulingService(user_repo, goal_repo, schedule_repo)

@router.post("/generate", response_model=ScheduleResponse)
def generate_schedule(
    data: ScheduleGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: SchedulingService = Depends(get_scheduling_service)
):
    """
    Runs deterministic Topological Sort and safety buffer capacity mapping to construct calendar blocks (POST /schedule/generate).
    """
    try:
        result = service.generate_active_schedule(goal_id=data.goal_id, user_id=current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
