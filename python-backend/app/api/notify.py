"""Notify API router — consolidates message and template controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.notify.models import NotifyMessage, NotifyPreference, NotifyTemplate

router = APIRouter(tags=["notify"])


# ── Messages ─────────────────────────────────────────────────────────

@router.get("/messages")
async def list_messages(
    receiver_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(NotifyMessage).order_by(NotifyMessage.send_time.desc())
    if receiver_id:
        stmt = stmt.where(NotifyMessage.receiver_id == receiver_id)
    if status:
        stmt = stmt.where(NotifyMessage.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"messageId": m.message_id, "title": m.title, "content": m.content,
                 "type": m.type, "senderId": m.sender_id, "receiverId": m.receiver_id,
                 "status": m.status, "sendTime": str(m.send_time) if m.send_time else None,
                 "readTime": str(m.read_time) if m.read_time else None} for m in items],
    ))


@router.post("/messages")
async def send_message(req: MessageSendRequest, db: AsyncSession = Depends(get_db)):
    msg = NotifyMessage(
        message_id=str(uuid.uuid4()), title=req.title, content=req.content,
        type=req.type, sender_id=req.sender_id, receiver_id=req.receiver_id,
        status="unread", send_time=datetime.now(timezone.utc),
    )
    db.add(msg)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"messageId": msg.message_id})


@router.post("/messages/{message_id}/read")
async def mark_read(message_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyMessage).where(NotifyMessage.message_id == message_id)
    msg = (await db.execute(stmt)).scalar_one_or_none()
    if not msg:
        raise ResourceNotFoundError("消息", message_id)
    msg.status = "read"
    msg.read_time = datetime.now(timezone.utc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Templates ────────────────────────────────────────────────────────

@router.get("/templates")
async def list_templates(db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"templateId": t.template_id, "templateName": t.template_name,
         "templateCode": t.template_code, "templateContent": t.template_content,
         "type": t.type, "status": t.status, "channel": getattr(t, "channel", None)} for t in items
    ])


@router.get("/templates/{template_id}")
async def get_template(template_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.template_id == template_id)
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise ResourceNotFoundError("通知模板", template_id)
    return ApiResponse(code="SUCCESS", message="success", data={
        "templateId": t.template_id, "templateName": t.template_name,
        "templateCode": t.template_code, "templateContent": t.template_content,
        "type": t.type, "status": t.status,
        "channel": getattr(t, "channel", None),
        "createTime": str(t.create_time) if hasattr(t, "create_time") and t.create_time else None,
    })


@router.get("/templates/channel/{channel}")
async def list_templates_by_channel(channel: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.type == channel)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"templateId": t.template_id, "templateName": t.template_name,
         "templateCode": t.template_code, "templateContent": t.template_content,
         "type": t.type, "status": t.status} for t in items
    ])


@router.get("/templates/active")
async def list_active_templates(db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.status == "active")
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"templateId": t.template_id, "templateName": t.template_name,
         "templateCode": t.template_code, "templateContent": t.template_content,
         "type": t.type, "status": t.status} for t in items
    ])


@router.post("/templates/{template_id}/activate")
async def activate_template(template_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.template_id == template_id)
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise ResourceNotFoundError("通知模板", template_id)
    t.status = "active"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="模板已启用")


@router.post("/templates/{template_id}/deactivate")
async def deactivate_template(template_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.template_id == template_id)
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise ResourceNotFoundError("通知模板", template_id)
    t.status = "inactive"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="模板已停用")


@router.put("/templates/{template_id}")
async def update_template(template_id: str, req: TemplateUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.template_id == template_id)
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise ResourceNotFoundError("通知模板", template_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyTemplate).where(NotifyTemplate.template_id == template_id)
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise ResourceNotFoundError("通知模板", template_id)
    await db.delete(t)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/templates")
async def create_template(req: TemplateCreateRequest, db: AsyncSession = Depends(get_db)):
    t = NotifyTemplate(
        template_id=str(uuid.uuid4()), template_name=req.template_name,
        template_code=req.template_code, template_content=req.template_content,
        type=req.type, status=req.status or "active",
    )
    db.add(t)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"templateId": t.template_id})


# ── Preferences ──────────────────────────────────────────────────────

@router.get("/preferences")
async def list_preferences(user_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(NotifyPreference)
    if user_id:
        stmt = stmt.where(NotifyPreference.user_id == user_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"prefId": p.pref_id, "userId": p.user_id, "notifyType": p.notify_type,
         "enabled": p.enabled, "channel": p.channel} for p in items
    ])


@router.post("/preferences")
async def create_preference(req: PreferenceCreateRequest, db: AsyncSession = Depends(get_db)):
    p = NotifyPreference(
        pref_id=str(uuid.uuid4()), user_id=req.user_id,
        notify_type=req.notify_type, enabled=req.enabled or 1,
        channel=req.channel,
    )
    db.add(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"prefId": p.pref_id})


# ── Request schemas ──────────────────────────────────────────────────

class MessageSendRequest(BaseModel):
    title: str
    content: str | None = None
    type: str | None = None
    sender_id: str | None = None
    receiver_id: str | None = None

class TemplateCreateRequest(BaseModel):
    template_name: str
    template_code: str | None = None
    template_content: str | None = None
    type: str | None = None
    status: str | None = None

class TemplateUpdateRequest(BaseModel):
    template_name: str | None = None
    template_code: str | None = None
    template_content: str | None = None
    type: str | None = None
    status: str | None = None

class PreferenceCreateRequest(BaseModel):
    user_id: str
    notify_type: str | None = None
    enabled: int | None = None
    channel: str | None = None
