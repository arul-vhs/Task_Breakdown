import uuid
import json
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.progress_repository import ProgressRepository
from app.providers.base_provider import BaseProvider
from app.services.scheduler_engine import scheduler_engine
from app.utils.prompts import get_adaptive_replanning_prompt

class ReplanningService:
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

    def generate_replan_preview(
        self,
        goal_id: uuid.UUID,
        user_id: uuid.UUID,
        new_hours_per_week: float,
        replanning_mode: str
    ) -> Dict[str, Any]:
        """
        Computes a forecast preview comparing previous metrics to proposed adjustments via Gemini.
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
        
        # Get roadmap DAG details
        if goal.execution_plan and goal.execution_plan.roadmap_json:
            roadmap_dag_data = goal.execution_plan.roadmap_json
        else:
            total_phases = goal.execution_plan.total_phases if goal.execution_plan else 0
            roadmap_dag_data = {"phases": [{"phase_number": i, "name": f"Phase {i}", "tasks": []} for i in range(1, total_phases + 1)]}
        
        sched = self.schedule_repository.get_active(goal_id)
        schedule_data = {
            "weekly_schedule": sched.weekly_schedule if sched else [],
            "daily_schedule": sched.daily_schedule if sched else []
        }

        progress = self.progress_metrics(goal_id, user_id)
        
        coach = self.progress_repository.get_coach_insights(goal_id)
        coach_insights = {
            "risk_level": coach.risk_level if coach else "Low",
            "coaching_summary": coach.coaching_summary if coach else ""
        }

        # 3. Print parameter details
        print("[ReplanningService] Invoking get_adaptive_replanning_prompt with parameters:")
        print(f"  - profile_data: type={type(profile_data)}, value={profile_data}")
        print(f"  - goal_context: type={type(goal_context_dict)}, value={goal_context_dict}")
        print(f"  - selected_strategy: type={type(selected_strat)}, value={selected_strat}")
        print(f"  - readiness_results: type={type(readiness)}, value={readiness}")
        print(f"  - roadmap_dag_data: type={type(roadmap_dag_data)}, value={roadmap_dag_data}")
        print(f"  - schedule_data: type={type(schedule_data)}, value={schedule_data}")
        print(f"  - progress_metrics: type={type(progress)}, value={progress}")
        print(f"  - coach_insights: type={type(coach_insights)}, value={coach_insights}")
        print(f"  - new_hours_per_week: type={type(new_hours_per_week)}, value={new_hours_per_week}")
        print(f"  - replanning_mode: type={type(replanning_mode)}, value={replanning_mode}")

        # 5. Use named keyword arguments
        prompt = get_adaptive_replanning_prompt(
            profile_data=profile_data,
            goal_context=goal_context_dict,
            selected_strategy=selected_strat,
            readiness_results=readiness,
            roadmap_dag_data=roadmap_dag_data,
            schedule_data=schedule_data,
            progress_metrics=progress,
            coach_insights=coach_insights,
            new_hours_per_week=new_hours_per_week,
            replanning_mode=replanning_mode
        )

        raw_response = self.provider.generate(prompt=prompt, json_mode=True)
        replanned_res = json.loads(raw_response)

        return {
            "replanning_mode": replanning_mode,
            "new_hours_per_week": new_hours_per_week,
            "roadmap_health_score": replanned_res.get("roadmap_health_score", 80),
            "completion_probability": replanned_res.get("completion_probability", 80),
            "goal_completion_forecast": replanned_res.get("goal_completion_forecast", "Adjusted timeline"),
            "risk_analysis": replanned_res.get("risk_analysis", ""),
            "recommended_adjustments": replanned_res.get("recommended_adjustments", []),
            "replanned_weekly_schedule": replanned_res.get("replanned_weekly_schedule", [])
        }

    def apply_replan(
        self,
        goal_id: uuid.UUID,
        user_id: uuid.UUID,
        new_hours_per_week: float,
        replanning_mode: str
    ) -> Dict[str, Any]:
        """
        Updates profile constraints, recalculates timelines, bumps schedule version snapshot,
        records reflections, logs replanning history, and triggers analytics events.
        """
        profile = self.user_repository.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found.")
            
        # 1. Update Profile Hours Constraint
        profile.weekly_hours_available = new_hours_per_week
        self.user_repository.db.commit()

        # 2. Reload Tasks and Dependencies
        db_tasks = self.goal_repository.get_tasks(goal_id)
        tasks_list = [
            {
                "phase_number": t.phase_number,
                "phase_name": t.phase_name,
                "task_id_alias": t.task_id_alias,
                "name": t.name,
                "allocated_hours": float(t.allocated_hours)
            } for t in db_tasks
        ]

        db_deps = self.goal_repository.get_task_dependencies(goal_id)
        deps_list = [
            {
                "task_id_alias": d.task_id_alias,
                "depends_on_alias": d.depends_on_alias
            } for d in db_deps
        ]

        profile_data = {
            "role": profile.role,
            "work_style": profile.work_style,
            "weekly_hours_available": float(new_hours_per_week),
            "biggest_challenge": profile.biggest_challenge
        }

        # 3. Recalculate Calendar Timeline locally
        sched_res = scheduler_engine.calculate_schedule(tasks_list, deps_list, profile_data)
        analysis = sched_res["schedule_analysis"]

        # 4. Save new active schedule
        self.schedule_repository.save_active_schedule(
            goal_id=goal_id,
            confidence=analysis["confidence_score"],
            forecast=analysis["goal_completion_forecast"],
            buffer_desc=analysis["buffer_time_allocation"],
            feasibility=analysis["deadline_feasibility_analysis"],
            weekly_schedule=sched_res["weekly_schedule"],
            daily_schedule=sched_res["daily_schedule"]
        )

        # 5. Increment versioning snapshot
        versions_count = len(self.schedule_repository.get_versions(goal_id))
        new_version_num = versions_count + 1

        self.schedule_repository.create_version(
            goal_id=goal_id,
            version=new_version_num,
            name=f"{replanning_mode} Replan",
            weekly=sched_res["weekly_schedule"],
            daily=sched_res["daily_schedule"],
            reason=f"Rescheduled under mode {replanning_mode} with capacity {new_hours_per_week}h/week"
        )

        # 6. Save Reflection history entry
        self.progress_repository.save_reflection(
            goal_id=goal_id,
            reflection=f"Rescheduled goal timeline to version {new_version_num}.",
            adjustments=[f"Set availability limit to {new_hours_per_week}h/week."],
            quote="Progress is adjustment. Stay focused."
        )

        # 7. Log Replanning history details
        self.progress_repository.save_replanning_history(
            goal_id=goal_id,
            mode=replanning_mode,
            hours=new_hours_per_week,
            risks=analysis["deadline_feasibility_analysis"],
            adjustments=[f"Adjusted weekly hours to {new_hours_per_week}"],
            old_plan=None,  # Optionally snapshot previous schedule if required
            new_plan=sched_res,
            reason=f"Rescheduled under mode {replanning_mode}"
        )

        # 8. Log schedule change events (Event Sourcing)
        self.schedule_repository.log_schedule_event(
            goal_id=goal_id,
            event_type="schedule_replanned",
            payload={"version": new_version_num, "mode": replanning_mode, "hours": new_hours_per_week}
        )

        # 9. Log analytics events
        self.progress_repository.log_analytics_event(
            user_id=user_id,
            event_type="schedule_replanned",
            properties={"goal_id": str(goal_id), "version": new_version_num}
        )

        return {
            "status": "applied",
            "current_version": new_version_num,
            "schedule": sched_res
        }

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
