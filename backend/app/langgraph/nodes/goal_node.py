import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.langgraph.state import GoalPilotState
from app.langgraph.constants import STAGE_GOAL_ANALYSIS

def goal_node(state: GoalPilotState, config: RunnableConfig) -> Dict[str, Any]:
    factory = config["configurable"]["factory"]
    service = factory.goal_service()
    
    goal_id = uuid.UUID(state["goal_id"])
    user_id = uuid.UUID(state["user_id"])
    
    try:
        res = service.analyze_goal_and_initialize_context(goal_id=goal_id, user_id=user_id)
        
        profile_db = service.user_repository.get_profile(user_id)
        profile_data = {
            "role": profile_db.role,
            "work_style": profile_db.work_style,
            "hours_per_week": float(profile_db.weekly_hours_available),
            "biggest_challenge": profile_db.biggest_challenge
        } if profile_db else {}
        
        return {
            "current_stage": STAGE_GOAL_ANALYSIS,
            "error": None,
            "profile": profile_data,
            "goal_context": {
                "category": res.get("category"),
                "difficulty": res.get("difficulty"),
                "estimated_duration": res.get("estimated_duration"),
                "required_skills": res.get("required_skills", []),
                "risks": res.get("risks", []),
                "qa_context": [{"question": q, "answer": ""} for q in res.get("questions", [])]
            }
        }
    except Exception as e:
        return {
            "current_stage": STAGE_GOAL_ANALYSIS,
            "error": str(e)
        }
