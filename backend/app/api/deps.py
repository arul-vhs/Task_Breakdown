from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.security.auth import get_current_user

# Keep these imports for any backend parts still referencing them
__all__ = ["get_db", "get_current_user"]
