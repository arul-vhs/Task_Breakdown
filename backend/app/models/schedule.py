import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Text, Integer, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    confidence_score = Column(Integer, default=80, nullable=False)
    goal_completion_forecast = Column(Text, nullable=True)
    buffer_time_allocation = Column(Text, nullable=True)
    feasibility_audit = Column(Text, nullable=True)
    weekly_schedule = Column(JSON, default=[], nullable=False)
    daily_schedule = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="schedule")


class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    weekly_schedule = Column(JSON, nullable=False)
    daily_schedule = Column(JSON, nullable=False)
    replan_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="schedule_versions")
