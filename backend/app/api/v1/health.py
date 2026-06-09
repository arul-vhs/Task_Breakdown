import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.database.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/health/database")
def database_health(db: Session = Depends(get_db)):
    start_time = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start_time) * 1000.0
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/health/llm")
def llm_health():
    # Health Check Optimization (no generate() calls to prevent token consumption)
    try:
        # Check API key configuration status
        gemini_key = settings.GEMINI_API_KEY
        openai_key = settings.OPENAI_API_KEY
        
        has_gemini = bool(gemini_key)
        has_openai = bool(openai_key)
        
        if not has_gemini and not has_openai:
            return {
                "status": "unhealthy",
                "reason": "Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured."
            }
            
        # Determine the primary active provider
        active_provider = "gemini" if has_gemini else "openai"
        model_name = settings.GEMINI_MODEL if active_provider == "gemini" else "gpt-4o"
        
        return {
            "status": "healthy",
            "provider": active_provider,
            "model": model_name
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
