import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    Date,
    UniqueConstraint,
    Index,
    JSON,
    UUID
)
from sqlalchemy.orm import relationship
import uuid
from app.database.session import Base

# 1. User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    progress_logs = relationship("ProgressLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

# 2. Profile Model
class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)  # Student, Founder, Working Professional, Freelancer, Job Seeker
    work_style = Column(String(50), nullable=False)  # Morning, Evening, Pomodoro, Deep Work
    weekly_hours_available = Column(Numeric(4, 1), default=10.0, nullable=False)
    biggest_challenge = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    user = relationship("User", back_populates="profile")

# 3. Goal Model
class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, strat_selection, readiness_check, planning, active, paused, completed
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
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

# 4. GoalContext Model
class GoalContext(Base):
    __tablename__ = "goal_context"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    category = Column(String(100))
    difficulty = Column(String(50))  # Beginner, Intermediate, Advanced
    estimated_duration = Column(String(100))
    required_skills = Column(JSON, default=[], nullable=False)
    risks = Column(JSON, default=[], nullable=False)
    qa_context = Column(JSON, default=[], nullable=False)  # [{"question": "", "answer": ""}]
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="goal_context")

# 5. Strategy Model
class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_key = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    pros = Column(JSON, default=[], nullable=False)
    cons = Column(JSON, default=[], nullable=False)
    is_recommended = Column(Boolean, default=False, nullable=False)
    is_selected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="strategies")

# 6. ReadinessAnalysis Model
class ReadinessAnalysis(Base):
    __tablename__ = "readiness_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_readiness_score = Column(Integer, nullable=False)
    dimension_scores = Column(JSON, nullable=False)  # {"skills": 80, "resources": 90, "time": 70}
    identified_gaps = Column(JSON, default=[], nullable=False)
    remediation_steps = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="readiness_analysis")

# 7. ExecutionPlan Model
class ExecutionPlan(Base):
    __tablename__ = "execution_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    blueprint_refinement = Column(String(50), default="Standard", nullable=False)  # Minimalist, Standard, Comprehensive
    total_phases = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="execution_plan")

# 8. Task Model
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_number = Column(Integer, nullable=False)
    phase_name = Column(String(255), nullable=False)
    task_id_alias = Column(String(50), nullable=False)  # e.g., T1, T2
    name = Column(String(255), nullable=False)
    description = Column(Text)
    allocated_hours = Column(Numeric(4, 1), default=1.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    time_spent = Column(Numeric(4, 1), default=0.0, nullable=False)
    due_date = Column(Date)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="tasks")
    progress_logs = relationship("ProgressLog", back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("goal_id", "task_id_alias", name="uq_goal_task_alias"),
    )

# 9. TaskDependency Model
class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    task_id_alias = Column(String(50), nullable=False)  # T2
    depends_on_alias = Column(String(50), nullable=False)  # T1
    
    __table_args__ = (
        Index('idx_task_deps_lookup', 'goal_id', 'task_id_alias'),
    )

# 10. Schedule Model
class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    confidence_score = Column(Integer, default=80, nullable=False)
    goal_completion_forecast = Column(Text)
    buffer_time_allocation = Column(Text)
    feasibility_audit = Column(Text)
    weekly_schedule = Column(JSON, default=[], nullable=False)
    daily_schedule = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="schedule")

# 11. ScheduleVersion Model
class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    weekly_schedule = Column(JSON, nullable=False)
    daily_schedule = Column(JSON, nullable=False)
    replan_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="schedule_versions")

# 12. ProgressLog Model
class ProgressLog(Base):
    __tablename__ = "progress_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # completed, uncompleted, time_logged
    time_delta = Column(Numeric(4, 1), default=0.0, nullable=False)
    logged_date = Column(Date, default=datetime.date.today, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    user = relationship("User", back_populates="progress_logs")
    task = relationship("Task", back_populates="progress_logs")

# 13. Reflection Model
class Reflection(Base):
    __tablename__ = "reflections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    reflection = Column(Text, nullable=False)
    suggested_adjustments = Column(JSON, default=[], nullable=False)
    encouragement_quote = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="reflections")

# 14. CoachInsight Model
class CoachInsight(Base):
    __tablename__ = "coach_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    risk_level = Column(String(50), default="Low", nullable=False)  # Low, Medium, High
    critical_risks = Column(JSON, default=[], nullable=False)
    action_items = Column(JSON, default=[], nullable=False)
    coaching_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="coach_insight")

# 15. ReplanningHistory Model
class ReplanningHistory(Base):
    __tablename__ = "replanning_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    replanning_mode = Column(String(50), nullable=False)  # Balanced, Catch Up, Low Stress, Aggressive
    new_hours_per_week = Column(Numeric(4, 1), nullable=False)
    risk_analysis = Column(Text, nullable=False)
    recommended_adjustments = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    goal = relationship("Goal", back_populates="replanning_history")

# 16. Notification Model
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    user = relationship("User", back_populates="notifications")

# 17. AuditLog Model
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    ip_address = Column(String(45))
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)
    
    user = relationship("User", back_populates="audit_logs")
