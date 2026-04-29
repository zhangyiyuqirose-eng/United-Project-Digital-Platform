"""RBAC manager with Redis-cached permission resolution."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.models import RolePermission, UserRole
from app.models.system.models import Permission, Role

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 minutes


class DataScopeType(str, Enum):
    ALL = "all"
    SELF = "self"
    DEPT = "dept"
    DEPT_TREE = "dept_tree"
    CUSTOM = "custom"


@dataclass
class UserInfo:
    user_id: str
    username: str
    roles: list[str] = field(default_factory=list)
    permissions: set[str] = field(default_factory=set)
    data_scope: str = "all"
    dept_id: Optional[str] = None
    dept_ids: list[str] = field(default_factory=list)


class RBACManager:
    """Role-based access control manager with Redis caching."""

    def __init__(self, redis: Optional[Redis] = None) -> None:
        self._redis = redis

    async def get_user_info(
        self, db: AsyncSession, user_id: str, username: str, dept_id: Optional[str] = None
    ) -> UserInfo:
        """Resolve all roles, permissions, and data scope for a user."""
        # Try cache first
        cache_key = f"rbac:user:{user_id}"
        if self._redis:
            try:
                cached = await self._redis.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    return UserInfo(**data)
            except Exception:
                pass

        # Resolve from database
        roles_result = await db.execute(
            select(Role).join(UserRole, Role.role_id == UserRole.role_id).where(UserRole.user_id == user_id)
        )
        roles = roles_result.scalars().all()

        role_names: list[str] = []
        all_permissions: set[str] = set()
        data_scope = DataScopeType.ALL.value

        for role in roles:
            role_names.append(role.role_code)
            if role.role_code == "admin":
                data_scope = DataScopeType.ALL.value
            perms_result = await db.execute(
                select(Permission.permission_code)
                .join(RolePermission, Permission.permission_id == RolePermission.permission_id)
                .where(RolePermission.role_id == role.role_id)
            )
            all_permissions.update(perms_result.scalars().all())

        user_info = UserInfo(
            user_id=user_id,
            username=username,
            roles=role_names,
            permissions=all_permissions,
            data_scope=data_scope,
            dept_id=dept_id,
        )

        # Cache result
        if self._redis:
            try:
                import json
                await self._redis.set(cache_key, json.dumps(user_info.__dict__), ex=CACHE_TTL)
            except Exception:
                pass

        return user_info

    async def clear_cache(self, user_id: str) -> None:
        """Invalidate cached permissions for a user."""
        if self._redis:
            await self._redis.delete(f"rbac:user:{user_id}")

    def has_permission(self, user_info: UserInfo, permission: str) -> bool:
        """Check if user has a specific permission."""
        if "admin" in user_info.roles:
            return True
        return permission in user_info.permissions

    def has_role(self, user_info: UserInfo, role: str) -> bool:
        """Check if user has a specific role."""
        return role in user_info.roles


_manager: RBACManager | None = None


def get_rbac_manager(redis: Optional[Redis] = None) -> RBACManager:
    global _manager
    if _manager is None:
        _manager = RBACManager(redis)
    return _manager
