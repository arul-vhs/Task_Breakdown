import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.progress_service import ProgressService
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.progress import (
    ProgressUpdateRequest,
    ProgressUpdateResponse,
    ProgressMetrics
)

router = APIRouter()

def get_progress_service(db: Session = Depends(get_db)) -> ProgressService:
    goal_repo = GoalRepository(db)
    progress_repo = ProgressRepository(db)
    return ProgressService(goal_repo, progress_repo)

@router.post("/update", response_model=ProgressUpdateResponse)
def update_progress(
    data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProgressService = Depends(get_progress_service)
):
    """
    Updates completion state of task checkpoints and logs telemetry.
    """
    try:
        result = service.toggle_task(
            goal_id=data.goal_id,
            task_alias=data.task_alias,
            is_completed=data.is_completed,
            time_spent=data.time_spent,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{goal_id}", response_model=ProgressMetrics)
def get_progress_metrics(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ProgressService = Depends(get_progress_service)
):
    """
    Retrieves project telemetry aggregates.
    """
    try:
        result = service.get_progress_metrics(goal_id=goal_id, user_id=current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
