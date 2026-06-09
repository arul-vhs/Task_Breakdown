import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID, Text, Numeric, Integer, Date, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class ExecutionPlan(Base):
    __tablename__ = "execution_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    blueprint_refinement = Column(String(50), default="Standard", nullable=False)  # Minimalist, Standard, Comprehensive
    total_phases = Column(Integer, default=1, nullable=False)
    roadmap_json = Column(JSON, nullable=True)  # Target design compatibility
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="execution_plan")


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_number = Column(Integer, nullable=False)
    phase_name = Column(String(255), nullable=False)
    task_id_alias = Column(String(50), nullable=False)  # e.g., T1, T2
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)  # Target design compatibility
    description = Column(Text, nullable=True)
    allocated_hours = Column(Numeric(4, 1), default=1.0, nullable=False)
    estimated_hours = Column(Numeric(4, 1), default=1.0, nullable=True)  # Target design compatibility
    is_completed = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="pending", nullable=True)  # Target design compatibility (pending, completed, in_progress)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Numeric(4, 1), default=0.0, nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="tasks")
    progress_logs = relationship("ProgressLog", back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("goal_id", "task_id_alias", name="uq_goal_task_alias"),
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    task_id_alias = Column(String(50), nullable=False)  # T2
    depends_on_alias = Column(String(50), nullable=False)  # T1
    
    __table_args__ = (
        Index('idx_task_deps_lookup', 'goal_id', 'task_id_alias'),
    )
