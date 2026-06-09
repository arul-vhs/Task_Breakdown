import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile
from app.security.password import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, password_plain: str) -> User:
        hashed_pwd = get_password_hash(password_plain)
        db_user = User(email=email, hashed_password=hashed_pwd)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_profile(self, user_id: uuid.UUID) -> Optional[Profile]:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def create_or_update_profile(
        self,
        user_id: uuid.UUID,
        role: str,
        work_style: str,
        weekly_hours: float,
        biggest_challenge: Optional[str] = None,
        full_name: Optional[str] = None,
        persona: Optional[str] = None,
        motivation_style: Optional[str] = None,
        risk_profile: Optional[str] = None
    ) -> Profile:
        profile = self.get_profile(user_id)
        if profile:
            profile.role = role
            profile.work_style = work_style
            profile.weekly_hours_available = weekly_hours
            if biggest_challenge is not None:
                profile.biggest_challenge = biggest_challenge
            if full_name is not None:
                profile.full_name = full_name
            if persona is not None:
                profile.persona = persona
            if motivation_style is not None:
                profile.motivation_style = motivation_style
            if risk_profile is not None:
                profile.risk_profile = risk_profile
        else:
            profile = Profile(
                user_id=user_id,
                role=role,
                work_style=work_style,
                weekly_hours_available=weekly_hours,
                biggest_challenge=biggest_challenge,
                full_name=full_name,
                persona=persona,
                motivation_style=motivation_style,
                risk_profile=risk_profile
            )
            self.db.add(profile)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
