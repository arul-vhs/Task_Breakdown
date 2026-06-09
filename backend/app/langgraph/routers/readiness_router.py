from app.langgraph.state import GoalPilotState


def readiness_router(state: GoalPilotState) -> str:
    # Error-first guard — any upstream failure routes to error drain
    if state.get("error"):
        return "error"

    readiness = state.get("readiness") or {}
    score = readiness.get("overall_readiness_score")

    if score is None:
        # Questions were just generated — pause and wait for user answers.
        # Do NOT loop back to validation directly; that would trigger a second
        # back-to-back Gemini call before the user has had a chance to respond.
        return "wait_for_validation_answers"

    if score >= 60:
        return "roadmap"
    else:
        return "coach"

