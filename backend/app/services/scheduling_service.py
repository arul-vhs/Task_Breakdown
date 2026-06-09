import uuid
import datetime
from typing import Dict, Any, List, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.services.scheduler_engine import scheduler_engine

class SchedulingService:
    def __init__(
        self,
        user_repository: UserRepository,
        goal_repository: GoalRepository,
        schedule_repository: ScheduleRepository
    ):
        self.user_repository = user_repository
        self.goal_repository = goal_repository
        self.schedule_repository = schedule_repository

    def generate_active_schedule(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Calculates and persists a daily/weekly schedule calendar, updates task due dates,
        and saves version 1 of the schedule history records.
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

        # Calculate deterministic schedule using the SchedulerEngine
        sched_res = scheduler_engine.calculate_schedule(tasks_list, deps_list, profile_data)
        analysis = sched_res["schedule_analysis"]

        # Persist schedule parameters
        self.schedule_repository.save_active_schedule(
            goal_id=goal_id,
            confidence=analysis["confidence_score"],
            forecast=analysis["goal_completion_forecast"],
            buffer_desc=analysis["buffer_time_allocation"],
            feasibility=analysis["deadline_feasibility_analysis"],
            weekly_schedule=sched_res["weekly_schedule"],
            daily_schedule=sched_res["daily_schedule"]
        )

        # Create Version 1 Schedule Snapshot
        self.schedule_repository.create_version(
            goal_id=goal_id,
            version=1,
            name="Original Schedule",
            weekly=sched_res["weekly_schedule"],
            daily=sched_res["daily_schedule"]
        )

        # Recalculate tasks due dates based on schedule calendar blocks
        task_due_dates = {}
        for day in sched_res["daily_schedule"]:
            w_num = day["week_number"]
            target_date = datetime.date.today() + datetime.timedelta(weeks=int(w_num)-1)
            for block in day["time_blocks"]:
                t_alias = block["task_id"]
                task_due_dates[t_alias] = target_date

        for t in db_tasks:
            if t.task_id_alias in task_due_dates:
                t.due_date = task_due_dates[t.task_id_alias]
                
        self.goal_repository.db.commit()
        self.goal_repository.update_status(goal_id, "active", user_id)
        
        # Log event tracking
        self.schedule_repository.log_schedule_event(
            goal_id=goal_id,
            event_type="schedule_generated",
            payload={"version": 1, "confidence": analysis["confidence_score"]}
        )

        return sched_res
