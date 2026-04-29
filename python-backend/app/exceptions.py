"""Custom exception classes and FastAPI exception handlers."""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.schemas import ApiResponse

logger = logging.getLogger(__name__)


class BusinessError(Exception):
    """Domain-level error with an error code and user-facing message."""

    def __init__(self, code: str = "BUSINESS_ERROR", message: str = "Operation failed", status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundError(BusinessError):
    def __init__(self, resource: str = "Resource", identifier: str | None = None):
        msg = f"{resource} not found" if identifier is None else f"{resource} not found: {identifier}"
        super().__init__(code="NOT_FOUND", message=msg, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(BusinessError):
    def __init__(self, message: str = "Validation failed", field: str | None = None):
        if field:
            message = f"{field}: {message}"
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(BusinessError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="AUTH_FAILED", message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionError(BusinessError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(code="PERMISSION_DENIED", message=message, status_code=status.HTTP_403_FORBIDDEN)


class RateLimitExceededError(BusinessError):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.retry_after = retry_after


# ── FastAPI exception handlers ───────────────────────────────────────

def register_exception_handlers(app) -> None:
    """Attach exception handlers to the FastAPI application."""

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        logger.warning("BusinessError: %s [%s]", exc.message, exc.code, exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(code=exc.code, message=exc.message, data=None).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiResponse(code="INTERNAL_ERROR", message="Internal server error", data=None).model_dump(),
        )
