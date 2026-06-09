"""
Human-in-the-loop interrupt nodes for GoalPilot LangGraph workflows.

Each function calls langgraph.types.interrupt() which:
  1. Suspends graph execution at that point
  2. Persists full workflow state to the checkpointer
  3. Returns the interrupt payload to the caller (frontend / API layer)
  4. Waits until the graph is resumed via workflow_app.invoke() or .stream()
     with the updated state injected via update_state()

Four interrupt points:

  Checkpoint 1 — wait_for_strategy_selection
    Fires after strategy_node generates options.
    Frontend shows strategies and user selects one.
    Resume payload: update_state({"selected_strategy_key": "..."})

  Checkpoint 1.5 — wait_for_validation_answers
    Fires after validation_node generates readiness questions.
    Frontend shows questions and user submits answers.
    Resume payload: update_state({"validation_answers": [{"question": ..., "answer": ...}]})
    This prevents the readiness_router from looping back to validation a second time
    before the user has a chance to answer.

  Checkpoint 2 — wait_for_plan_approval
    Fires after roadmap_node generates the full task breakdown.
    Frontend shows roadmap and user approves or requests changes.
    Resume payload: update_state({"plan_approved": True})

  Checkpoint 3 — wait_for_replan_decision
    Fires after replanning_node generates a preview.
    Frontend shows preview and user decides to apply or discard.
    Resume payload: update_state({"apply_replanning": True/False})
"""

from typing import Dict, Any
from langgraph.types import interrupt
from app.langgraph.state import GoalPilotState


def wait_for_strategy_selection(state: GoalPilotState) -> Dict[str, Any]:
    """
    Checkpoint 1 — Pause until the user selects a strategy.

    Exposes the generated strategies list to the frontend.
    Graph resumes when selected_strategy_key is injected into state.
    """
    interrupt({
        "type": "strategy_selection",
        "message": "Waiting for user strategy selection. "
                   "Update state with selected_strategy_key to resume.",
        "strategies": state.get("strategies", []),
    })
    # Unreachable during interrupt — executed only on resume.
    return {}


def wait_for_validation_answers(state: GoalPilotState) -> Dict[str, Any]:
    """
    Checkpoint 1.5 — Pause until the user answers the readiness questions.

    Fires after validation_node generates questions (first pass).
    Prevents the readiness_router from triggering a second Gemini call
    before the user has submitted answers.

    Graph resumes when validation_answers is injected into state.
    The edge wait_for_validation_answers -> validation then runs the
    evaluate pass of validation_node.
    """
    readiness = state.get("readiness") or {}
    interrupt({
        "type": "validation_answers",
        "message": "Please answer the readiness questions. "
                   "Update state with validation_answers=[{question, answer}] to resume.",
        "questions": readiness.get("validation_questions", []),
    })
    # Unreachable during interrupt — executed only on resume.
    return {}


def wait_for_plan_approval(state: GoalPilotState) -> Dict[str, Any]:
    """
    Checkpoint 2 — Pause until the user approves the generated roadmap.

    Exposes the execution_plan and full task list to the frontend.
    Graph resumes when plan_approved=True is injected into state.
    """
    interrupt({
        "type": "plan_approval",
        "message": "Waiting for roadmap approval. "
                   "Update state with plan_approved=True to proceed to scheduling.",
        "execution_plan": state.get("execution_plan", {}),
        "tasks": state.get("tasks", []),
        "task_count": len(state.get("tasks", [])),
    })
    # Unreachable during interrupt — executed only on resume.
    return {}


def wait_for_replan_decision(state: GoalPilotState) -> Dict[str, Any]:
    """
    Checkpoint 3 — Pause until the user decides on the replanning preview.

    Exposes the replanned_preview to the frontend.
    Graph resumes when apply_replanning=True/False is injected into state.
      - True  → replanning_router routes to schedule (apply changes)
      - False → replanning_router routes to END (discard preview)
    """
    interrupt({
        "type": "replan_decision",
        "message": "Waiting for replanning decision. "
                   "Update state with apply_replanning=True to apply, False to discard.",
        "preview": state.get("replanned_preview", {}),
    })
    # Unreachable during interrupt — executed only on resume.
    return {}
