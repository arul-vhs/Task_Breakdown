import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import update_log_context

logger = logging.getLogger("goalpilot.error_handler")

async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    update_log_context({"event": "exception_value_error", "error_msg": str(exc)})
    logger.warning(f"ValueError caught: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc)
            }
        }
    )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    update_log_context({"event": "exception_database_error", "error_msg": str(exc)})
    logger.error(f"Database error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred."
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    update_log_context({"event": "exception_http_error", "error_status": exc.status_code})
    logger.warning(f"HTTPException caught ({exc.status_code}): {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    update_log_context({"event": "exception_unhandled_error", "error_msg": str(exc)})
    logger.error(f"Unhandled exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred."
            }
        }
    )
