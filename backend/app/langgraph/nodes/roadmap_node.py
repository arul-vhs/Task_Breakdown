import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_ROADMAP

def roadmap_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.blueprint_service()
    
    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])
    
    execution_plan = state.get("execution_plan") or {}
    refinement = execution_plan.get("blueprint_refinement", "Standard")
    
    try:
        res = service.generate_roadmap_and_tasks(
            goal_id=goal_id,
            user_id=user_id,
            refinement_choice=refinement,
            depth="Detailed"
        )
        return {
            "current_stage": STAGE_ROADMAP,
            "error": None,
            "execution_plan": {
                "blueprint_refinement": refinement,
                "total_phases": res.get("total_phases")
            },
            "tasks": res.get("tasks", []),
            "dependencies": res.get("dependencies", [])
        }
    except Exception as e:
        return {
            "current_stage": STAGE_ROADMAP,
            "error": str(e)
        }
