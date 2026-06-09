import uuid
import json
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.providers.base_provider import BaseProvider
from app.utils.prompts import (
    get_strategy_validation_questions_prompt,
    get_strategy_readiness_evaluation_prompt
)

class ValidationService:
    def __init__(
        self,
        user_repository: UserRepository,
        goal_repository: GoalRepository,
        strategy_repository: StrategyRepository,
        provider: BaseProvider
    ):
        self.user_repository = user_repository
        self.goal_repository = goal_repository
        self.strategy_repository = strategy_repository
        self.provider = provider

    def generate_validation_questions(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Generates 3 strategy alignment validation questions.
        """
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found.")
            
        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "weekly_hours_available": float(profile.weekly_hours_available),
            "biggest_challenge": profile.biggest_challenge
        }

        goal = self.goal_repository.get_by_id(goal_id, user_id)
        if not goal:
            raise ValueError("Goal not found.")

        ctx = self.goal_repository.get_context(goal_id)
        goal_context_dict = {
            "goal": goal.title,
            "category": ctx.category if ctx else None,
            "difficulty": ctx.difficulty if ctx else None,
            "qa_context": ctx.qa_context if ctx else []
        }

        selected_strat = self.strategy_repository.get_selected(goal_id)
        # Fallback: if no strategy is explicitly selected, use the first available
        if not selected_strat:
            all_strats = self.strategy_repository.get_all_by_goal(goal_id)
            if not all_strats:
                raise ValueError("No strategies found for this goal. Please complete the strategy selection step first.")
            selected_strat = all_strats[0]

        strat_dict = {
            "strategy_key": selected_strat.strategy_key,
            "title": selected_strat.title,
            "description": selected_strat.description
        }

        prompt = get_strategy_validation_questions_prompt(profile_data, goal_context_dict, strat_dict)
        raw_response = self.provider.generate(prompt=prompt, json_mode=True)
        result = json.loads(raw_response)

        return {
            "validation_questions": result.get("validation_questions", [])
        }

    def evaluate_readiness(self, goal_id: uuid.UUID, user_id: uuid.UUID, qa_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Grades answers and computes overall readiness and gaps analysis.
        """
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found.")
            
        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "weekly_hours_available": float(profile.weekly_hours_available),
            "biggest_challenge": profile.biggest_challenge
        }

        goal = self.goal_repository.get_by_id(goal_id, user_id)
        ctx = self.goal_repository.get_context(goal_id)
        goal_context_dict = {
            "goal": goal.title,
            "category": ctx.category if ctx else None,
            "difficulty": ctx.difficulty if ctx else None,
            "qa_context": ctx.qa_context if ctx else []
        }

        selected_strat = self.strategy_repository.get_selected(goal_id)
        # Fallback: if no strategy is explicitly selected, use the first available
        if not selected_strat:
            all_strats = self.strategy_repository.get_all_by_goal(goal_id)
            if not all_strats:
                raise ValueError("No strategies found for this goal. Please complete the strategy selection step first.")
            selected_strat = all_strats[0]

        strat_dict = {
            "strategy_key": selected_strat.strategy_key,
            "title": selected_strat.title,
            "description": selected_strat.description
        }

        prompt = get_strategy_readiness_evaluation_prompt(profile_data, goal_context_dict, strat_dict, qa_list)
        raw_response = self.provider.generate(prompt=prompt, json_mode=True)
        readiness_res = json.loads(raw_response)

        score = readiness_res.get("overall_readiness_score", 80)
        dim_scores = readiness_res.get("dimension_scores", {"skills": 80, "resources": 80, "time": 80})
        gaps = readiness_res.get("identified_gaps", [])
        steps = readiness_res.get("remediation_steps", [])

        # Persist to database
        self.strategy_repository.save_readiness_analysis(
            goal_id=goal_id,
            overall_score=score,
            dimension_scores=dim_scores,
            identified_gaps=gaps,
            remediation_steps=steps,
            analysis_json=readiness_res
        )
        
        self.goal_repository.update_status(goal_id, "readiness_check", user_id)
        
        # Log event tracking
        self.goal_repository.log_goal_event(
            goal_id=goal_id,
            event_type="readiness_evaluated",
            payload=readiness_res
        )

        return {
            "overall_readiness_score": score,
            "dimension_scores": dim_scores,
            "identified_gaps": gaps,
            "remediation_steps": steps
        }
