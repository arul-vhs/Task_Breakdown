"""
GoalPilot LangGraph — compiled StateGraph.

Topology (final production-grade):

  START
    ↓
  goal → strategy → wait_for_strategy_selection (INTERRUPT: Checkpoint 1)
    ↓
  validation (question generation)
    ↓  [readiness_router]
    ├── score is None  → validation (re-enter, waiting for answers)
    ├── score >= 60    → roadmap → wait_for_plan_approval (INTERRUPT: Checkpoint 2)
    │                     ↓
    │                   schedule → execution
    │                     ↓  [execution_router]
    │                     ├── health >= 50 → coach → END
    │                     └── health < 50  → replanning
    │                                          ↓
    │                               wait_for_replan_decision (INTERRUPT: Checkpoint 3)
    │                                          ↓  [replanning_router]
    │                                          ├── apply=True  → schedule (graph-based loop)
    │                                          └── apply=False → END
    └── score < 60     → coach → END

Error drain:
  Any router that detects state["error"] routes to error → END.

Human-in-the-loop:
  All pauses use explicit interrupt() nodes (not interrupt_before=[...]).
  The checkpointer is imported from checkpointer.py to allow backend swaps.
"""

from langgraph.graph import StateGraph, END

from app.langgraph.state import GoalPilotState
from app.langgraph.checkpointer import checkpointer

# --- Business logic nodes ---
from app.langgraph.nodes.goal_node import goal_node
from app.langgraph.nodes.strategy_node import strategy_node
from app.langgraph.nodes.validation_node import validation_node
from app.langgraph.nodes.roadmap_node import roadmap_node
from app.langgraph.nodes.schedule_node import schedule_node
from app.langgraph.nodes.execution_node import execution_node
from app.langgraph.nodes.coach_node import coach_node
from app.langgraph.nodes.replanning_node import replanning_node

# --- Human interrupt nodes ---
from app.langgraph.nodes.human_interrupt import (
    wait_for_strategy_selection,
    wait_for_validation_answers,
    wait_for_plan_approval,
    wait_for_replan_decision,
)

# --- Error drain node ---
from app.langgraph.nodes.error_node import error_node

# --- Conditional routers ---
from app.langgraph.routers.readiness_router import readiness_router
from app.langgraph.routers.execution_router import execution_router
from app.langgraph.routers.replanning_router import replanning_router


def create_workflow() -> StateGraph:
    workflow = StateGraph(GoalPilotState)

    # ------------------------------------------------------------------ #
    # Register all nodes                                                   #
    # ------------------------------------------------------------------ #

    # Business logic nodes
    workflow.add_node("goal", goal_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("roadmap", roadmap_node)
    workflow.add_node("schedule", schedule_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("coach", coach_node)
    workflow.add_node("replanning", replanning_node)

    # Human interrupt nodes (explicit pause points)
    workflow.add_node("wait_for_strategy_selection", wait_for_strategy_selection)
    workflow.add_node("wait_for_validation_answers", wait_for_validation_answers)
    workflow.add_node("wait_for_plan_approval", wait_for_plan_approval)
    workflow.add_node("wait_for_replan_decision", wait_for_replan_decision)

    # Error drain node
    workflow.add_node("error", error_node)

    # ------------------------------------------------------------------ #
    # Entry point                                                          #
    # ------------------------------------------------------------------ #
    workflow.set_entry_point("goal")

    # ------------------------------------------------------------------ #
    # Core linear path: goal discovery                                     #
    # ------------------------------------------------------------------ #
    workflow.add_edge("goal", "strategy")
    workflow.add_edge("strategy", "wait_for_strategy_selection")
    # Resume from Checkpoint 1 continues to validation
    workflow.add_edge("wait_for_strategy_selection", "validation")

    # ------------------------------------------------------------------ #
    # Checkpoint 1.5: Readiness routing                                    #
    # validation runs in two passes:                                       #
    #   Pass 1: no answers -> generates questions -> wait_for_validation_answers (INTERRUPT)
    #   Pass 2: answers present -> evaluates -> routes to roadmap or coach #
    # Routing back to "validation" directly is intentionally removed to    #
    # prevent a double Gemini call before the user has responded.          #
    # ------------------------------------------------------------------ #
    workflow.add_conditional_edges(
        "validation",
        readiness_router,
        {
            "wait_for_validation_answers": "wait_for_validation_answers",  # Checkpoint 1.5
            "roadmap": "roadmap",          # Score >= 60 -> proceed
            "coach": "coach",              # Score < 60  -> low-readiness coaching
            "error": "error",              # Error guard
        },
    )
    # Resume from Checkpoint 1.5 (validation_answers injected) -> evaluate pass
    workflow.add_edge("wait_for_validation_answers", "validation")

    # ------------------------------------------------------------------ #
    # Checkpoint 2: Plan approval                                          #
    # roadmap generates the task breakdown, then pauses for user sign-off #
    # ------------------------------------------------------------------ #
    workflow.add_edge("roadmap", "wait_for_plan_approval")
    # Resume from Checkpoint 2 (plan_approved=True) continues to schedule
    workflow.add_edge("wait_for_plan_approval", "schedule")

    # ------------------------------------------------------------------ #
    # Execution loop                                                       #
    # ------------------------------------------------------------------ #
    workflow.add_edge("schedule", "execution")

    workflow.add_conditional_edges(
        "execution",
        execution_router,
        {
            "coach": "coach",              # Health >= 50 → normal completion
            "replanning": "replanning",    # Health <  50 → trigger replan
            "error": "error",              # Error guard
        },
    )

    # ------------------------------------------------------------------ #
    # Checkpoint 3: Replan decision                                        #
    # replanning generates a preview, then pauses for user apply/discard  #
    # ------------------------------------------------------------------ #
    workflow.add_edge("replanning", "wait_for_replan_decision")

    workflow.add_conditional_edges(
        "wait_for_replan_decision",
        replanning_router,
        {
            # apply=True  → re-enter schedule → execution (graph-based loop, no while)
            "schedule": "schedule",
            # apply=False → discard preview, end workflow
            END: END,
            # Error guard
            "error": "error",
        },
    )

    # ------------------------------------------------------------------ #
    # Terminal edges                                                       #
    # ------------------------------------------------------------------ #
    workflow.add_edge("coach", END)   # Normal completion (both healthy & low-readiness paths)
    workflow.add_edge("error", END)   # Error drain terminates cleanly

    return workflow


# ------------------------------------------------------------------ #
# Compiled workflow — single instance shared across the application   #
# ------------------------------------------------------------------ #
workflow_app = create_workflow().compile(
    checkpointer=checkpointer,
    # interrupt_before is intentionally omitted.
    # Human pauses are handled by explicit interrupt() nodes.
)
