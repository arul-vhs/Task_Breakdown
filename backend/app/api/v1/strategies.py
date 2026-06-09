import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.services.strategy_service import StrategyService
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.failover_provider import FailoverProvider
from app.core.limiter import limiter
from app.core.logger import logger, update_log_context
from app.schemas.strategy import (
    StrategyGenerateInput,
    StrategyGenerateResponse,
    StrategySelect
)

router = APIRouter()

def get_strategy_service(db: Session = Depends(get_db)) -> StrategyService:
    user_repo = UserRepository(db)
    goal_repo = GoalRepository(db)
    strategy_repo = StrategyRepository(db)
    provider = FailoverProvider()
    return StrategyService(user_repo, goal_repo, strategy_repo, provider)

@router.post("/generate", response_model=StrategyGenerateResponse)
@limiter.limit("10/minute")
def generate_strategies(
    request: Request,
    data: StrategyGenerateInput,
    current_user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Invokes LLM provider to construct Fast MVP, Balanced Growth, Ambitious Scale options.
    """
    update_log_context({
        "event": "strategy_generate_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "strategy_selection"
    })
    logger.info(f"Generating strategies for goal: {data.goal_id}")
    
    try:
        result = service.generate_strategies(goal_id=data.goal_id, user_id=current_user.id)
        update_log_context({"event": "strategy_generate_success"})
        logger.info(f"Strategies successfully generated for goal: {data.goal_id}")
        return result
    except ValueError as e:
        logger.warning(f"Strategy generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/select", response_model=Dict[str, Any])
def select_strategy(
    data: StrategySelect,
    current_user: User = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Sets selected strategy pathway for goal checkpoints.
    """
    update_log_context({
        "event": "strategy_select_attempt",
        "user_id": str(current_user.id),
        "goal_id": str(data.goal_id),
        "workflow_stage": "strategy_selection"
    })
    logger.info(f"Selecting strategy {data.strategy_key} for goal: {data.goal_id}")
    
    try:
        result = service.select_strategy(goal_id=data.goal_id, strategy_key=data.strategy_key, user_id=current_user.id)
        update_log_context({"event": "strategy_select_success"})
        logger.info(f"Strategy {data.strategy_key} selected for goal: {data.goal_id}")
        return {
            "status": "selected",
            "strategy_key": result["strategy"].strategy_key
        }
    except ValueError as e:
        logger.warning(f"Strategy selection error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
