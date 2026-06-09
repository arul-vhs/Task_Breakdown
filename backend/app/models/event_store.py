import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, JSON, Integer
from sqlalchemy.orm import relationship
from app.database.session import Base

class GoalEvent(Base):
    __tablename__ = "goal_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # goal_created, goal_status_changed, etc.
    event_payload = Column(JSON, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="goal_events")


class TaskEvent(Base):
    __tablename__ = "task_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(100), nullable=False)  # task_created, task_completed, task_reassigned
    event_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="task_events")


class ScheduleEvent(Base):
    __tablename__ = "schedule_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # schedule_created, schedule_version_bumped
    event_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="schedule_events")
