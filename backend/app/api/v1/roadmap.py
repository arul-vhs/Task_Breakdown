import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.blueprint_service import BlueprintService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.failover_provider import FailoverProvider
from app.core.logger import logger, update_log_context
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    RoadmapGenerateResponse
)

router = APIRouter()

def get_blueprint_service(db: Session = Depends(get_db)) -> BlueprintService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    strategy_repo = StrategyRepository(db)
    provider = FailoverProvider()
    return BlueprintService(user_repo, goal_repo, strategy_repo, provider)

@router.post("/generate", response_model=RoadmapGenerateResponse)
def generate_roadmap(
    data: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: BlueprintService = Depends(get_blueprint_service)
):
    """
    Formulates a phased roadmap and decomposes tasks & dependencies.
    """
    update_log_context({
        "event": "roadmap_generate_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "roadmap_generation"
    })
    logger.info(f"Generating roadmap blueprint for goal: {data.goal_id}")
    
    try:
        result = service.generate_roadmap_and_tasks(
            goal_id=data.goal_id,
            user_id=current_user.id,
            refinement_choice=data.refinement_choice,
            depth=data.depth
        )
        update_log_context({"event": "roadmap_generate_success"})
        logger.info(f"Roadmap blueprint successfully generated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Roadmap generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
