"""System API router — consolidates 13 system controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.dependencies import get_current_admin_user, get_current_user
from app.exceptions import BusinessError, ResourceNotFoundError, ValidationError
from app.models.system.models import (
    Announcement,
    Asset,
    Config,
    Dept,
    Dict,
    Meeting,
    Permission,
    ReviewMeeting,
    ReviewOpinion,
    Role,
)
from app.models.auth.models import RolePermission, User, UserRole

router = APIRouter(tags=["system"])


# ── Users ────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    username: str | None = None,
    name: str | None = None,
    dept_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    if username:
        stmt = stmt.where(User.username.ilike(f"%{username}%"))
    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))
    if dept_id:
        stmt = stmt.where(User.dept_id == dept_id)
    stmt = stmt.order_by(User.create_time.desc())

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    offset = (page - 1) * size
    stmt = stmt.offset(offset).limit(size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return ApiResponse(
        code="SUCCESS", message="success",
        data=PageResult(
            total=total, page=page, size=size,
            records=[
                dict(
                    userId=u.user_id, username=u.username, name=u.name,
                    deptId=u.dept_id, email=u.email,
                    phone=u.decrypt_fields().get("phone", u.phone),
                    status=u.status,
                )
                for u in users
            ],
        ),
    )


@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)
    decrypted = user.decrypt_fields()
    return ApiResponse(code="SUCCESS", message="success", data={
        "userId": user.user_id, "username": user.username, "name": user.name,
        "deptId": user.dept_id, "email": user.email,
        "phone": decrypted.get("phone", user.phone),
        "status": user.status,
    })


@router.post("/users")
async def create_user(req: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    from app.core.security import hash_password
    user = User(
        user_id=str(uuid.uuid4()), username=req.username,
        password=hash_password(req.password), name=req.name,
        dept_id=req.dept_id, email=req.email, phone=req.phone,
        status=req.status or 1, password_changed_at=datetime.now(timezone.utc),
    )
    user.encrypt_fields()
    db.add(user)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"userId": user.user_id})


@router.put("/users/{user_id}")
async def update_user(user_id: str, req: UserUpdateRequest, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.encrypt_fields()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await _get_user_or_404(db, user_id)
    await db.delete(user)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Roles ────────────────────────────────────────────────────────────

@router.get("/roles")
async def list_roles(page: int = 1, size: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(Role).order_by(Role.create_time.desc())
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data={
        "total": len(roles), "page": page, "size": size,
        "items": [{"roleId": r.role_id, "roleName": r.role_name, "roleCode": r.role_code,
                    "description": r.description, "status": r.status} for r in roles],
    })


@router.post("/roles")
async def create_role(req: RoleCreateRequest, db: AsyncSession = Depends(get_db)):
    role = Role(role_id=str(uuid.uuid4()), role_name=req.role_name,
                role_code=req.role_code, description=req.description, status=req.status or 1)
    db.add(role)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"roleId": role.role_id})


@router.put("/roles/{role_id}")
async def update_role(role_id: str, req: RoleUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Role).where(Role.role_id == role_id)
    role = (await db.execute(stmt)).scalar_one_or_none()
    if not role:
        raise ResourceNotFoundError("角色", role_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Role).where(Role.role_id == role_id)
    role = (await db.execute(stmt)).scalar_one_or_none()
    if not role:
        raise ResourceNotFoundError("角色", role_id)
    await db.delete(role)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Role permissions ─────────────────────────────────────────────────

@router.get("/roles/{role_id}/permissions")
async def get_role_permissions(role_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).join(RolePermission, Permission.permission_id == RolePermission.permission_id).where(RolePermission.role_id == role_id)
    result = await db.execute(stmt)
    perms = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"permissionId": p.permission_id, "permissionName": p.permission_name,
         "permissionCode": p.permission_code, "resourceType": p.resource_type,
         "resourceUrl": p.resource_url, "parentId": p.parent_id} for p in perms
    ])


@router.put("/roles/{role_id}/permissions")
async def set_role_permissions(role_id: str, req: RolePermissionsRequest, db: AsyncSession = Depends(get_db)):
    # Delete existing
    stmt = select(RolePermission).where(RolePermission.role_id == role_id)
    result = await db.execute(stmt)
    for rp in result.scalars().all():
        await db.delete(rp)
    # Add new
    for pid in req.permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=pid))
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── User roles ───────────────────────────────────────────────────────

@router.get("/users/{user_id}/roles")
async def get_user_roles(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Role).join(UserRole, Role.role_id == UserRole.role_id).where(UserRole.user_id == user_id)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"roleId": r.role_id, "roleName": r.role_name, "roleCode": r.role_code} for r in roles
    ])


@router.put("/users/{user_id}/roles")
async def set_user_roles(user_id: str, req: UserRolesRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(UserRole).where(UserRole.user_id == user_id)
    result = await db.execute(stmt)
    for ur in result.scalars().all():
        await db.delete(ur)
    for rid in req.role_ids:
        db.add(UserRole(user_id=user_id, role_id=rid))
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Departments ──────────────────────────────────────────────────────

@router.get("/depts")
async def list_depts(db: AsyncSession = Depends(get_db)):
    stmt = select(Dept).order_by(Dept.sort_order)
    result = await db.execute(stmt)
    depts = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"deptId": d.dept_id, "deptName": d.dept_name, "parentId": d.parent_id,
         "leaderId": d.leader_id, "sortOrder": d.sort_order, "status": d.status} for d in depts
    ])


@router.post("/depts")
async def create_dept(req: DeptCreateRequest, db: AsyncSession = Depends(get_db)):
    dept = Dept(dept_id=str(uuid.uuid4()), dept_name=req.dept_name,
                parent_id=req.parent_id, leader_id=req.leader_id,
                sort_order=req.sort_order or 0, status=req.status or 1)
    db.add(dept)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"deptId": dept.dept_id})


@router.put("/depts/{dept_id}")
async def update_dept(dept_id: str, req: DeptUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Dept).where(Dept.dept_id == dept_id)
    dept = (await db.execute(stmt)).scalar_one_or_none()
    if not dept:
        raise ResourceNotFoundError("部门", dept_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/depts/{dept_id}")
async def delete_dept(dept_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Dept).where(Dept.dept_id == dept_id)
    dept = (await db.execute(stmt)).scalar_one_or_none()
    if not dept:
        raise ResourceNotFoundError("部门", dept_id)
    await db.delete(dept)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Permissions ──────────────────────────────────────────────────────

@router.get("/permissions")
async def list_permissions(db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).order_by(Permission.permission_code)
    result = await db.execute(stmt)
    perms = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"permissionId": p.permission_id, "permissionName": p.permission_name,
         "permissionCode": p.permission_code, "resourceType": p.resource_type,
         "resourceUrl": p.resource_url, "parentId": p.parent_id, "status": p.status} for p in perms
    ])


# ── Dict ─────────────────────────────────────────────────────────────

@router.get("/dicts")
async def list_dicts(dict_type: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Dict).order_by(Dict.sort_order)
    if dict_type:
        stmt = stmt.where(Dict.dict_type == dict_type)
    result = await db.execute(stmt)
    dicts = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"dictId": d.dict_id, "dictType": d.dict_type, "dictLabel": d.dict_label,
         "dictValue": d.dict_value, "sortOrder": d.sort_order, "status": d.status} for d in dicts
    ])


# ── Config ───────────────────────────────────────────────────────────

@router.get("/config")
async def list_config(db: AsyncSession = Depends(get_db)):
    stmt = select(Config)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"configId": c.config_id, "configKey": c.config_key, "configValue": c.config_value,
         "description": c.description} for c in configs
    ])


@router.put("/config/{config_key}")
async def update_config(config_key: str, req: ConfigUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Config).where(Config.config_key == config_key)
    cfg = (await db.execute(stmt)).scalar_one_or_none()
    if not cfg:
        cfg = Config(config_id=str(uuid.uuid4()), config_key=config_key)
        db.add(cfg)
    cfg.config_value = req.config_value
    cfg.description = req.description
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Announcements ────────────────────────────────────────────────────

@router.get("/announcements")
async def list_announcements(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Announcement).order_by(Announcement.create_time.desc())
    total_stmt = select(func.count()).select_from(Announcement)
    total = (await db.execute(total_stmt)).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"announcementId": a.announcement_id, "title": a.title,
                 "content": a.content, "type": a.type, "status": a.status,
                 "publisherId": a.publisher_id, "publishTime": str(a.publish_time) if a.publish_time else None}
               for a in items],
    ))


@router.post("/announcements")
async def create_announcement(req: AnnouncementCreateRequest, db: AsyncSession = Depends(get_db)):
    ann = Announcement(
        announcement_id=str(uuid.uuid4()), title=req.title, content=req.content,
        type=req.type, status=req.status or 1, publisher_id=req.publisher_id,
        publish_time=req.publish_time,
    )
    db.add(ann)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"announcementId": ann.announcement_id})


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str, req: AnnouncementUpdateRequest, db: AsyncSession = Depends(get_db),
):
    stmt = select(Announcement).where(Announcement.announcement_id == announcement_id)
    ann = (await db.execute(stmt)).scalar_one_or_none()
    if not ann:
        raise ResourceNotFoundError("公告", announcement_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(ann, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(announcement_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Announcement).where(Announcement.announcement_id == announcement_id)
    ann = (await db.execute(stmt)).scalar_one_or_none()
    if not ann:
        raise ResourceNotFoundError("公告", announcement_id)
    await db.delete(ann)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Assets ───────────────────────────────────────────────────────────

@router.get("/assets")
async def list_assets(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Asset).order_by(Asset.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(Asset))).scalar() or 0
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"assetId": a.asset_id, "assetName": a.asset_name, "assetType": a.asset_type,
                 "assetCode": a.asset_code, "ownerId": a.owner_id, "location": a.location,
                 "status": a.status} for a in items],
    ))


@router.post("/assets")
async def create_asset(req: AssetCreateRequest, db: AsyncSession = Depends(get_db)):
    asset = Asset(
        asset_id=str(uuid.uuid4()), asset_name=req.asset_name, asset_type=req.asset_type,
        asset_code=req.asset_code, owner_id=req.owner_id, location=req.location,
        status=req.status or "active",
    )
    db.add(asset)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"assetId": asset.asset_id})


# ── Meetings ─────────────────────────────────────────────────────────

@router.get("/meetings")
async def list_meetings(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Meeting).order_by(Meeting.create_time.desc())
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"meetingId": m.meeting_id, "meetingName": m.meeting_name, "meetingType": m.meeting_type,
         "startTime": str(m.start_time) if m.start_time else None,
         "endTime": str(m.end_time) if m.end_time else None,
         "location": m.location, "organizerId": m.organizer_id, "status": m.status} for m in items
    ])


@router.post("/meetings")
async def create_meeting(req: MeetingCreateRequest, db: AsyncSession = Depends(get_db)):
    meeting = Meeting(
        meeting_id=str(uuid.uuid4()), meeting_name=req.meeting_name,
        meeting_type=req.meeting_type, start_time=req.start_time,
        end_time=req.end_time, location=req.location, organizer_id=req.organizer_id,
        participants=req.participants, status=req.status,
    )
    db.add(meeting)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"meetingId": meeting.meeting_id})


# ── Review Meetings ──────────────────────────────────────────────────

@router.get("/review-meetings")
async def list_review_meetings(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(ReviewMeeting).order_by(ReviewMeeting.create_time.desc())
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"reviewId": r.review_id, "projectId": r.project_id, "reviewType": r.review_type,
         "reviewDate": str(r.review_date) if r.review_date else None,
         "reviewerId": r.reviewer_id, "conclusion": r.conclusion} for r in items
    ])


@router.post("/review-meetings")
async def create_review_meeting(req: ReviewMeetingCreateRequest, db: AsyncSession = Depends(get_db)):
    rm = ReviewMeeting(
        review_id=str(uuid.uuid4()), project_id=req.project_id,
        review_type=req.review_type, review_date=req.review_date,
        reviewer_id=req.reviewer_id, conclusion=req.conclusion,
    )
    db.add(rm)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"reviewId": rm.review_id})


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/users/list")
async def list_users_alias(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    username: str | None = None,
    name: str | None = None,
    dept_id: str | None = Query(None, alias="deptId"),
    db: AsyncSession = Depends(get_db),
):
    return await list_users(page=page, size=size, username=username, name=name, dept_id=dept_id, db=db)


@router.post("/users/create")
async def create_user_alias(req: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_user(req, db)


@router.get("/roles/list")
async def list_roles_alias(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_roles(page=page, size=size, db=db)


@router.post("/roles/create")
async def create_role_alias(req: RoleCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_role(req, db)


@router.get("/roles/all")
async def list_all_roles(db: AsyncSession = Depends(get_db)):
    stmt = select(Role).where(Role.status == 1).order_by(Role.role_code)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"roleId": r.role_id, "roleName": r.role_name, "roleCode": r.role_code,
         "description": r.description, "status": r.status} for r in roles
    ])


@router.get("/depts/tree")
async def depts_tree(db: AsyncSession = Depends(get_db)):
    stmt = select(Dept).where(Dept.status == 1).order_by(Dept.sort_order)
    result = await db.execute(stmt)
    depts = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"deptId": d.dept_id, "deptName": d.dept_name, "parentId": d.parent_id,
         "leaderId": d.leader_id, "sortOrder": d.sort_order, "status": d.status} for d in depts
    ])


@router.post("/depts/create")
async def create_dept_alias(req: DeptCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_dept(req, db)


@router.get("/permissions/tree")
async def permissions_tree(db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).order_by(Permission.permission_code)
    result = await db.execute(stmt)
    perms = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[_permission_to_dict(p) for p in perms])


@router.get("/permissions/role/{role_id}")
async def get_role_perms_alias(role_id: str, db: AsyncSession = Depends(get_db)):
    return await get_role_permissions(role_id, db)


@router.post("/permissions/create")
async def create_permission(req: PermissionCreateRequest, db: AsyncSession = Depends(get_db)):
    perm = Permission(
        permission_id=str(uuid.uuid4()), permission_name=req.permission_name,
        permission_code=req.permission_code, permission_type=req.permission_type,
        parent_id=req.parent_id, path=req.path, sort_order=req.sort_order or 0,
        status=req.status or 1,
    )
    db.add(perm)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"permissionId": perm.permission_id})


@router.get("/announcements/list")
async def list_announcements_alias(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_announcements(page=page, size=size, db=db)


@router.post("/announcements/create")
async def create_announcement_alias(req: AnnouncementCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_announcement(req, db)


# ── Singular path aliases (frontend uses singular: /user/*, /role/*, etc.) ──

@router.get("/user/list")
async def user_list(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    username: str | None = None, name: str | None = None,
    dept_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    return await list_users(page=page, size=size, username=username, name=name, dept_id=dept_id, db=db)


@router.post("/user/create")
async def user_create(req: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_user(req, db)


@router.put("/user/{user_id}")
async def user_update(user_id: str, req: UserUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_user(user_id, req, db)


@router.delete("/user/{user_id}")
async def user_delete(user_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_user(user_id, db)


@router.put("/user/{user_id}/roles")
async def user_set_roles(user_id: str, req: UserRolesRequest, db: AsyncSession = Depends(get_db)):
    return await set_user_roles(user_id, req, db)


@router.get("/role/list")
async def role_list(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
                    db: AsyncSession = Depends(get_db)):
    return await list_roles(page=page, size=size, db=db)


@router.get("/role/all")
async def role_all(db: AsyncSession = Depends(get_db)):
    return await list_all_roles(db=db)


@router.post("/role/create")
async def role_create(req: RoleCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_role(req, db)


@router.put("/role/{role_id}")
async def role_update(role_id: str, req: RoleUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_role(role_id, req, db)


@router.delete("/role/{role_id}")
async def role_delete(role_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_role(role_id, db)


@router.put("/role/{role_id}/permissions")
async def role_set_perms(role_id: str, req: RolePermissionsRequest, db: AsyncSession = Depends(get_db)):
    return await set_role_permissions(role_id, req, db)


@router.get("/permission/tree")
async def perm_tree(db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).order_by(Permission.permission_code)
    result = await db.execute(stmt)
    perms = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[_permission_to_dict(p) for p in perms])


@router.get("/permission/role/{role_id}")
async def perm_by_role(role_id: str, db: AsyncSession = Depends(get_db)):
    return await get_role_permissions(role_id, db)


@router.post("/permission/create")
async def perm_create(req: PermissionCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_permission(req, db)


@router.put("/permission/{permission_id}")
async def perm_update(permission_id: str, req: PermissionCreateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).where(Permission.permission_id == permission_id)
    p = (await db.execute(stmt)).scalar_one_or_none()
    if not p:
        raise ResourceNotFoundError("权限", permission_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/permission/{permission_id}")
async def perm_delete(permission_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Permission).where(Permission.permission_id == permission_id)
    p = (await db.execute(stmt)).scalar_one_or_none()
    if not p:
        raise ResourceNotFoundError("权限", permission_id)
    await db.delete(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/dept/tree")
async def dept_tree(db: AsyncSession = Depends(get_db)):
    return await depts_tree(db=db)


@router.post("/dept/create")
async def dept_create(req: DeptCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_dept(req, db)


@router.put("/dept/{dept_id}")
async def dept_update(dept_id: str, req: DeptUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_dept(dept_id, req, db)


@router.delete("/dept/{dept_id}")
async def dept_delete(dept_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_dept(dept_id, db)


@router.get("/announcement/list")
async def announcement_list(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
                            db: AsyncSession = Depends(get_db)):
    return await list_announcements(page=page, size=size, db=db)


@router.post("/announcement/create")
async def announcement_create(req: AnnouncementCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_announcement(req, db)


@router.put("/announcement/{announcement_id}")
async def announcement_update(announcement_id: str, req: AnnouncementUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_announcement(announcement_id, req, db)


@router.delete("/announcement/{announcement_id}")
async def announcement_delete(announcement_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_announcement(announcement_id, db)


@router.post("/announcement/{announcement_id}/publish")
async def announcement_publish(announcement_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Announcement).where(Announcement.announcement_id == announcement_id)
    ann = (await db.execute(stmt)).scalar_one_or_none()
    if not ann:
        raise ResourceNotFoundError("公告", announcement_id)
    ann.status = 2  # published
    ann.publish_time = datetime.now(timezone.utc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="发布成功")


# ── Dashboard ────────────────────────────────────────────────────────

@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    from app.models.project.models import Project
    from app.models.business.models import Contract
    total_projects = (await db.execute(select(func.count()).select_from(Project))).scalar() or 0
    active_projects = (await db.execute(select(func.count()).select_from(Project).where(Project.status == "active"))).scalar() or 0
    total_contracts = (await db.execute(select(func.count()).select_from(Contract))).scalar() or 0
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    return ApiResponse(code="SUCCESS", message="success", data={
        "totalProjects": total_projects, "activeProjects": active_projects,
        "totalContracts": total_contracts, "totalUsers": total_users,
    })


# ── System Auth (frontend uses /system/auth/*) ───────────────────────

@router.post("/auth/login")
async def system_login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    from app.core.security import create_token, create_refresh_token, verify_password
    stmt = select(User).where(User.username == req.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password):
        raise ValidationError("用户名或密码错误")
    if user.status != 1:
        raise BusinessError(code="USER_DISABLED", message="账号已被禁用", status_code=400)
    access_token = create_token(user.user_id, {"role": "admin" if user.dept_id == "1" else "user"})
    refresh_token = create_refresh_token(user.user_id)
    decrypted = user.decrypt_fields()
    return ApiResponse(code="SUCCESS", message="success", data={
        "token": access_token, "refreshToken": refresh_token,
        "userInfo": {"userId": user.user_id, "username": user.username, "name": user.name or user.username,
                     "deptId": user.dept_id, "email": user.email,
                     "phone": decrypted.get("phone", user.phone)},
    })


@router.get("/auth/captcha")
async def system_captcha():
    """Placeholder captcha — not required in dev."""
    return ApiResponse(code="SUCCESS", message="success", data={"captchaId": "dev", "captchaImage": ""})


@router.post("/auth/logout")
async def system_logout():
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/auth/info")
async def system_auth_info(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, current_user["user_id"])
    if not user:
        raise ResourceNotFoundError("User", current_user["user_id"])
    decrypted = user.decrypt_fields()
    return ApiResponse(code="SUCCESS", message="success", data={
        "userId": user.user_id, "username": user.username, "name": user.name,
        "deptId": user.dept_id, "email": user.email,
        "phone": decrypted.get("phone", user.phone),
        "status": user.status,
    })


# ── Helper ───────────────────────────────────────────────────────────

async def _get_user_or_404(db: AsyncSession, user_id: str) -> User:
    stmt = select(User).where(User.user_id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise ResourceNotFoundError("用户", user_id)
    return user


# ── Request schemas ──────────────────────────────────────────────────

class UserCreateRequest(BaseModel):
    username: str
    password: str
    name: str | None = None
    dept_id: str | None = None
    email: str | None = None
    phone: str | None = None
    status: int | None = None


class UserLoginRequest(BaseModel):
    username: str
    password: str
    captcha: str | None = None

class UserUpdateRequest(BaseModel):
    name: str | None = None
    dept_id: str | None = None
    email: str | None = None
    phone: str | None = None
    status: int | None = None

class RoleCreateRequest(BaseModel):
    role_name: str
    role_code: str
    description: str | None = None
    status: int | None = None

class RoleUpdateRequest(BaseModel):
    role_name: str | None = None
    role_code: str | None = None
    description: str | None = None
    status: int | None = None

class RolePermissionsRequest(BaseModel):
    permission_ids: list[str]

class UserRolesRequest(BaseModel):
    role_ids: list[str]

class DeptCreateRequest(BaseModel):
    dept_name: str
    parent_id: str | None = None
    leader_id: str | None = None
    sort_order: int | None = None
    status: int | None = None

class DeptUpdateRequest(BaseModel):
    dept_name: str | None = None
    parent_id: str | None = None
    leader_id: str | None = None
    sort_order: int | None = None
    status: int | None = None

class ConfigUpdateRequest(BaseModel):
    config_value: str | None = None
    description: str | None = None

class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str | None = None
    type: str | None = None
    status: int | None = None
    publisher_id: str | None = None
    publish_time: datetime | None = None

class AnnouncementUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    type: str | None = None
    status: int | None = None
    publisher_id: str | None = None
    publish_time: datetime | None = None

class AssetCreateRequest(BaseModel):
    asset_name: str
    asset_type: str | None = None
    asset_code: str | None = None
    owner_id: str | None = None
    location: str | None = None
    status: str | None = None

class MeetingCreateRequest(BaseModel):
    meeting_name: str
    meeting_type: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    organizer_id: str | None = None
    participants: str | None = None
    status: str | None = None

class ReviewMeetingCreateRequest(BaseModel):
    project_id: str | None = None
    review_type: str | None = None
    review_date: datetime | None = None
    reviewer_id: str | None = None
    conclusion: str | None = None
