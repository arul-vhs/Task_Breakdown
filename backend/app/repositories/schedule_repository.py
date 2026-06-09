import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.schedule import Schedule, ScheduleVersion
from app.models.event_store import ScheduleEvent

class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_active_schedule(
        self,
        goal_id: uuid.UUID,
        confidence: int,
        forecast: str,
        buffer_desc: str,
        feasibility: str,
        weekly_schedule: List[Any],
        daily_schedule: List[Any]
    ) -> Schedule:
        sched = self.db.query(Schedule).filter(Schedule.goal_id == goal_id).first()
        if sched:
            sched.confidence_score = confidence
            sched.goal_completion_forecast = forecast
            sched.buffer_time_allocation = buffer_desc
            sched.feasibility_audit = feasibility
            sched.weekly_schedule = weekly_schedule
            sched.daily_schedule = daily_schedule
        else:
            sched = Schedule(
                goal_id=goal_id,
                confidence_score=confidence,
                goal_completion_forecast=forecast,
                buffer_time_allocation=buffer_desc,
                feasibility_audit=feasibility,
                weekly_schedule=weekly_schedule,
                daily_schedule=daily_schedule
            )
            self.db.add(sched)
        self.db.commit()
        self.db.refresh(sched)
        return sched

    def get_active(self, goal_id: uuid.UUID) -> Optional[Schedule]:
        return self.db.query(Schedule).filter(Schedule.goal_id == goal_id).first()

    def create_version(
        self,
        goal_id: uuid.UUID,
        version: int,
        name: str,
        weekly: List[Any],
        daily: List[Any],
        reason: Optional[str] = None
    ) -> ScheduleVersion:
        sv = ScheduleVersion(
            goal_id=goal_id,
            version_number=version,
            name=name,
            weekly_schedule=weekly,
            daily_schedule=daily,
            replan_reason=reason
        )
        self.db.add(sv)
        self.db.commit()
        self.db.refresh(sv)
        return sv

    def get_versions(self, goal_id: uuid.UUID) -> List[ScheduleVersion]:
        return self.db.query(ScheduleVersion).filter(ScheduleVersion.goal_id == goal_id).order_by(ScheduleVersion.version_number.desc()).all()

    def log_schedule_event(self, goal_id: uuid.UUID, event_type: str, payload: Dict[str, Any]) -> ScheduleEvent:
        event = ScheduleEvent(
            goal_id=goal_id,
            event_type=event_type,
            event_payload=payload
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
