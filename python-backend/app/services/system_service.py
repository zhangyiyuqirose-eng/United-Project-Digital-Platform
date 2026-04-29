"""System domain service — users, depts, roles, permissions, config, announcements, etc."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.core.security import hash_password
from app.exceptions import BusinessError, ResourceNotFoundError, ValidationError
from app.models.auth.models import RolePermission, User, UserRole
from app.models.system.models import (
    Announcement,
    Asset,
    AuditLog,
    Config,
    Dept,
    Dict,
    Meeting,
    Permission,
    Role,
)
from app.services.base import BaseService


class SystemService:
    """Encapsulates all system-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._user_svc = BaseService(db, User)
        self._dept_svc = BaseService(db, Dept)
        self._role_svc = BaseService(db, Role)
        self._perm_svc = BaseService(db, Permission)
        self._config_svc = BaseService(db, Config)
        self._announce_svc = BaseService(db, Announcement)
        self._asset_svc = BaseService(db, Asset)
        self._meeting_svc = BaseService(db, Meeting)
        self._dict_svc = BaseService(db, Dict)

    # ═══════════════════════════════════════════════════════════════════════
    # User CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_users(
        self, page: int = 1, size: int = 10,
        keyword: str | None = None, dept_id: str | None = None,
        status: int | None = None,
    ) -> PageResult:
        base = select(User)
        conditions: list = []
        if keyword:
            conditions.append(
                User.username.ilike(f"%{keyword}%") | User.name.ilike(f"%{keyword}%")
            )
        if dept_id:
            conditions.append(User.dept_id == dept_id)
        if status is not None:
            conditions.append(User.status == status)
        if conditions:
            base = base.where(*conditions)

        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0

        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(User.create_time.desc())
        )
        records = [_user_to_dict(u) for u in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def get_user(self, user_id: str) -> dict:
        u = await self._user_svc.get_or_404(user_id)
        return _user_to_dict(u)

    async def create_user(self, req: dict) -> dict:
        # Check duplicate username
        existing = await self.db.execute(
            select(User).where(User.username == req["username"])
        )
        if existing.scalar_one_or_none():
            raise ValidationError("用户名已存在")

        user = User(
            user_id=str(uuid.uuid4()),
            username=req["username"],
            password=hash_password(req.get("password", "Admin123!")),
            name=req.get("name"),
            dept_id=req.get("dept_id"),
            email=req.get("email"),
            phone=req.get("phone"),
            status=req.get("status", 1),
            password_changed_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.flush()
        return {"userId": user.user_id}

    async def update_user(self, user_id: str, updates: dict) -> None:
        await self._user_svc.update(user_id, **updates)

    async def delete_user(self, user_id: str) -> None:
        await self._user_svc.delete(user_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Dept CRUD + Tree
    # ═══════════════════════════════════════════════════════════════════════

    async def list_depts(self, page: int = 1, size: int = 100) -> PageResult:
        return await self._dept_svc.list_page(page=page, limit=size)

    async def get_dept(self, dept_id: str) -> dict:
        d = await self._dept_svc.get_or_404(dept_id)
        return _dept_to_dict(d)

    async def create_dept(self, req: dict) -> dict:
        dept = Dept(
            dept_id=str(uuid.uuid4()),
            dept_name=req["dept_name"],
            parent_id=req.get("parent_id"),
            leader_id=req.get("leader_id"),
            sort_order=req.get("sort_order", 0),
            status=req.get("status", 1),
        )
        self.db.add(dept)
        await self.db.flush()
        return {"deptId": dept.dept_id}

    async def update_dept(self, dept_id: str, updates: dict) -> None:
        await self._dept_svc.update(dept_id, **updates)

    async def delete_dept(self, dept_id: str) -> None:
        # Check for children
        children = await self.db.execute(
            select(func.count()).select_from(Dept).where(Dept.parent_id == dept_id)
        )
        if (children.scalar() or 0) > 0:
            raise BusinessError(code="PARAM_ERROR", message="请先删除子部门")
        await self._dept_svc.delete(dept_id)

    async def get_dept_tree(self) -> list[dict]:
        """Build a tree structure from flat dept list."""
        result = await self.db.execute(
            select(Dept).order_by(Dept.sort_order)
        )
        depts = result.scalars().all()
        dept_map: dict[str, dict] = {}
        roots: list[dict] = []

        for d in depts:
            node = _dept_to_dict(d)
            node["children"] = []
            dept_map[d.dept_id] = node

        for d in depts:
            node = dept_map[d.dept_id]
            if d.parent_id and d.parent_id in dept_map:
                dept_map[d.parent_id]["children"].append(node)
            else:
                roots.append(node)

        return roots

    # ═══════════════════════════════════════════════════════════════════════
    # Role CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_roles(self, page: int = 1, size: int = 100) -> PageResult:
        return await self._role_svc.list_page(page=page, limit=size)

    async def get_role(self, role_id: str) -> dict:
        r = await self._role_svc.get_or_404(role_id)
        return _role_to_dict(r)

    async def create_role(self, req: dict) -> dict:
        role = Role(
            role_id=str(uuid.uuid4()),
            role_name=req["role_name"],
            role_code=req["role_code"],
            description=req.get("description"),
            data_scope=req.get("data_scope", "all"),
            status=req.get("status", 1),
        )
        self.db.add(role)
        await self.db.flush()
        return {"roleId": role.role_id}

    async def update_role(self, role_id: str, updates: dict) -> None:
        await self._role_svc.update(role_id, **updates)

    async def delete_role(self, role_id: str) -> None:
        await self._role_svc.delete(role_id)

    # ── Role-Permission assignment ─────────────────────────────────────

    async def set_role_permissions(self, role_id: str, perm_ids: list[str]) -> dict:
        """Replace all permissions for a role."""
        role = await self._role_svc.get_or_404(role_id)
        # Delete existing
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        # Insert new
        for pid in perm_ids:
            rp = RolePermission(role_id=role_id, permission_id=pid)
            self.db.add(rp)
        await self.db.flush()
        return {"roleId": role_id, "permissionCount": len(perm_ids)}

    async def get_role_permissions(self, role_id: str) -> list[str]:
        """Get permission IDs assigned to a role."""
        result = await self.db.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id == role_id)
        )
        return [row[0] for row in result.all()]

    # ═══════════════════════════════════════════════════════════════════════
    # User-Role assignment
    # ═══════════════════════════════════════════════════════════════════════

    async def set_user_roles(self, user_id: str, role_ids: list[str]) -> dict:
        """Replace all roles for a user."""
        user = await self._user_svc.get_or_404(user_id)
        await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        for rid in role_ids:
            ur = UserRole(user_id=user_id, role_id=rid)
            self.db.add(ur)
        await self.db.flush()
        return {"userId": user_id, "roleCount": len(role_ids)}

    async def get_user_roles(self, user_id: str) -> list[str]:
        """Get role IDs assigned to a user."""
        result = await self.db.execute(
            select(UserRole.role_id).where(UserRole.user_id == user_id)
        )
        return [row[0] for row in result.all()]

    # ═══════════════════════════════════════════════════════════════════════
    # Permission CRUD + Tree
    # ═══════════════════════════════════════════════════════════════════════

    async def list_permissions(self, page: int = 1, size: int = 100) -> PageResult:
        return await self._perm_svc.list_page(page=page, limit=size)

    async def get_permission(self, perm_id: str) -> dict:
        p = await self._perm_svc.get_or_404(perm_id)
        return _perm_to_dict(p)

    async def create_permission(self, req: dict) -> dict:
        perm = Permission(
            permission_id=str(uuid.uuid4()),
            permission_name=req["permission_name"],
            permission_code=req["permission_code"],
            resource_type=req.get("resource_type"),
            resource_url=req.get("resource_url"),
            parent_id=req.get("parent_id"),
            status=req.get("status", 1),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(perm)
        await self.db.flush()
        return {"permissionId": perm.permission_id}

    async def update_permission(self, perm_id: str, updates: dict) -> None:
        await self._perm_svc.update(perm_id, **updates)

    async def delete_permission(self, perm_id: str) -> None:
        await self._perm_svc.delete(perm_id)

    async def get_permission_tree(self) -> list[dict]:
        """Build a tree structure from flat permission list."""
        result = await self.db.execute(select(Permission).order_by(Permission.permission_code))
        perms = result.scalars().all()
        perm_map: dict[str, dict] = {}
        roots: list[dict] = []

        for p in perms:
            node = _perm_to_dict(p)
            node["children"] = []
            perm_map[p.permission_id] = node

        for p in perms:
            node = perm_map[p.permission_id]
            if p.parent_id and p.parent_id in perm_map:
                perm_map[p.parent_id]["children"].append(node)
            else:
                roots.append(node)

        return roots

    # ═══════════════════════════════════════════════════════════════════════
    # Announcement CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_announcements(
        self, page: int = 1, size: int = 10, type: str | None = None
    ) -> PageResult:
        base = select(Announcement)
        if type:
            base = base.where(Announcement.type == type)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.offset(offset).limit(size).order_by(Announcement.publish_time.desc())
        )
        records = [_announce_to_dict(a) for a in result.scalars().all()]
        return PageResult(total=total, page=page, size=size, records=records)

    async def get_announcement(self, announcement_id: str) -> dict:
        a = await self._announce_svc.get_or_404(announcement_id)
        return _announce_to_dict(a)

    async def create_announcement(self, req: dict) -> dict:
        a = Announcement(
            announcement_id=str(uuid.uuid4()),
            title=req["title"],
            content=req.get("content"),
            type=req.get("type"),
            status=req.get("status", 1),
            publisher_id=req.get("publisher_id"),
            publish_time=req.get("publish_time", datetime.now(timezone.utc)),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(a)
        await self.db.flush()
        return {"announcementId": a.announcement_id}

    async def update_announcement(self, announcement_id: str, updates: dict) -> None:
        await self._announce_svc.update(announcement_id, **updates)

    async def delete_announcement(self, announcement_id: str) -> None:
        await self._announce_svc.delete(announcement_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Config CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_configs(self, page: int = 1, size: int = 100) -> PageResult:
        return await self._config_svc.list_page(page=page, limit=size)

    async def get_config_by_key(self, key: str) -> dict | None:
        result = await self.db.execute(
            select(Config).where(Config.config_key == key)
        )
        c = result.scalar_one_or_none()
        return _config_to_dict(c) if c else None

    async def create_config(self, req: dict) -> dict:
        c = Config(
            config_id=str(uuid.uuid4()),
            config_key=req["config_key"],
            config_value=req.get("config_value"),
            description=req.get("description"),
        )
        self.db.add(c)
        await self.db.flush()
        return {"configId": c.config_id}

    async def update_config(self, config_id: str, updates: dict) -> None:
        await self._config_svc.update(config_id, **updates)

    async def delete_config(self, config_id: str) -> None:
        await self._config_svc.delete(config_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Asset CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_assets(self, page: int = 1, size: int = 10) -> PageResult:
        return await self._asset_svc.list_page(page=page, limit=size)

    async def create_asset(self, req: dict) -> dict:
        asset = Asset(
            asset_id=str(uuid.uuid4()),
            asset_name=req["asset_name"],
            asset_type=req.get("asset_type"),
            asset_code=req.get("asset_code"),
            owner_id=req.get("owner_id"),
            location=req.get("location"),
            status=req.get("status"),
            purchase_date=req.get("purchase_date"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(asset)
        await self.db.flush()
        return {"assetId": asset.asset_id}

    async def update_asset(self, asset_id: str, updates: dict) -> None:
        await self._asset_svc.update(asset_id, **updates)

    async def delete_asset(self, asset_id: str) -> None:
        await self._asset_svc.delete(asset_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Meeting CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_meetings(self, page: int = 1, size: int = 10) -> PageResult:
        return await self._meeting_svc.list_page(page=page, limit=size)

    async def create_meeting(self, req: dict) -> dict:
        m = Meeting(
            meeting_id=str(uuid.uuid4()),
            meeting_name=req["meeting_name"],
            meeting_type=req.get("meeting_type"),
            start_time=req.get("start_time"),
            end_time=req.get("end_time"),
            location=req.get("location"),
            organizer_id=req.get("organizer_id"),
            participants=req.get("participants"),
            status=req.get("status"),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(m)
        await self.db.flush()
        return {"meetingId": m.meeting_id}

    async def update_meeting(self, meeting_id: str, updates: dict) -> None:
        await self._meeting_svc.update(meeting_id, **updates)

    async def delete_meeting(self, meeting_id: str) -> None:
        await self._meeting_svc.delete(meeting_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Dict CRUD
    # ═══════════════════════════════════════════════════════════════════════

    async def list_dicts(self, dict_type: str | None = None, page: int = 1, size: int = 100) -> PageResult:
        filters = {}
        if dict_type:
            filters["dict_type"] = dict_type
        return await self._dict_svc.list_page(page=page, limit=size, **filters)

    async def create_dict(self, req: dict) -> dict:
        d = Dict(
            dict_id=str(uuid.uuid4()),
            dict_type=req["dict_type"],
            dict_label=req["dict_label"],
            dict_value=req["dict_value"],
            sort_order=req.get("sort_order", 0),
            status=req.get("status", 1),
            create_time=datetime.now(timezone.utc),
        )
        self.db.add(d)
        await self.db.flush()
        return {"dictId": d.dict_id}

    async def update_dict(self, dict_id: str, updates: dict) -> None:
        await self._dict_svc.update(dict_id, **updates)

    async def delete_dict(self, dict_id: str) -> None:
        await self._dict_svc.delete(dict_id)

    # ═══════════════════════════════════════════════════════════════════════
    # Dashboard stats
    # ═══════════════════════════════════════════════════════════════════════

    async def get_dashboard_stats(self) -> dict:
        """Aggregate system-wide statistics for the admin dashboard."""
        user_count = await self._user_svc.count()
        dept_count = await self._dept_svc.count()
        role_count = await self._role_svc.count()
        perm_count = await self._perm_svc.count()

        active_users = await self._user_svc.count(status=1)

        # Announcements
        announce_count = await self._announce_svc.count(status=1)

        return {
            "totalUsers": user_count,
            "activeUsers": active_users,
            "totalDepts": dept_count,
            "totalRoles": role_count,
            "totalPermissions": perm_count,
            "activeAnnouncements": announce_count,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Dict converters
# ═══════════════════════════════════════════════════════════════════════════

def _user_to_dict(u: User) -> dict:
    return {
        "userId": u.user_id,
        "username": u.username,
        "name": u.name,
        "deptId": u.dept_id,
        "email": u.email,
        "phone": u.phone,
        "status": u.status,
    }


def _dept_to_dict(d: Dept) -> dict:
    return {
        "deptId": d.dept_id,
        "deptName": d.dept_name,
        "parentId": d.parent_id,
        "leaderId": d.leader_id,
        "sortOrder": d.sort_order,
        "status": d.status,
    }


def _role_to_dict(r: Role) -> dict:
    return {
        "roleId": r.role_id,
        "roleName": r.role_name,
        "roleCode": r.role_code,
        "description": r.description,
        "dataScope": r.data_scope,
        "status": r.status,
    }


def _perm_to_dict(p: Permission) -> dict:
    return {
        "permissionId": p.permission_id,
        "permissionName": p.permission_name,
        "permissionCode": p.permission_code,
        "resourceType": p.resource_type,
        "resourceUrl": p.resource_url,
        "parentId": p.parent_id,
        "status": p.status,
    }


def _announce_to_dict(a: Announcement) -> dict:
    return {
        "announcementId": a.announcement_id,
        "title": a.title,
        "content": a.content,
        "type": a.type,
        "status": a.status,
        "publisherId": a.publisher_id,
        "publishTime": str(a.publish_time) if a.publish_time else None,
    }


def _config_to_dict(c: Config) -> dict:
    return {
        "configId": c.config_id,
        "configKey": c.config_key,
        "configValue": c.config_value,
        "description": c.description,
    }
