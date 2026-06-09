import datetime
import uuid
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.progress import ProgressLog

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
        
        # Streak calculations (done inline to prevent import conflicts with legacy models.models)
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        logs = db.query(ProgressLog.logged_date).filter(
            and_(ProgressLog.user_id == user_uuid, ProgressLog.action == "completed")
        ).distinct().order_by(ProgressLog.logged_date.desc()).all()
        
        streak = 0
        if logs:
            dates = [row[0] for row in logs]
            yesterday = today - datetime.timedelta(days=1)
            
            # Check if user did something today or yesterday to continue streak
            if dates[0] in (today, yesterday):
                streak = 1
                current_date = dates[0]
                for next_date in dates[1:]:
                    if current_date - next_date == datetime.timedelta(days=1):
                        streak += 1
                        current_date = next_date
                    else:
                        break
        
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
