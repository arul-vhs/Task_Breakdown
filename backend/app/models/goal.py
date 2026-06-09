import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Text, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft", nullable=False)  # draft, strat_selection, readiness_check, planning, active, paused, completed
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    goal_context = relationship("GoalContext", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="goal", cascade="all, delete-orphan")
    readiness_analysis = relationship("ReadinessAnalysis", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    execution_plan = relationship("ExecutionPlan", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    schedule = relationship("Schedule", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    schedule_versions = relationship("ScheduleVersion", back_populates="goal", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="goal", cascade="all, delete-orphan")
    coach_insight = relationship("CoachInsight", back_populates="goal", uselist=False, cascade="all, delete-orphan")
    replanning_history = relationship("ReplanningHistory", back_populates="goal", cascade="all, delete-orphan")
    goal_events = relationship("GoalEvent", back_populates="goal", cascade="all, delete-orphan")
    task_events = relationship("TaskEvent", back_populates="goal", cascade="all, delete-orphan")
    schedule_events = relationship("ScheduleEvent", back_populates="goal", cascade="all, delete-orphan")


class GoalContext(Base):
    __tablename__ = "goal_context"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Combined for compatibility: direct columns + JSON blob compatibility
    category = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)  # Beginner, Intermediate, Advanced
    estimated_duration = Column(String(100), nullable=True)
    required_skills = Column(JSON, default=[], nullable=False)
    risks = Column(JSON, default=[], nullable=False)
    qa_context = Column(JSON, default=[], nullable=False)  # [{"question": "", "answer": ""}]
    context_json = Column(JSON, nullable=True)  # Aggregated field for target design compatibility
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="goal_context")
