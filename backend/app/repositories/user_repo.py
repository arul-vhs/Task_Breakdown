from sqlalchemy.orm import Session
from app.models.models import User, Profile
from app.security.hashing import get_password_hash
import uuid

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, password_plain: str) -> User:
    hashed_pwd = get_password_hash(password_plain)
    db_user = User(email=email, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_profile(db: Session, user_id: uuid.UUID) -> Profile:
    return db.query(Profile).filter(Profile.user_id == user_id).first()

def create_or_update_profile(
    db: Session,
    user_id: uuid.UUID,
    role: str,
    work_style: str,
    weekly_hours: float,
    biggest_challenge: str = None,
    full_name: str = None
) -> Profile:
    profile = get_profile(db, user_id)
    if profile:
        profile.role = role
        profile.work_style = work_style
        profile.weekly_hours_available = weekly_hours
        if biggest_challenge is not None:
            profile.biggest_challenge = biggest_challenge
        if full_name is not None:
            profile.full_name = full_name
    else:
        profile = Profile(
            user_id=user_id,
            role=role,
            work_style=work_style,
            weekly_hours_available=weekly_hours,
            biggest_challenge=biggest_challenge,
            full_name=full_name
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile
