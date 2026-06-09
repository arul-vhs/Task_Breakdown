import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_COACHING

def coach_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.coach_service()
    
    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])
    
    try:
        res = service.generate_daily_coaching_insights(goal_id=goal_id, user_id=user_id)
        return {
            "current_stage": STAGE_COACHING,
            "error": None,
            "coach_insights": res
        }
    except Exception as e:
        return {
            "current_stage": STAGE_COACHING,
            "error": str(e)
        }
