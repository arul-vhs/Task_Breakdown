"""
Central error handling node for GoalPilot LangGraph workflows.

This node is the terminal drain for any workflow error. All conditional
routers check state["error"] first and route here if set.

Responsibilities:
  - Log the error with full stage context
  - Prevent unhandled exceptions from crashing the graph
  - Return a safe, inspectable state for the frontend
  - Preserve current_stage so the caller knows which node failed
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState

logger = logging.getLogger(__name__)


def error_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Terminal error drain node.

    Invoked whenever any router detects state["error"] is set.
    Logs the failure and returns the state unchanged so the
    frontend can surface the error message to the user.
    """
    stage = state.get("current_stage", "unknown")
    error_msg = state.get("error", "Unknown error")
    thread_id = state.get("thread_id", "unknown")

    logger.error(
        "[GoalPilot] Workflow error detected | thread_id=%s | stage=%s | error=%s",
        thread_id,
        stage,
        error_msg,
    )

    # Return state unchanged — the error and stage are already set.
    # The graph terminates at END after this node.
    return {
        "current_stage": stage,
        "error": error_msg,
    }
