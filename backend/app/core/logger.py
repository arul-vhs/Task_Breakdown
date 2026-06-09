import logging
import json
import contextvars
from datetime import datetime
import sys
from typing import Any, Dict

# Context variable to hold request/workflow parameters for structured logging
log_context = contextvars.ContextVar("log_context", default={})

def set_log_context(ctx: Dict[str, Any]):
    log_context.set(ctx)

def get_log_context() -> Dict[str, Any]:
    return log_context.get()

def update_log_context(updates: Dict[str, Any]):
    ctx = log_context.get().copy()
    ctx.update(updates)
    log_context.set(ctx)

def clear_log_context():
    log_context.set({})

class StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ctx = log_context.get()
        
        # Base JSON payload
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": ctx.get("request_id"),
            "thread_id": ctx.get("thread_id"),
            "user_id": ctx.get("user_id"),
            "goal_id": ctx.get("goal_id"),
            "workflow_stage": ctx.get("workflow_stage") or ctx.get("current_stage"),
            "endpoint": ctx.get("endpoint"),
            "duration_ms": ctx.get("duration_ms"),
            "event": ctx.get("event")
        }
        
        # Merge manual extra fields from logger.info(..., extra=...)
        if hasattr(record, "request_id") and record.request_id:
            payload["request_id"] = record.request_id
        if hasattr(record, "thread_id") and record.thread_id:
            payload["thread_id"] = record.thread_id
        if hasattr(record, "user_id") and record.user_id:
            payload["user_id"] = record.user_id
        if hasattr(record, "goal_id") and record.goal_id:
            payload["goal_id"] = record.goal_id
        if hasattr(record, "workflow_stage") and record.workflow_stage:
            payload["workflow_stage"] = record.workflow_stage
        if hasattr(record, "endpoint") and record.endpoint:
            payload["endpoint"] = record.endpoint
        if hasattr(record, "duration_ms") and record.duration_ms is not None:
            payload["duration_ms"] = record.duration_ms
        if hasattr(record, "event") and record.event:
            payload["event"] = record.event
            
        # Support inline dictionary format for record args
        if isinstance(record.args, dict):
            for k, v in record.args.items():
                if k in payload:
                    payload[k] = v
                    
        return json.dumps(payload)

def setup_logging():
    root = logging.getLogger()
    
    # Remove all existing standard handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    
    # Propagate other library logs to root logger, configuring formatting
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        l = logging.getLogger(logger_name)
        l.handlers = []
        l.propagate = True

# Standard custom logger for the application
logger = logging.getLogger("goalpilot")
logger.setLevel(logging.INFO)
