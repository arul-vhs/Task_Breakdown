import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID, Text, JSON, Integer
from sqlalchemy.orm import relationship
from app.database.session import Base

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
    strategy_json = Column(JSON, nullable=True)  # Target design compatibility
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="strategies")


class ReadinessAnalysis(Base):
    __tablename__ = "readiness_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_readiness_score = Column(Integer, nullable=False)
    dimension_scores = Column(JSON, nullable=False)  # {"skills": 80, "resources": 90, "time": 70}
    identified_gaps = Column(JSON, default=[], nullable=False)
    remediation_steps = Column(JSON, default=[], nullable=False)
    analysis_json = Column(JSON, nullable=True)  # Target design compatibility
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="readiness_analysis")
