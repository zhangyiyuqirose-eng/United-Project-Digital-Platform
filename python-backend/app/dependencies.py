"""FastAPI dependencies: DB session, current user, Redis client, RBAC."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.config import settings
from app.core.rbac import RBACManager, UserInfo, get_rbac_manager
from app.core.security import decode_token
from app.database import async_session_factory, get_db

# ── Security scheme ──────────────────────────────────────────────────

bearer_scheme = HTTPBearer()

security = HTTPBearer(auto_error=False)


# ── Current user ─────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Extract and validate JWT token, return user info dict."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )

    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role", "user"),
        "username": payload.get("username", ""),
        "dept_id": payload.get("dept_id"),
    }


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return current_user


# ── Redis ────────────────────────────────────────────────────────────

_redis: Redis | None = None


async def get_redis() -> Redis:
    """Get or create Redis connection."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


# ── RBAC / Data permissions ──────────────────────────────────────────

async def get_user_info(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> UserInfo:
    """Resolve full user info with roles, permissions, and data scope."""
    manager = get_rbac_manager(redis)
    return await manager.get_user_info(
        db=db,
        user_id=current_user["user_id"],
        username=current_user.get("username", ""),
        dept_id=current_user.get("dept_id"),
    )


def require_permission(permission: str):
    """FastAPI dependency factory: require a specific permission."""
    async def _check(user_info: UserInfo = Depends(get_user_info)):
        manager = get_rbac_manager()
        if not manager.has_permission(user_info, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}",
            )
        return user_info
    return _check


def require_role(role: str):
    """FastAPI dependency factory: require a specific role."""
    async def _check(user_info: UserInfo = Depends(get_user_info)):
        manager = get_rbac_manager()
        if not manager.has_role(user_info, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}",
            )
        return user_info
    return _check
