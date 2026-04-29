"""RBAC permission checking — mirrors @RequiresPermission in Java."""

from __future__ import annotations

from functools import wraps

from fastapi import HTTPException, status


def requires_permission(permission_code: str, *, logical_and: bool = False):
    """Decorator that checks if the current user has the required permission.

    In the monolith this checks the user's roles/permissions loaded during auth.
    For now it's a placeholder — full RBAC is enforced at the API router level
    via dependency injection.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Permission check is done via FastAPI dependencies in api/ routers
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionDenied(Exception):
    """Raised when a user lacks the required permission."""

    def __init__(self, message: str = "Insufficient permissions"):
        self.message = message
        super().__init__(self.message)
