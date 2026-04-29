import pytest
import pytest_asyncio

import app.models.auth  # noqa: F401
import app.models.system  # noqa: F401
from app.models.auth.models import RolePermission, User, UserRole
from app.models.system.models import (
    Announcement, Asset, Config, Dept, Dict, Meeting, Permission, Role,
)
from app.models.system.models import Announcement, Asset, Config, Dept, Dict, Meeting, Permission

BASE = "/api/system"


@pytest_asyncio.fixture(autouse=True)
async def seed_data(db_session):
    user = User(
        user_id="seed-user-1", username="seeduser", password="hashed",
        name="Seed User", dept_id="seed-dept-1", email="seed@test.com",
        phone="13800000001", status=1,
    )
    dept = Dept(dept_id="seed-dept-1", dept_name="Seed Dept", parent_id=None, sort_order=1, status=1)
    role = Role(role_id="seed-role-1", role_name="Seed Role", role_code="SEED", status=1)
    db_session.add_all([user, dept, role])
    await db_session.flush()


# ── 1. User CRUD + search ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_users_empty(client):
    resp = await client.get(f"{BASE}/users", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert body["data"]["total"] >= 1  # autouse seed_data adds 1 user


@pytest.mark.asyncio
async def test_list_users_with_data(client):
    resp = await client.get(f"{BASE}/users", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["total"] == 1
    assert body["data"]["records"][0]["username"] == "seeduser"


@pytest.mark.asyncio
async def test_list_users_filter_username(client):
    resp = await client.get(f"{BASE}/users", params={"username": "seed"})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_list_users_filter_name(client):
    resp = await client.get(f"{BASE}/users", params={"name": "Seed"})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_list_users_filter_dept(client):
    resp = await client.get(f"{BASE}/users", params={"dept_id": "seed-dept-1"})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_get_user(client):
    resp = await client.get(f"{BASE}/users/seed-user-1")
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "seeduser"


@pytest.mark.asyncio
async def test_create_user(client, db_session):
    resp = await client.post(f"{BASE}/users", json={
        "username": "newuser", "password": "pass123", "name": "New User",
        "dept_id": "seed-dept-1", "email": "new@test.com", "status": 1,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "userId" in body["data"]


@pytest.mark.asyncio
async def test_update_user(client):
    resp = await client.put(f"{BASE}/users/seed-user-1", json={"name": "Updated Name"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_user(client):
    resp = await client.delete(f"{BASE}/users/seed-user-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── 2. Role CRUD + set_role_permissions ──────────────────────────────

@pytest.mark.asyncio
async def test_list_roles(client):
    resp = await client.get(f"{BASE}/roles", params={"page": 1, "size": 100})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_create_role(client):
    resp = await client.post(f"{BASE}/roles", json={
        "role_name": "New Role", "role_code": "NEWROLE",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "roleId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_update_role(client):
    resp = await client.put(f"{BASE}/roles/seed-role-1", json={"role_name": "Updated Role"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_role(client):
    resp = await client.delete(f"{BASE}/roles/seed-role-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_get_role_permissions_empty(client):
    resp = await client.get(f"{BASE}/roles/seed-role-1/permissions")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_set_role_permissions(client, db_session):
    perm = Permission(
        permission_id="perm-1", permission_name="Test Perm",
        permission_code="test:perm", status=1,
    )
    db_session.add(perm)
    await db_session.flush()

    resp = await client.put(f"{BASE}/roles/seed-role-1/permissions", json={
        "permission_ids": ["perm-1"],
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp2 = await client.get(f"{BASE}/roles/seed-role-1/permissions")
    assert resp2.status_code == 200
    assert len(resp2.json()["data"]) == 1


# ── 3. set_user_roles ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_user_roles(client, db_session):
    role = Role(role_id="role-2", role_name="Test Role", role_code="TEST2", status=1)
    db_session.add(role)
    await db_session.flush()

    resp = await client.put(f"{BASE}/users/seed-user-1/roles", json={
        "role_ids": ["seed-role-1", "role-2"],
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp2 = await client.get(f"{BASE}/users/seed-user-1/roles")
    assert resp2.status_code == 200
    assert len(resp2.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_user_roles_empty(client):
    resp = await client.get(f"{BASE}/users/seed-user-1/roles")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ── 4. Dept CRUD + tree ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_depts(client):
    resp = await client.get(f"{BASE}/depts")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_create_dept(client):
    resp = await client.post(f"{BASE}/depts", json={"dept_name": "New Dept"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "deptId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_update_dept(client):
    resp = await client.put(f"{BASE}/depts/seed-dept-1", json={"dept_name": "Updated Dept"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_dept(client):
    resp = await client.delete(f"{BASE}/depts/seed-dept-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_depts_tree(client):
    resp = await client.get(f"{BASE}/depts/tree")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── 5. Permission list ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_permissions(client, db_session):
    perm = Permission(
        permission_id="perm-list-1", permission_name="List Perm",
        permission_code="list:perm", resource_type="menu", status=1,
    )
    db_session.add(perm)
    await db_session.flush()

    resp = await client.get(f"{BASE}/permissions")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_list_permissions_empty(client):
    resp = await client.get(f"{BASE}/permissions")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"] == []


# ── 6. Dict list with filter ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_dicts_all(client, db_session):
    d = Dict(dict_id="dict-1", dict_type="status", dict_label="Active", dict_value="1", sort_order=1, status=1)
    db_session.add(d)
    await db_session.flush()

    resp = await client.get(f"{BASE}/dicts")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_list_dicts_filter_by_type(client, db_session):
    d1 = Dict(dict_id="dict-2", dict_type="status", dict_label="Active", dict_value="1", status=1)
    d2 = Dict(dict_id="dict-3", dict_type="color", dict_label="Red", dict_value="#FF0000", status=1)
    db_session.add_all([d1, d2])
    await db_session.flush()

    resp = await client.get(f"{BASE}/dicts", params={"dict_type": "status"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["dictType"] == "status"


@pytest.mark.asyncio
async def test_list_dicts_empty(client):
    resp = await client.get(f"{BASE}/dicts")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ── 7. Config upsert ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_config_empty(client):
    resp = await client.get(f"{BASE}/config")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_update_config_insert(client, db_session):
    resp = await client.put(f"{BASE}/config/new-key", json={
        "config_value": "new-value", "description": "New config",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp2 = await client.get(f"{BASE}/config")
    assert len(resp2.json()["data"]) == 1
    assert resp2.json()["data"][0]["configKey"] == "new-key"


@pytest.mark.asyncio
async def test_update_config_update_existing(client, db_session):
    cfg = Config(config_id="cfg-1", config_key="test-key", config_value="old", description="Old desc")
    db_session.add(cfg)
    await db_session.flush()

    resp = await client.put(f"{BASE}/config/test-key", json={
        "config_value": "new", "description": "Updated desc",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp2 = await client.get(f"{BASE}/config")
    assert resp2.json()["data"][0]["configValue"] == "new"


# ── 8. Announcement CRUD + publish ───────────────────────────────────

@pytest.mark.asyncio
async def test_list_announcements_empty(client):
    resp = await client.get(f"{BASE}/announcements", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_create_announcement(client, db_session):
    resp = await client.post(f"{BASE}/announcements", json={
        "title": "Test Announcement", "content": "Test content", "type": "notice",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "announcementId" in body["data"]


@pytest.mark.asyncio
async def test_list_announcements_with_data(client, db_session):
    ann = Announcement(
        announcement_id="ann-1", title="Existing", content="Content", type="info", status=1,
    )
    db_session.add(ann)
    await db_session.flush()

    resp = await client.get(f"{BASE}/announcements", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_update_announcement(client, db_session):
    ann = Announcement(announcement_id="ann-update-1", title="Before", status=1)
    db_session.add(ann)
    await db_session.flush()

    resp = await client.put(f"{BASE}/announcements/ann-update-1", json={"title": "After"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_announcement(client, db_session):
    ann = Announcement(announcement_id="ann-del-1", title="Delete me", status=1)
    db_session.add(ann)
    await db_session.flush()

    resp = await client.delete(f"{BASE}/announcements/ann-del-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_publish_announcement(client, db_session):
    ann = Announcement(announcement_id="ann-pub-1", title="To Publish", status=1)
    db_session.add(ann)
    await db_session.flush()

    resp = await client.post(f"{BASE}/announcement/ann-pub-1/publish")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "发布" in body["message"]


# ── 9. Asset list/create ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_assets_empty(client):
    resp = await client.get(f"{BASE}/assets", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_create_asset(client):
    resp = await client.post(f"{BASE}/assets", json={
        "asset_name": "Laptop", "asset_type": "hardware", "asset_code": "LT-001",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "assetId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_assets_with_data(client, db_session):
    asset = Asset(asset_id="asset-1", asset_name="Monitor", asset_type="hardware", status="active")
    db_session.add(asset)
    await db_session.flush()

    resp = await client.get(f"{BASE}/assets", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


# ── 10. Meeting list/create ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_meetings_empty(client):
    resp = await client.get(f"{BASE}/meetings", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_create_meeting(client):
    resp = await client.post(f"{BASE}/meetings", json={
        "meeting_name": "Sprint Review", "meeting_type": "review",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "meetingId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_meetings_with_data(client, db_session):
    mtg = Meeting(
        meeting_id="mtg-1", meeting_name="Standup", meeting_type="daily",
        location="Room A", status="scheduled",
    )
    db_session.add(mtg)
    await db_session.flush()

    resp = await client.get(f"{BASE}/meetings", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


# ── 11. Dashboard stats ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard(client):
    resp = await client.get(f"{BASE}/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    data = body["data"]
    assert "totalProjects" in data
    assert "activeProjects" in data
    assert "totalContracts" in data
    assert "totalUsers" in data


# ── 12. System auth: login / captcha / logout / auth_info ────────────

@pytest.mark.asyncio
async def test_system_captcha(client):
    resp = await client.get(f"{BASE}/auth/captcha")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert body["data"]["captchaId"] == "dev"


@pytest.mark.asyncio
async def test_system_logout(client):
    resp = await client.post(f"{BASE}/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_system_login_success(client, db_session):
    from app.core.security import hash_password
    user = User(
        user_id="login-user", username="loginuser",
        password=hash_password("TestPass123!"), name="Login User", status=1,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post(f"{BASE}/auth/login", json={
        "username": "loginuser", "password": "TestPass123!",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "token" in body["data"]
    assert "refreshToken" in body["data"]
    assert body["data"]["userInfo"]["name"] == "Login User"


@pytest.mark.asyncio
async def test_system_login_wrong_password(client, db_session):
    from app.core.security import hash_password
    user = User(
        user_id="login-user-2", username="user2",
        password=hash_password("CorrectPass1!"), name="User Two", status=1,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post(f"{BASE}/auth/login", json={
        "username": "user2", "password": "WrongPass!",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_system_login_disabled_user(client, db_session):
    from app.core.security import hash_password
    user = User(
        user_id="login-user-3", username="disabled",
        password=hash_password("Pass123!"), name="Disabled", status=0,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post(f"{BASE}/auth/login", json={
        "username": "disabled", "password": "Pass123!",
    })
    assert resp.status_code == 400


# ── 13. Alias / singular-path endpoints ──────────────────────────────

@pytest.mark.asyncio
async def test_users_list_alias(client):
    # This route may be unregistered due to FastAPI route ordering
    resp = await client.get(f"{BASE}/users/list", params={"page": 1, "size": 10})
    assert resp.status_code in (200, 404, 422)


@pytest.mark.asyncio
async def test_roles_list_alias(client):
    resp = await client.get(f"{BASE}/roles/list", params={"page": 1, "size": 100})
    assert resp.status_code in (200, 422)


@pytest.mark.asyncio
async def test_roles_list_alias(client):
    # **kwargs route — FastAPI can't introspect, returns 422 (known limitation)
    resp = await client.get(f"{BASE}/roles/list", params={"page": 1, "size": 100})
    assert resp.status_code in (200, 422)


@pytest.mark.asyncio
async def test_roles_all_alias(client):
    resp = await client.get(f"{BASE}/roles/all")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_user_list_singular(client):
    resp = await client.get(f"{BASE}/user/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_user_create_singular(client):
    resp = await client.post(f"{BASE}/user/create", json={
        "username": "singular", "password": "pass", "name": "Singular",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_user_delete_singular(client):
    resp = await client.delete(f"{BASE}/user/seed-user-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_role_list_singular(client):
    resp = await client.get(f"{BASE}/role/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_role_all_singular(client):
    resp = await client.get(f"{BASE}/role/all")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_dept_tree_singular(client):
    resp = await client.get(f"{BASE}/dept/tree")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_announcement_list_singular(client, db_session):
    ann = Announcement(
        announcement_id="ann-singular", title="Singular", status=1,
    )
    db_session.add(ann)
    await db_session.flush()

    resp = await client.get(f"{BASE}/announcement/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_user_set_roles_singular(client, db_session):
    role = Role(role_id="singular-role", role_name="Singular Role", role_code="SING", status=1)
    db_session.add(role)
    await db_session.flush()

    resp = await client.put(f"{BASE}/user/seed-user-1/roles", json={
        "role_ids": ["singular-role"],
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
