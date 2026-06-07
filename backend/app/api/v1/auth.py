import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from app.database.session import get_db
from app.repositories import user_repo
from app.security.jwt_handler import create_access_token, create_refresh_token
from app.security.hashing import verify_password
from app.api.deps import get_current_user
from app.models.models import User
from app.config import settings

router = APIRouter()

# ==========================================
# Schema Definitions
# ==========================================
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

# ==========================================
# Authentication Endpoints
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    """
    db_user = user_repo.get_user_by_email(db, data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered."
        )
    user = user_repo.create_user(db, data.email, data.password)
    return user

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Exchanges credentials (username/password) for access and refresh tokens.
    """
    user = user_repo.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Gets the current active user details.
    """
    return current_user

# ==========================================
# Profile/Onboarding Endpoints
# ==========================================

@router.post("/profile", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates or updates the user onboarding profile characteristics.
    """
    profile = user_repo.create_or_update_profile(
        db=db,
        user_id=current_user.id,
        role=data.role,
        work_style=data.work_style,
        weekly_hours=data.weekly_hours_available,
        biggest_challenge=data.biggest_challenge,
        full_name=data.full_name
    )
    return profile

@router.get("/profile", response_model=ProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the user's active profile metadata.
    """
    profile = user_repo.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile onboarding not completed."
        )
    return profile
