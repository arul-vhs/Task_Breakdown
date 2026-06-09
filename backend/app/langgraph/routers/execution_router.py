from app.langgraph.state import GoalPilotState


def execution_router(state: GoalPilotState) -> str:
    # Error-first guard — any upstream failure routes to error drain
    if state.get("error"):
        return "error"

    progress = state.get("progress") or {}
    health_score = progress.get("health_score", 100)

    if health_score < 50:
        return "replanning"
    else:
        return "coach"
