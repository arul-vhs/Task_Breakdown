import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_REPLANNING

def replanning_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.replanning_service()
    
    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])
    
    new_hours = state.get("new_hours_per_week", 10.0)
    mode = state.get("replanning_mode", "Balanced")
    apply = state.get("apply_replanning", False)
    
    try:
        if apply:
            res = service.apply_replan(
                goal_id=goal_id,
                user_id=user_id,
                new_hours_per_week=new_hours,
                replanning_mode=mode
            )
            history = list(state.get("replanning_history") or [])
            history.append(res)
            return {
                "current_stage": STAGE_REPLANNING,
                "error": None,
                "replanning_history": history,
                "apply_replanning": False
            }
        else:
            res = service.generate_replan_preview(
                goal_id=goal_id,
                user_id=user_id,
                new_hours_per_week=new_hours,
                replanning_mode=mode
            )
            return {
                "current_stage": STAGE_REPLANNING,
                "error": None,
                "replanned_preview": res
            }
    except Exception as e:
        return {
            "current_stage": STAGE_REPLANNING,
            "error": str(e)
        }
