"""Unit tests for RBAC manager (app/core/rbac.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.rbac import RBACManager, UserInfo


def _make_user_info(roles=None, permissions=None, data_scope="all"):
    return UserInfo(
        user_id="u-1",
        username="testuser",
        roles=roles or [],
        permissions=permissions or set(),
        data_scope=data_scope,
    )


# ── has_permission ───────────────────────────────────────────────────

def test_has_permission_admin_bypass():
    info = _make_user_info(roles=["admin"])
    mgr = RBACManager()
    assert mgr.has_permission(info, "anything") is True


def test_has_permission_with_explicit_perm():
    info = _make_user_info(permissions=["user:read", "user:write"])
    mgr = RBACManager()
    assert mgr.has_permission(info, "user:read") is True
    assert mgr.has_permission(info, "user:write") is True


def test_has_permission_no_perm():
    info = _make_user_info(permissions=["user:read"])
    mgr = RBACManager()
    assert mgr.has_permission(info, "admin:delete") is False


def test_has_permission_empty_roles():
    info = _make_user_info(roles=[], permissions=["basic:view"])
    mgr = RBACManager()
    assert mgr.has_permission(info, "basic:view") is True
    assert mgr.has_permission(info, "admin:write") is False


# ── has_role ─────────────────────────────────────────────────────────

def test_has_role_present():
    info = _make_user_info(roles=["manager", "viewer"])
    mgr = RBACManager()
    assert mgr.has_role(info, "manager") is True


def test_has_role_not_present():
    info = _make_user_info(roles=["viewer"])
    mgr = RBACManager()
    assert mgr.has_role(info, "admin") is False


def test_has_role_empty():
    info = _make_user_info(roles=[])
    mgr = RBACManager()
    assert mgr.has_role(info, "any") is False


# ── get_user_info with Redis cache hit ───────────────────────────────

@pytest.mark.asyncio
async def test_get_user_info_cache_hit():
    redis_mock = AsyncMock()
    redis_mock.get.return_value = b'{"user_id":"u-1","username":"cached","roles":["admin"],"permissions":[],"data_scope":"all","dept_id":null,"dept_ids":[]}'

    mgr = RBACManager(redis=redis_mock)
    db_mock = MagicMock()

    info = await mgr.get_user_info(db_mock, "u-1", "testuser")
    assert info.username == "cached"
    assert info.roles == ["admin"]
    # DB should NOT be queried when cache hits
    db_mock.execute.assert_not_called()


# ── get_user_info with Redis cache miss ──────────────────────────────

@pytest.mark.asyncio
async def test_get_user_info_cache_miss():
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set = AsyncMock()

    mgr = RBACManager(redis=redis_mock)
    db_mock = MagicMock()

    # Mock the role query result
    role_mock = MagicMock()
    role_mock.role_code = "editor"
    role_mock.role_id = "role-1"
    roles_result_mock = MagicMock()
    roles_result_mock.scalars.return_value.all.return_value = [role_mock]

    # Mock the permission query result
    perms_result_mock = MagicMock()
    perms_result_mock.scalars.return_value.all.return_value = ["doc:read", "doc:write"]

    db_mock.execute = AsyncMock(side_effect=[roles_result_mock, perms_result_mock])

    info = await mgr.get_user_info(db_mock, "u-1", "testuser", dept_id="dept-1")
    assert info.user_id == "u-1"
    assert info.roles == ["editor"]
    assert "doc:read" in info.permissions
    assert info.dept_id == "dept-1"


# ── get_user_info without Redis ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_info_no_redis():
    mgr = RBACManager(redis=None)
    db_mock = MagicMock()

    role_mock = MagicMock()
    role_mock.role_code = "admin"
    role_mock.role_id = "role-admin"
    roles_result_mock = MagicMock()
    roles_result_mock.scalars.return_value.all.return_value = [role_mock]

    perms_result_mock = MagicMock()
    perms_result_mock.scalars.return_value.all.return_value = []

    db_mock.execute = AsyncMock(side_effect=[roles_result_mock, perms_result_mock])

    info = await mgr.get_user_info(db_mock, "u-1", "adminuser")
    assert info.roles == ["admin"]
    assert info.data_scope == "all"


# ── get_user_info with admin role ────────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_info_admin_data_scope():
    mgr = RBACManager(redis=None)
    db_mock = MagicMock()

    role_mock = MagicMock()
    role_mock.role_code = "admin"
    role_mock.role_id = "role-admin"
    roles_result_mock = MagicMock()
    roles_result_mock.scalars.return_value.all.return_value = [role_mock]

    perms_result_mock = MagicMock()
    perms_result_mock.scalars.return_value.all.return_value = ["*"]

    db_mock.execute = AsyncMock(side_effect=[roles_result_mock, perms_result_mock])

    info = await mgr.get_user_info(db_mock, "u-1", "adminuser")
    assert info.data_scope == "all"
    assert "admin" in info.roles


# ── get_user_info with multiple roles ────────────────────────────────

@pytest.mark.asyncio
async def test_get_user_info_multiple_roles():
    mgr = RBACManager(redis=None)
    db_mock = MagicMock()

    role1 = MagicMock()
    role1.role_code = "viewer"
    role1.role_id = "role-viewer"
    role2 = MagicMock()
    role2.role_code = "editor"
    role2.role_id = "role-editor"
    roles_result_mock = MagicMock()
    roles_result_mock.scalars.return_value.all.return_value = [role1, role2]

    perm_results = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=["doc:read"])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=["doc:write", "doc:delete"])))),
    ]

    call_count = [0]

    async def mock_execute(stmt):
        result = perm_results[call_count[0]]
        call_count[0] += 1
        return result

    # First call returns roles, subsequent calls return permissions
    db_mock.execute = AsyncMock(side_effect=[roles_result_mock] + [r for r in perm_results])

    info = await mgr.get_user_info(db_mock, "u-1", "multirole")
    assert "viewer" in info.roles
    assert "editor" in info.roles


# ── clear_cache ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_cache_with_redis():
    redis_mock = AsyncMock()
    mgr = RBACManager(redis=redis_mock)
    await mgr.clear_cache("u-1")
    redis_mock.delete.assert_called_once_with("rbac:user:u-1")


@pytest.mark.asyncio
async def test_clear_cache_no_redis():
    mgr = RBACManager(redis=None)
    # Should not raise
    await mgr.clear_cache("u-1")


# ── get_rbac_manager singleton ───────────────────────────────────────

def test_get_rbac_manager_singleton():
    from app.core.rbac import get_rbac_manager, _manager

    # Reset the global for test isolation
    import app.core.rbac as rbac_module
    old = rbac_module._manager
    rbac_module._manager = None

    mgr1 = get_rbac_manager()
    mgr2 = get_rbac_manager()
    assert mgr1 is mgr2

    # Restore
    rbac_module._manager = old


def test_get_rbac_manager_with_redis():
    from app.core.rbac import get_rbac_manager
    import app.core.rbac as rbac_module
    old = rbac_module._manager
    rbac_module._manager = None

    redis_mock = MagicMock()
    mgr = get_rbac_manager(redis=redis_mock)
    assert mgr._redis is redis_mock

    rbac_module._manager = old


# ── UserInfo dataclass ───────────────────────────────────────────────

def test_user_info_defaults():
    info = UserInfo(user_id="u-1", username="test")
    assert info.roles == []
    assert info.permissions == set()
    assert info.data_scope == "all"
    assert info.dept_id is None
    assert info.dept_ids == []


def test_user_info_with_values():
    info = UserInfo(
        user_id="u-1", username="test",
        roles=["admin"], permissions={"read", "write"},
        data_scope="dept", dept_id="d-1",
    )
    assert info.roles == ["admin"]
    assert "read" in info.permissions
    assert info.data_scope == "dept"
    assert info.dept_id == "d-1"
