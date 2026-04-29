"""Shared response schemas and error codes — must match Java ApiResponse<T> exactly."""

from __future__ import annotations

import time
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str
    message: str
    data: T | None = None
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> dict:
        return cls(code="SUCCESS", message=message, data=data).model_dump()

    @classmethod
    def error(cls, code: str = "500", message: str = "Internal server error") -> dict:
        return cls(code=code, message=message, data=None).model_dump()


class PageResult(BaseModel):
    """Pagination wrapper matching MyBatis-Plus Page response."""

    records: list[Any] = []
    total: int = 0
    page: int = 1
    size: int = 10


class PaginationInput(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


# ── Error codes (mirror ErrorCodeEnum.java) ──────────────────────────

class ErrorCode:
    SUCCESS = "SUCCESS"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    PARAM_ERROR = "PARAM_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE = "DUPLICATE"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"

    LOGIN_FAILED = "AUTH_LOGIN_FAILED"
    TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    CAPTCHA_ERROR = "AUTH_CAPTCHA_ERROR"
    SSO_ERROR = "AUTH_SSO_ERROR"

    USER_NOT_FOUND = "SYS_USER_NOT_FOUND"
    USER_DISABLED = "SYS_USER_DISABLED"
    ROLE_NOT_FOUND = "SYS_ROLE_NOT_FOUND"
    DEPT_NOT_FOUND = "SYS_DEPT_NOT_FOUND"

    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_STATUS_ERROR = "PROJECT_STATUS_ERROR"
    PROJECT_CHANGE_DENIED = "PROJECT_CHANGE_DENIED"

    STAFF_NOT_FOUND = "RESOURCE_STAFF_NOT_FOUND"
    STAFF_STATUS_ERROR = "RESOURCE_STAFF_STATUS_ERROR"
    UNSPENT_HOURS = "RESOURCE_UNSPENT_HOURS"

    TIMESHEET_OVERFLOW = "TIMESHEET_OVERFLOW"
    TIMESHEET_NOT_FOUND = "TIMESHEET_NOT_FOUND"

    COST_CALCULATE_ERROR = "COST_CALCULATE_ERROR"
    SETTLEMENT_ERROR = "COST_SETTLEMENT_ERROR"

    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    TASK_NOT_FOUND = "WORKFLOW_TASK_NOT_FOUND"
    TASK_ALREADY_DONE = "WORKFLOW_TASK_ALREADY_DONE"

    AI_GENERATE_ERROR = "AI_GENERATE_ERROR"
    NLQ_PARSE_ERROR = "NLQ_PARSE_ERROR"

    NOTIFY_SEND_ERROR = "NOTIFY_SEND_ERROR"

    FILE_NOT_FOUND = "FILE_NOT_FOUND"

    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    INTEGRATION_TIMEOUT = "INTEGRATION_TIMEOUT"
