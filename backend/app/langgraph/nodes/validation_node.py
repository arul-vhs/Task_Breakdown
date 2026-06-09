import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_VALIDATION


def validation_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.validation_service()

    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])

    # Read answers from the explicit state field populated at Checkpoint 1.5.
    # Falls back to readiness["answers"] for backward compatibility.
    answers = (
        state.get("validation_answers")
        or (state.get("readiness") or {}).get("answers")
        or []
    )

    try:
        if answers:
            # Evaluate mode — answers have been submitted
            res = service.evaluate_readiness(goal_id=goal_id, user_id=user_id, qa_list=answers)
            return {
                "current_stage": STAGE_VALIDATION,
                "error": None,
                "readiness": {
                    "answers": answers,
                    "overall_readiness_score": res.get("overall_readiness_score"),
                    "dimension_scores": res.get("dimension_scores"),
                    "identified_gaps": res.get("identified_gaps"),
                    "remediation_steps": res.get("remediation_steps"),
                },
            }
        else:
            # Question generation mode — no answers yet
            res = service.generate_validation_questions(goal_id=goal_id, user_id=user_id)
            return {
                "current_stage": STAGE_VALIDATION,
                "error": None,
                "readiness": {
                    "validation_questions": res.get("validation_questions", []),
                    "answers": [],
                },
            }
    except Exception as e:
        return {
            "current_stage": STAGE_VALIDATION,
            "error": str(e),
        }

