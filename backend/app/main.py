from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import (
    auth,
    goals,
    strategies,
    validation,
    roadmap,
    schedules,
    progress,
    coach,
    replanning,
    workflows,
    health
)
from app.database.session import engine
from app.database.base import Base
import uvicorn

# Initialize structured logging immediately
from app.core.logger import setup_logging
setup_logging()

# Import middlewares and error handlers
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import (
    value_error_handler,
    sqlalchemy_error_handler,
    http_exception_handler,
    generic_exception_handler
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

# Import rate limiting dependencies
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

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

# Set rate limiter state and error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register central exception handlers
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Configure request ID & duration logging middleware
app.add_middleware(RequestIDMiddleware)

# Configure CORS permissions matching approved architectures
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Health routes (directly at root)
app.include_router(
    health.router,
    tags=["Health Monitoring"]
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

app.include_router(
    strategies.router,
    prefix=f"{settings.API_V1_STR}/strategies",
    tags=["Strategy Management"]
)

app.include_router(
    validation.router,
    prefix=f"{settings.API_V1_STR}/validation",
    tags=["Validation Management"]
)

app.include_router(
    roadmap.router,
    prefix=f"{settings.API_V1_STR}/roadmap",
    tags=["Roadmap Management"]
)

app.include_router(
    schedules.router,
    prefix=f"{settings.API_V1_STR}/schedule",
    tags=["Schedule Management"]
)

app.include_router(
    progress.router,
    prefix=f"{settings.API_V1_STR}/progress",
    tags=["Progress Management"]
)

app.include_router(
    coach.router,
    prefix=f"{settings.API_V1_STR}/coach",
    tags=["Coach Management"]
)

app.include_router(
    replanning.router,
    prefix=f"{settings.API_V1_STR}/replan",
    tags=["Adaptive Replanning"]
)

app.include_router(
    workflows.router,
    prefix=f"{settings.API_V1_STR}/workflows",
    tags=["Workflow Engine"]
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
