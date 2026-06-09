import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_EXECUTION
from app.repositories.progress_repository import ProgressRepository


def execution_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.progress_service()

    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])

    try:
        metrics = service.get_progress_metrics(goal_id=goal_id, user_id=user_id)

        # Instantiate ProgressRepository directly — ServiceFactory does not
        # expose repositories as attributes, only via factory methods.
        progress_repo = ProgressRepository(factory.db)
        reflections_data = []
        if hasattr(progress_repo, "get_reflections"):
            reflections_db = progress_repo.get_reflections(goal_id)
            reflections_data = [
                {
                    "reflection": r.reflection,
                    "suggested_adjustments": r.suggested_adjustments,
                    "encouragement_quote": r.encouragement_quote,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reflections_db
            ]

        return {
            "current_stage": STAGE_EXECUTION,
            "error": None,
            "progress": metrics,
            "reflections": reflections_data,
        }
    except Exception as e:
        return {
            "current_stage": STAGE_EXECUTION,
            "error": str(e),
        }

