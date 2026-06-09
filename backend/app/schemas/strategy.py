import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class StrategyItem(BaseModel):
    strategy_key: str
    title: str
    description: str
    pros: List[str] = []
    cons: List[str] = []
    is_recommended: bool = False
    is_selected: bool = False

class StrategyGenerateInput(BaseModel):
    goal_id: uuid.UUID

class StrategyGenerateResponse(BaseModel):
    strategies: List[StrategyItem]
    recommended_strategy_key: str
    recommendation_explanation: str

class StrategySelect(BaseModel):
    goal_id: uuid.UUID
    strategy_key: str
