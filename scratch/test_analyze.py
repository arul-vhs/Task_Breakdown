from app.core.database import get_supabase
from app.core.security import create_access_token
from app.core.logging import get_logger
from app.schemas import SignUpRequest, LoginRequest, TokenResponse
from fastapi import HTTPException
import bcrypt
import uuid

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    # bcrypt requires password <= 72 bytes — truncate safely
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))


class AuthService:
    def __init__(self):
        self.db = get_supabase()

    async def sign_up(self, data: SignUpRequest) -> TokenResponse:
        # Check if user exists
        existing = self.db.table("users").select("id").eq("email", data.email).execute()
        if existing.data:
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed = hash_password(data.password)
        user_id = str(uuid.uuid4())

        user = self.db.table("users").insert({
            "id": user_id,
            "email": data.email,
            "full_name": data.full_name,
            "password_hash": hashed,
            "auth_provider": "email",
        }).execute()

        if not user.data:
            raise HTTPException(status_code=500, detail="Failed to create user")

        user_data = user.data[0]
        token = create_access_token({"sub": user_id})

        logger.info("user_signed_up", user_id=user_id, email=data.email)
        return TokenResponse(
            access_token=token,
            user={
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "has_profile": False,
            }
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        result = self.db.table("users").select("*").eq("email", data.email).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = result.data[0]

        if not verify_password(data.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        profile = self.db.table("profiles").select("id").eq("user_id", user["id"]).execute()
        has_profile = bool(profile.data)

        token = create_access_token({"sub": user["id"]})
        logger.info("user_logged_in", user_id=user["id"])

        return TokenResponse(
            access_token=token,
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "has_profile": has_profile,
                "avatar_url": user.get("avatar_url"),
            }
        )

    async def google_auth(self, access_token: str) -> TokenResponse:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            google_user = resp.json()

        email = google_user["email"]
        full_name = google_user.get("name", email.split("@")[0])
        google_id = google_user["sub"]
        avatar_url = google_user.get("picture")

        existing = self.db.table("users").select("*").eq("email", email).execute()

        if existing.data:
            user = existing.data[0]
            user_id = user["id"]
        else:
            user_id = str(uuid.uuid4())
            result = self.db.table("users").insert({
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "google_id": google_id,
                "avatar_url": avatar_url,
                "auth_provider": "google",
            }).execute()
            user = result.data[0]

        profile = self.db.table("profiles").select("id").eq("user_id", user_id).execute()
        has_profile = bool(profile.data)

        token = create_access_token({"sub": user_id})
        logger.info("google_auth_success", user_id=user_id, email=email)

        return TokenResponse(
            access_token=token,
            user={
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "has_profile": has_profile,
                "avatar_url": avatar_url,
            }
        )