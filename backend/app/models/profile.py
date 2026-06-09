import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Numeric, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)  # Student, Founder, Working Professional, Freelancer, Job Seeker
    persona = Column(String(100), nullable=True)  # beginner, intermediate, advanced
    work_style = Column(String(50), nullable=False)  # Morning, Evening, Pomodoro, Deep Work
    motivation_style = Column(String(50), nullable=True)
    risk_profile = Column(String(50), nullable=True)
    weekly_hours_available = Column(Numeric(4, 1), default=10.0, nullable=False)
    biggest_challenge = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="profile")
