import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Numeric, Date, Integer, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class ProgressLog(Base):
    __tablename__ = "progress_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # completed, uncompleted, time_logged
    time_delta = Column(Numeric(4, 1), default=0.0, nullable=False)
    logged_date = Column(Date, default=datetime.date.today, nullable=False)
    
    # Target design compatibility fields
    completion_percent = Column(Integer, default=0, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="progress_logs")
    task = relationship("Task", back_populates="progress_logs")
