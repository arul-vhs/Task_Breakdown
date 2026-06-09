import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from app.database.session import Base

class Reflection(Base):
    __tablename__ = "reflections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    reflection = Column(Text, nullable=False)
    reflection_text = Column(Text, nullable=True)  # Target design compatibility
    suggested_adjustments = Column(JSON, default=[], nullable=False)
    encouragement_quote = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="reflections")


class CoachInsight(Base):
    __tablename__ = "coach_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    risk_level = Column(String(50), default="Low", nullable=False)  # Low, Medium, High
    critical_risks = Column(JSON, default=[], nullable=False)
    action_items = Column(JSON, default=[], nullable=False)
    coaching_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="coach_insight")


class ReplanningHistory(Base):
    __tablename__ = "replanning_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    replanning_mode = Column(String(50), nullable=True)  # Balanced, Catch Up, Low Stress, Aggressive
    new_hours_per_week = Column(Numeric(4, 1), nullable=True)
    risk_analysis = Column(Text, nullable=True)
    recommended_adjustments = Column(JSON, nullable=True)
    
    # Target design compatibility fields
    old_plan = Column(JSON, nullable=True)
    new_plan = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="replanning_history")
