from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, goals
from app.database.session import engine, Base
import uvicorn

# Initialize Database tables on application launch
from sqlalchemy import create_engine
from sqlalchemy.sql import text

def create_database_if_not_exists():
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        return
    try:
        # Connect to system database "postgres" to verify target db existence
        base_url, db_name = db_url.rsplit("/", 1)
        sys_url = f"{base_url}/postgres"
        sys_engine = create_engine(sys_url, isolation_level="AUTOCOMMIT")
        with sys_engine.connect() as conn:
            exists = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
            ).scalar()
            if not exists:
                conn.execute(text(f"CREATE DATABASE {db_name}"))
    except Exception as e:
        print(f"PostgreSQL database check error: {e}")

try:
    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database table generation error: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Agent OnboardX Backend - AI Goal Execution Engine API"
)

# Configure CORS permissions matching approved architectures
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router endpoints
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

app.include_router(
    goals.router,
    prefix=f"{settings.API_V1_STR}/goals",
    tags=["Goals Management"]
)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Agent OnboardX API Engine",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
