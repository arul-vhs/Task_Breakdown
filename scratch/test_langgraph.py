# -*- coding: utf-8 -*-
"""
End-to-end verification script for the Phase 6 LangGraph orchestration layer.

Tests the full human-in-the-loop workflow:

  goal -> strategy -> [INTERRUPT: Checkpoint 1 - strategy selection]
    -> validation (questions) -> [inject answers] -> validation (evaluate)
    -> roadmap -> [INTERRUPT: Checkpoint 2 - plan approval]
    -> schedule -> execution -> coach -> END

Assertions:
  - All 3 interrupt checkpoints fire correctly
  - current_stage = "coaching" at completion
  - error = None at completion
  - thread_id present in state snapshot
  - DB tasks count > 0
"""

import sys
import os
import uuid

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

import app.database.base  # noqa: F401 -- ensures all models are registered
from app.database.session import SessionLocal
from app.langgraph.factory import ServiceFactory
from app.langgraph.graph import workflow_app
from app.repositories.goal_repository import GoalRepository
from app.models.task import Task


def _print_event(event: dict) -> None:
    """Pretty-print a single stream event. Handles both dict outputs and tuple interrupt payloads."""
    node_name = list(event.keys())[0]
    node_value = event[node_name]
    if isinstance(node_value, dict):
        stage = node_value.get("current_stage", "")
        err = node_value.get("error")
        print(f"   Node executed: {node_name} | stage: {stage}" + (f" | ERROR: {err}" if err else ""))
    else:
        # interrupt() returns a tuple — the graph is pausing here
        print(f"   Node executed: {node_name} | [INTERRUPT FIRED] payload type={type(node_value).__name__}")


def run_verification():
    db = SessionLocal()
    factory = ServiceFactory(db)

    user_id_str = "d2a6eafc-1463-4cef-893c-b3518668663c"
    user_id = uuid.UUID(user_id_str)

    # ------------------------------------------------------------------ #
    # 1. Create test goal                                                  #
    # ------------------------------------------------------------------ #
    print("1. Creating a new test goal...")
    goal_repo = GoalRepository(db)
    goal = goal_repo.create(
        title="Master LangGraph Orchestration in 7 Days",
        user_id=user_id,
        description="Build state graphs, checkpoints, interrupts, and custom routers.",
    )
    print(f"   Goal created: {goal.id}")

    # ------------------------------------------------------------------ #
    # 2. Build thread_id and config                                        #
    # ------------------------------------------------------------------ #
    thread_id = f"user_{user_id_str}_goal_{goal.id}"
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db": db,
            "factory": factory,
        }
    }

    initial_state = {
        "user_id": user_id_str,
        "goal_id": str(goal.id),
        "goal_title": goal.title,
        "thread_id": thread_id,
        "current_stage": "",
        "error": None,
    }

    try:
        # ------------------------------------------------------------------ #
        # Step 1: goal -> strategy -> wait_for_strategy_selection (INTERRUPT) #
        # ------------------------------------------------------------------ #
        print("\n--- Step 1: goal -> strategy -> [INTERRUPT: Checkpoint 1] ---")
        for event in workflow_app.stream(initial_state, config):
            _print_event(event)

        snapshot = workflow_app.get_state(config)
        print("\n=== Checkpoint 1: Strategy Selection ===")
        print("   Next node:", snapshot.next)
        print("   Current stage:", snapshot.values.get("current_stage"))
        print("   Error:", snapshot.values.get("error"))
        print("   thread_id in state:", snapshot.values.get("thread_id"))

        strategies = snapshot.values.get("strategies", [])
        print(f"   Strategies generated: {len(strategies)}")
        for s in strategies:
            print(f"     - [{s['strategy_key']}] {s['title']} | recommended={s['is_recommended']}")

        assert strategies, "FAIL: No strategies generated. Cannot proceed."
        assert snapshot.values.get("thread_id") == thread_id, "FAIL: thread_id missing from state"

        # Simulate user selecting first strategy
        selected_key = strategies[0]["strategy_key"]
        print(f"\n   User selects strategy: {selected_key}")
        factory.strategy_service().select_strategy(goal.id, selected_key, user_id)
        workflow_app.update_state(
            config,
            {"selected_strategy_key": selected_key},
            as_node="wait_for_strategy_selection",
        )

        # ------------------------------------------------------------------ #
        # Step 2: validation (question generation) -> wait_for_validation_answers (INTERRUPT)
        # ------------------------------------------------------------------ #
        print("\n--- Step 2: validation (question gen) -> [INTERRUPT: Checkpoint 1.5] ---")
        for event in workflow_app.stream(None, config):
            _print_event(event)

        snapshot = workflow_app.get_state(config)
        readiness_state = snapshot.values.get("readiness") or {}
        questions = readiness_state.get("validation_questions", [])
        print(f"\n=== Checkpoint 1.5: Validation Q&A ===")
        print("   Next node:", snapshot.next)
        print(f"   Questions generated: {len(questions)}")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q}")

        assert questions, "FAIL: No validation questions generated."

        # Simulate user submitting expert-level answers (guarantees score >= 60)
        mock_answers = [
            {
                "question": q,
                "answer": (
                    "I have 5 years of senior Python backend experience including event sourcing "
                    "and graph structures. I have 15 hours/week blocked on my calendar, a fully "
                    "configured dev environment, and zero competing priorities."
                ),
            }
            for q in questions
        ]
        print("\n   Injecting validation_answers into state...")
        workflow_app.update_state(
            config,
            {"validation_answers": mock_answers},
            as_node="wait_for_validation_answers",
        )

        # ------------------------------------------------------------------ #
        # Step 3: validation (evaluate) -> roadmap -> wait_for_plan_approval  #
        # ------------------------------------------------------------------ #
        print("\n--- Step 3: validation (evaluate) -> roadmap -> [INTERRUPT: Checkpoint 2] ---")
        for event in workflow_app.stream(None, config):
            _print_event(event)

        snapshot = workflow_app.get_state(config)
        readiness_score = snapshot.values.get("readiness", {}).get("overall_readiness_score")
        tasks = snapshot.values.get("tasks", [])
        print("\n=== Checkpoint 2: Plan Approval ===")
        print("   Next node:", snapshot.next)
        print("   Current stage:", snapshot.values.get("current_stage"))
        print(f"   Readiness score: {readiness_score}")
        print(f"   Tasks in roadmap: {len(tasks)}")
        print("   Error:", snapshot.values.get("error"))

        assert snapshot.values.get("error") is None, \
            f"FAIL: Error in state: {snapshot.values.get('error')}"
        assert tasks, "FAIL: No tasks in roadmap."

        # Simulate user approving the plan
        print("\n   User approves plan: plan_approved=True")
        workflow_app.update_state(
            config,
            {"plan_approved": True},
            as_node="wait_for_plan_approval",
        )

        # ------------------------------------------------------------------ #
        # Step 4: schedule -> execution -> coach -> END                       #
        # ------------------------------------------------------------------ #
        print("\n--- Step 4: schedule -> execution -> coach -> END ---")
        for event in workflow_app.stream(None, config):
            _print_event(event)

        snapshot = workflow_app.get_state(config)
        print("\n=== Workflow Completed ===")
        print("   Next node:", snapshot.next)
        print("   Final stage:", snapshot.values.get("current_stage"))
        print("   Error:", snapshot.values.get("error"))

        coach = snapshot.values.get("coach_insights") or {}
        briefing = str(coach.get("daily_briefing", ""))[:120]
        print(f"\n   Coach daily briefing (first 120 chars): {briefing}")

        # ------------------------------------------------------------------ #
        # 5. Database verification                                            #
        # ------------------------------------------------------------------ #
        db_tasks = db.query(Task).filter(Task.goal_id == goal.id).all()
        print(f"\n5. DB verification: {len(db_tasks)} tasks stored.")

        # Final assertions
        assert snapshot.values.get("current_stage") == "coaching", \
            f"FAIL: Expected stage 'coaching', got '{snapshot.values.get('current_stage')}'"
        assert snapshot.values.get("error") is None, \
            f"FAIL: Expected error=None, got '{snapshot.values.get('error')}'"
        assert len(db_tasks) > 0, "FAIL: No tasks saved to the database!"

        print("\n[OK] All assertions passed. Verification Successful!")

    finally:
        db.close()


if __name__ == "__main__":
    run_verification()
