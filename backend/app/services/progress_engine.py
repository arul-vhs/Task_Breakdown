import datetime
from sqlalchemy.orm import Session
from app.models.models import Task, ProgressLog
from app.repositories import goal_repo

class ProgressEngine:
    def __init__(self):
        pass

    def calculate_goal_metrics(self, db: Session, goal_id: str, user_id: str) -> dict:
        """
        Calculates all project progress telemetry metrics locally.
        """
        # Fetch tasks
        tasks = db.query(Task).filter(Task.goal_id == goal_id).all()
        if not tasks:
            return {
                "total_tasks_count": 0,
                "completed_tasks_count": 0,
                "completion_percentage": 0.0,
                "health_score": 100,
                "overdue_tasks_count": 0,
                "overdue_tasks_names": [],
                "streak_count": 0,
                "time_spent_total": 0.0,
                "allocated_hours_total": 0.0
            }
            
        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.is_completed]
        completed_count = len(completed_tasks)
        
        # Calculate percentages
        completion_pct = round((completed_count / total_tasks) * 100, 1)
        
        # Overdue checks
        today = datetime.date.today()
        overdue_tasks = []
        for t in tasks:
            if not t.is_completed and t.due_date and t.due_date < today:
                overdue_tasks.append(t)
                
        overdue_count = len(overdue_tasks)
        overdue_names = [t.name for t in overdue_tasks]
        
        # Health calculation: starts at 100, drops by 10 per overdue task, bounded to 0-100
        health_score = max(0, 100 - (overdue_count * 10))
        
        # Streak calculations
        streak = goal_repo.get_streak_count(db, user_id)
        
        # Hours spent vs allocated
        time_spent_total = sum(float(t.time_spent) for t in tasks)
        allocated_hours_total = sum(float(t.allocated_hours) for t in tasks)
        
        return {
            "total_tasks_count": total_tasks,
            "completed_tasks_count": completed_count,
            "completion_percentage": completion_pct,
            "health_score": health_score,
            "overdue_tasks_count": overdue_count,
            "overdue_tasks_names": overdue_names,
            "streak_count": streak,
            "time_spent_total": round(time_spent_total, 1),
            "allocated_hours_total": round(allocated_hours_total, 1)
        }

progress_engine = ProgressEngine()
