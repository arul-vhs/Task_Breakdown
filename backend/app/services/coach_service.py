import uuid
import json
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.progress_repository import ProgressRepository
from app.providers.base_provider import BaseProvider
from app.utils.prompts import (
    get_coaching_briefing_prompt,
    get_coaching_chat_prompt
)

class CoachService:
    def __init__(
        self,
        user_repository: UserRepository,
        goal_repository: GoalRepository,
        schedule_repository: ScheduleRepository,
        progress_repository: ProgressRepository,
        provider: BaseProvider
    ):
        self.user_repository = user_repository
        self.goal_repository = goal_repository
        self.schedule_repository = schedule_repository
        self.progress_repository = progress_repository
        self.provider = provider

    def generate_daily_coaching_insights(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Gathers telemetry, reflections, and schedules to compute daily risk factor ratings and action instructions.
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
            "difficulty": ctx.difficulty if ctx else None
        }

        selected_strat = self.db_selected_strategy(goal_id)
        readiness = self.db_readiness(goal_id)
        roadmap = {"phases": goal.execution_plan.total_phases if goal.execution_plan else 0}
        
        sched = self.schedule_repository.get_active(goal_id)
        schedule_data = {
            "weekly_schedule": sched.weekly_schedule if sched else [],
            "daily_schedule": sched.daily_schedule if sched else []
        }

        progress = self.progress_metrics(goal_id, user_id)
        reflections = [{"reflection": r.reflection, "quote": r.encouragement_quote} for r in self.progress_repository.get_reflections(goal_id)]

        prompt = get_coaching_briefing_prompt(
            profile_data,
            goal_context_dict,
            selected_strat,
            readiness,
            roadmap,
            schedule_data,
            progress,
            reflections
        )
        
        raw_response = self.provider.generate(prompt=prompt, json_mode=True)
        coach_res = json.loads(raw_response)

        # Extract fields from the rich response to match database schema
        replanning_payload = coach_res.get("adaptive_replanning_payload", {})
        risk_level = str(replanning_payload.get("risk_level", "Low")).capitalize()
        
        risk_assessment = coach_res.get("risk_assessment", "")
        if isinstance(risk_assessment, str):
            critical_risks = [line.strip("- *").strip() for line in risk_assessment.split("\n") if line.strip()]
        else:
            critical_risks = risk_assessment or []
            
        rec_actions = coach_res.get("recommended_actions", [])
        if isinstance(rec_actions, str):
            action_items = [line.strip("- *").strip() for line in rec_actions.split("\n") if line.strip()]
        else:
            action_items = rec_actions or []
            
        daily_briefing = coach_res.get("daily_briefing", "")
        progress_analysis = coach_res.get("progress_analysis", "")
        coaching_summary = f"{daily_briefing}\n\n{progress_analysis}".strip()
        if not coaching_summary:
            coaching_summary = "Guidance complete."

        # Persist insights in database
        self.progress_repository.save_coach_insights(
            goal_id=goal_id,
            risk_level=risk_level,
            critical_risks=critical_risks,
            action_items=action_items,
            coaching_summary=coaching_summary
        )

        return coach_res

    def chat_with_coach(self, goal_id: uuid.UUID, user_id: uuid.UUID, message: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Conversational assistant chat thread execution.
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
            "difficulty": ctx.difficulty if ctx else None
        }

        selected_strat = self.db_selected_strategy(goal_id)
        readiness = self.db_readiness(goal_id)
        roadmap = {"phases": goal.execution_plan.total_phases if goal.execution_plan else 0}
        
        sched = self.schedule_repository.get_active(goal_id)
        schedule_data = {
            "weekly_schedule": sched.weekly_schedule if sched else [],
            "daily_schedule": sched.daily_schedule if sched else []
        }

        progress = self.progress_metrics(goal_id, user_id)
        reflections = [{"reflection": r.reflection, "quote": r.encouragement_quote} for r in self.progress_repository.get_reflections(goal_id)]

        prompt = get_coaching_chat_prompt(
            profile_data,
            goal_context_dict,
            selected_strat,
            readiness,
            roadmap,
            schedule_data,
            progress,
            reflections,
            chat_history + [{"role": "user", "content": message}]
        )

        # General text generation (not JSON forced)
        reply = self.provider.generate(prompt=prompt, json_mode=False)
        
        # Log analytics interaction
        self.progress_repository.log_analytics_event(
            user_id=user_id,
            event_type="coach_chat",
            properties={"goal_id": str(goal_id)}
        )
        
        return reply

    # Helper database readers
    def db_selected_strategy(self, goal_id: uuid.UUID) -> Dict[str, Any]:
        from app.models.strategy import Strategy
        strat = self.goal_repository.db.query(Strategy).filter(
            Strategy.goal_id == goal_id, Strategy.is_selected == True
        ).first()
        return {"strategy_key": strat.strategy_key, "title": strat.title} if strat else {}

    def db_readiness(self, goal_id: uuid.UUID) -> Dict[str, Any]:
        from app.models.strategy import ReadinessAnalysis
        readiness = self.goal_repository.db.query(ReadinessAnalysis).filter(ReadinessAnalysis.goal_id == goal_id).first()
        return readiness.__dict__ if readiness else {}

    def progress_metrics(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        from app.services.progress_engine import progress_engine
        return progress_engine.calculate_goal_metrics(
            db=self.goal_repository.db,
            goal_id=str(goal_id),
            user_id=str(user_id)
        )
