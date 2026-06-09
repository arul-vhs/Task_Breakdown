import uuid
from typing import Dict, Any, List
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.progress_engine import progress_engine

class ProgressService:
    def __init__(
        self,
        goal_repository: GoalRepository,
        progress_repository: ProgressRepository
    ):
        self.goal_repository = goal_repository
        self.progress_repository = progress_repository

    def toggle_task(
        self,
        goal_id: uuid.UUID,
        task_alias: str,
        is_completed: bool,
        time_spent: float,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Updates task completion check status, logs progress, and returns recalculated telemetry metrics.
        """
        task = self.progress_repository.update_task_completion(
            goal_id=goal_id,
            task_id_alias=task_alias,
            is_completed=is_completed,
            time_spent=time_spent,
            user_id=user_id
        )
        if not task:
            raise ValueError(f"Task alias {task_alias} not found under goal.")
            
        # Log event sourcing
        self.goal_repository.log_task_event(
            goal_id=goal_id,
            task_id=task.id,
            event_type="task_toggled",
            payload={"task_id_alias": task_alias, "is_completed": is_completed, "time_spent": time_spent}
        )
        
        # Log analytics aggregates
        self.progress_repository.log_analytics_event(
            user_id=user_id,
            event_type="task_completed" if is_completed else "task_uncompleted",
            properties={"goal_id": str(goal_id), "task_id_alias": task_alias}
        )
        
        # Recalculate and return metrics using progress engine
        metrics = self.get_progress_metrics(goal_id, user_id)
        
        # Update daily aggregates
        self.progress_repository.log_daily_activity(
            user_id=user_id,
            active_minutes=int(time_spent * 60) if is_completed else 0,
            actions_count=1
        )
        
        # Log streak history if changed
        streak = metrics["streak_count"]
        self.progress_repository.log_streak_history(user_id, streak)
        
        return {
            "task_id_alias": task_alias,
            "is_completed": task.is_completed,
            "time_spent": float(task.time_spent),
            "metrics": metrics
        }

    def get_progress_metrics(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Retrieves current progress aggregates.
        """
        return progress_engine.calculate_goal_metrics(
            db=self.progress_repository.db,
            goal_id=str(goal_id),
            user_id=str(user_id)
        )
