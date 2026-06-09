import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.logger import log_context, logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Determine path parameters for contextual user/goal IDs (if any)
        # Fast API path params are resolved later in routing, but we can do a preliminary extraction
        # from request.url.path to help structured logs catch goal/user IDs
        path_parts = request.url.path.strip("/").split("/")
        goal_id = None
        user_id = None
        
        # Detect goal UUIDs or thread IDs in path
        for part in path_parts:
            # Simple UUID check
            if len(part) == 36 and part.count("-") == 4:
                goal_id = part
                
        # Initialize context for this thread
        token = log_context.set({
            "request_id": request_id,
            "thread_id": None,
            "user_id": None,
            "goal_id": goal_id,
            "workflow_stage": None,
            "endpoint": f"{request.method} {request.url.path}",
            "duration_ms": None,
            "event": "request_start"
        })
        
        # Log start
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.perf_counter() - start_time) * 1000.0
            
            # Update log context for the end event
            ctx = log_context.get().copy()
            ctx["duration_ms"] = round(duration, 2)
            ctx["event"] = "request_complete"
            log_context.set(ctx)
            
            logger.info(f"Request completed with status {response.status_code}")
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000.0
            ctx = log_context.get().copy()
            ctx["duration_ms"] = round(duration, 2)
            ctx["event"] = "request_error"
            log_context.set(ctx)
            
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise e
            
        finally:
            log_context.reset(token)
