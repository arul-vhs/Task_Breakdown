import uuid
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ProfileUpdate(BaseModel):
    role: str = Field(..., description="Student, Founder, Working Professional, Freelancer, Job Seeker")
    work_style: str = Field(..., description="Morning, Evening, Pomodoro, Deep Work")
    weekly_hours_available: float = Field(..., ge=1.0, le=168.0)
    biggest_challenge: str = None
    full_name: str = None

class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    work_style: str
    weekly_hours_available: float
    biggest_challenge: str = None
    full_name: str = None

    class Config:
        from_attributes = True
