from langgraph.graph import END
from app.langgraph.state import GoalPilotState


def replanning_router(state: GoalPilotState) -> str:
    # Error-first guard — any upstream failure routes to error drain
    if state.get("error"):
        return "error"

    apply = state.get("apply_replanning", False)

    if apply:
        return "schedule"
    else:
        return END
