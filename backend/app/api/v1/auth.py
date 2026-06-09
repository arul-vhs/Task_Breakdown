import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token, create_refresh_token
from app.security.password import verify_password
from app.security.auth import get_current_user
from app.models.user import User
from app.core.limiter import limiter
from app.core.logger import logger, update_log_context
from app.schemas.auth import (
    UserRegister,
    UserResponse,
    TokenResponse,
    ProfileUpdate,
    ProfileResponse
)

router = APIRouter()

# ==========================================
# Authentication Endpoints
# ==========================================

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user account (Signup).
    """
    update_log_context({"event": "user_signup_attempt", "email": data.email})
    logger.info(f"Attempting user signup for {data.email}")
    
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_email(data.email)
    if db_user:
        logger.warning(f"Signup failed: email {data.email} already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered."
        )
    user = user_repo.create(data.email, data.password)
    
    update_log_context({"event": "user_signup_success", "user_id": str(user.id)})
    logger.info(f"User signup successful: {user.id}")
    return user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticates username/password and yields Access/Refresh JWTs (Login).
    """
    update_log_context({"event": "user_login_attempt", "email": form_data.username})
    logger.info(f"Attempting user login for {form_data.username}")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    update_log_context({"event": "user_login_success", "user_id": str(user.id)})
    logger.info(f"User login successful: {user.id}")
    
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
# Legacy/Backward Compatibility Routes
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_legacy(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    return signup(request, data, db)

@router.post("/token", response_model=TokenResponse)
def login_legacy(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    return login(request, db, form_data)

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
    user_repo = UserRepository(db)
    profile = user_repo.create_or_update_profile(
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
    user_repo = UserRepository(db)
    profile = user_repo.get_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile onboarding not completed."
        )
    return profile
