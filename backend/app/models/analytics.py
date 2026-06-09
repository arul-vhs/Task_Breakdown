import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # goal_created, task_completed, screen_view, etc.
    properties = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analytics_events")


class DailyActivity(Base):
    __tablename__ = "daily_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False, index=True)
    active_minutes = Column(Integer, default=0, nullable=False)
    actions_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="daily_activities")


class StreakHistory(Base):
    __tablename__ = "streak_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    streak_count = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="streak_history")
