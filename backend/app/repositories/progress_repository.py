import uuid
import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.progress import ProgressLog
from app.models.reflection import Reflection, CoachInsight, ReplanningHistory
from app.models.analytics import AnalyticsEvent, DailyActivity, StreakHistory

class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_task_completion(
        self,
        goal_id: uuid.UUID,
        task_id_alias: str,
        is_completed: bool,
        time_spent: float,
        user_id: uuid.UUID
    ) -> Optional[Task]:
        from sqlalchemy import or_
        task = self.db.query(Task).filter(
            and_(
                Task.goal_id == goal_id,
                or_(
                    Task.task_id_alias == task_id_alias,
                    Task.name == task_id_alias,
                    Task.title == task_id_alias
                )
            )
        ).first()
        if task:
            task.is_completed = is_completed
            task.status = "completed" if is_completed else "pending"
            task.updated_at = datetime.datetime.utcnow()
            
            if is_completed:
                task.completed_at = datetime.datetime.utcnow()
                action = "completed"
            else:
                task.completed_at = None
                action = "uncompleted"
                
            time_delta = time_spent - float(task.time_spent)
            task.time_spent = time_spent
            
            # Log progress transaction
            progress_log = ProgressLog(
                user_id=user_id,
                goal_id=goal_id,
                task_id=task.id,
                action=action,
                time_delta=time_delta,
                logged_date=datetime.date.today()
            )
            self.db.add(progress_log)
            self.db.commit()
            self.db.refresh(task)
        return task

    def get_streak_count(self, user_id: uuid.UUID) -> int:
        logs = self.db.query(ProgressLog.logged_date).filter(
            and_(ProgressLog.user_id == user_id, ProgressLog.action == "completed")
        ).distinct().order_by(ProgressLog.logged_date.desc()).all()
        
        if not logs:
            return 0
            
        dates = [row[0] for row in logs]
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        # Check if user did something today or yesterday to continue streak
        if dates[0] not in (today, yesterday):
            return 0
            
        streak = 1
        current_date = dates[0]
        for next_date in dates[1:]:
            if current_date - next_date == datetime.timedelta(days=1):
                streak += 1
                current_date = next_date
            else:
                break
        return streak

    def save_reflection(self, goal_id: uuid.UUID, reflection: str, adjustments: List[str], quote: Optional[str] = None) -> Reflection:
        ref = Reflection(goal_id=goal_id, reflection=reflection, reflection_text=reflection, suggested_adjustments=adjustments, encouragement_quote=quote)
        self.db.add(ref)
        self.db.commit()
        self.db.refresh(ref)
        return ref

    def get_reflections(self, goal_id: uuid.UUID) -> List[Reflection]:
        return self.db.query(Reflection).filter(Reflection.goal_id == goal_id).order_by(Reflection.created_at.desc()).all()

    def save_coach_insights(
        self,
        goal_id: uuid.UUID,
        risk_level: str,
        critical_risks: List[str],
        action_items: List[str],
        coaching_summary: str
    ) -> CoachInsight:
        insight = self.db.query(CoachInsight).filter(CoachInsight.goal_id == goal_id).first()
        if insight:
            insight.risk_level = risk_level
            insight.critical_risks = critical_risks
            insight.action_items = action_items
            insight.coaching_summary = coaching_summary
        else:
            insight = CoachInsight(
                goal_id=goal_id,
                risk_level=risk_level,
                critical_risks=critical_risks,
                action_items=action_items,
                coaching_summary=coaching_summary
            )
            self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def get_coach_insights(self, goal_id: uuid.UUID) -> Optional[CoachInsight]:
        return self.db.query(CoachInsight).filter(CoachInsight.goal_id == goal_id).first()

    def save_replanning_history(
        self,
        goal_id: uuid.UUID,
        mode: str,
        hours: float,
        risks: str,
        adjustments: List[str],
        old_plan: Optional[Dict[str, Any]] = None,
        new_plan: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> ReplanningHistory:
        rep = ReplanningHistory(
            goal_id=goal_id,
            replanning_mode=mode,
            new_hours_per_week=hours,
            risk_analysis=risks,
            recommended_adjustments=adjustments,
            old_plan=old_plan,
            new_plan=new_plan,
            reason=reason
        )
        self.db.add(rep)
        self.db.commit()
        self.db.refresh(rep)
        return rep

    def log_analytics_event(self, user_id: uuid.UUID, event_type: str, properties: Dict[str, Any]) -> AnalyticsEvent:
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            properties=properties
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def log_daily_activity(self, user_id: uuid.UUID, active_minutes: int = 0, actions_count: int = 1) -> DailyActivity:
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        activity = self.db.query(DailyActivity).filter(
            and_(DailyActivity.user_id == user_id, DailyActivity.activity_date >= today_start)
        ).first()
        
        if activity:
            activity.active_minutes += active_minutes
            activity.actions_count += actions_count
        else:
            activity = DailyActivity(
                user_id=user_id,
                active_minutes=active_minutes,
                actions_count=actions_count
            )
            self.db.add(activity)
            
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def log_streak_history(self, user_id: uuid.UUID, streak_count: int, is_active: bool = True) -> StreakHistory:
        history = StreakHistory(
            user_id=user_id,
            streak_count=streak_count,
            is_active=is_active
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
