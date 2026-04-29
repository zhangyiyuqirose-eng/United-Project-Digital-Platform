"""Notify domain service — messages, templates, user preferences."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError
from app.models.notify.models import NotifyMessage, NotifyPreference, NotifyTemplate


def _now() -> datetime:
    return datetime.now(timezone.utc)


class NotifyService:
    """Encapsulates all notification-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Message ─────────────────────────────────────────────────────────

    async def list_messages(
        self, receiver_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(NotifyMessage)
        if receiver_id:
            base = base.where(NotifyMessage.receiver_id == receiver_id)
        base = base.order_by(NotifyMessage.send_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_message_dict(m) for m in result.scalars().all()],
        )

    async def list_unread(
        self, user_id: str, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(NotifyMessage).where(
            NotifyMessage.receiver_id == user_id,
            NotifyMessage.status == "unread",
        ).order_by(NotifyMessage.send_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_message_dict(m) for m in result.scalars().all()],
        )

    async def get_message(self, message_id: str) -> dict[str, object]:
        m = await self._get_message_or_404(message_id)
        return _message_dict(m)

    async def send(
        self,
        to_user_id: str,
        title: str,
        content: str,
        msg_type: str = "system",
        sender_id: str | None = None,
    ) -> dict[str, str]:
        """Send a notification message to a user."""
        msg = NotifyMessage(
            message_id=str(uuid.uuid4()),
            title=title,
            content=content,
            type=msg_type,
            sender_id=sender_id,
            receiver_id=to_user_id,
            status="unread",
            send_time=_now(),
        )
        self.db.add(msg)
        await self.db.flush()
        return {"messageId": msg.message_id, "status": "sent"}

    async def mark_read(self, message_id: str) -> dict[str, str]:
        m = await self._get_message_or_404(message_id)
        m.status = "read"
        m.read_time = _now()
        await self.db.flush()
        return {"messageId": message_id, "status": "read"}

    async def delete_message(self, message_id: str) -> None:
        m = await self._get_message_or_404(message_id)
        await self.db.delete(m)
        await self.db.flush()

    async def unread_count(self, user_id: str) -> dict[str, int]:
        stmt = select(func.count()).select_from(NotifyMessage).where(
            NotifyMessage.receiver_id == user_id, NotifyMessage.status == "unread"
        )
        count = (await self.db.execute(stmt)).scalar() or 0
        return {"userId": user_id, "unreadCount": count}

    # ── Template ────────────────────────────────────────────────────────

    async def list_templates(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(NotifyTemplate)
        if status:
            base = base.where(NotifyTemplate.status == status)
        base = base.order_by(NotifyTemplate.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_notify_template_dict(t) for t in result.scalars().all()],
        )

    async def get_template(self, template_id: str) -> dict[str, object]:
        t = await self._get_notify_template_or_404(template_id)
        return _notify_template_dict(t)

    async def get_template_by_code(self, template_code: str) -> dict[str, object] | None:
        stmt = select(NotifyTemplate).where(
            NotifyTemplate.template_code == template_code
        )
        result = await self.db.execute(stmt)
        t = result.scalar_one_or_none()
        if not t:
            return None
        return _notify_template_dict(t)

    async def get_templates_by_channel(
        self, channel: str
    ) -> list[dict[str, object]]:
        """Return active templates whose type matches the given channel."""
        stmt = (
            select(NotifyTemplate)
            .where(
                NotifyTemplate.type == channel,
                NotifyTemplate.status == "active",
            )
            .order_by(NotifyTemplate.create_time.desc())
        )
        result = await self.db.execute(stmt)
        return [_notify_template_dict(t) for t in result.scalars().all()]

    async def create_template(self, **kwargs: object) -> dict[str, str]:
        t = NotifyTemplate(template_id=str(uuid.uuid4()), **kwargs)
        self.db.add(t)
        await self.db.flush()
        return {"templateId": t.template_id}

    async def update_template(self, template_id: str, **kwargs: object) -> None:
        t = await self._get_notify_template_or_404(template_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(t, k):
                setattr(t, k, v)
        await self.db.flush()

    async def delete_template(self, template_id: str) -> None:
        t = await self._get_notify_template_or_404(template_id)
        await self.db.delete(t)
        await self.db.flush()

    async def activate_template(self, template_id: str) -> dict[str, str]:
        t = await self._get_notify_template_or_404(template_id)
        t.status = "active"
        await self.db.flush()
        return {"templateId": template_id, "status": "active"}

    async def deactivate_template(self, template_id: str) -> dict[str, str]:
        t = await self._get_notify_template_or_404(template_id)
        t.status = "inactive"
        await self.db.flush()
        return {"templateId": template_id, "status": "inactive"}

    # ── Preference ──────────────────────────────────────────────────────

    async def list_preferences(
        self, user_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(NotifyPreference)
        if user_id:
            base = base.where(NotifyPreference.user_id == user_id)
        base = base.order_by(NotifyPreference.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_preference_dict(p) for p in result.scalars().all()],
        )

    async def get_user_preferences(self, user_id: str) -> list[dict[str, object]]:
        stmt = (
            select(NotifyPreference)
            .where(NotifyPreference.user_id == user_id)
            .order_by(NotifyPreference.create_time.desc())
        )
        result = await self.db.execute(stmt)
        return [_preference_dict(p) for p in result.scalars().all()]

    async def get_preference(self, pref_id: str) -> dict[str, object]:
        p = await self._get_preference_or_404(pref_id)
        return _preference_dict(p)

    async def create_preference(self, **kwargs: object) -> dict[str, str]:
        p = NotifyPreference(pref_id=str(uuid.uuid4()), **kwargs)
        self.db.add(p)
        await self.db.flush()
        return {"prefId": p.pref_id}

    async def update_preference(self, pref_id: str, **kwargs: object) -> None:
        p = await self._get_preference_or_404(pref_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(p, k):
                setattr(p, k, v)
        await self.db.flush()

    async def delete_preference(self, pref_id: str) -> None:
        p = await self._get_preference_or_404(pref_id)
        await self.db.delete(p)
        await self.db.flush()

    # ── Internal helpers ────────────────────────────────────────────────

    async def _get_message_or_404(self, message_id: str) -> NotifyMessage:
        m = await self.db.get(NotifyMessage, message_id)
        if not m:
            raise ResourceNotFoundError("通知消息", message_id)
        return m

    async def _get_notify_template_or_404(self, template_id: str) -> NotifyTemplate:
        t = await self.db.get(NotifyTemplate, template_id)
        if not t:
            raise ResourceNotFoundError("通知模板", template_id)
        return t

    async def _get_preference_or_404(self, pref_id: str) -> NotifyPreference:
        p = await self.db.get(NotifyPreference, pref_id)
        if not p:
            raise ResourceNotFoundError("通知偏好", pref_id)
        return p


# ── Dict converters ──────────────────────────────────────────────────────

def _message_dict(m: NotifyMessage) -> dict[str, object]:
    return {
        "messageId": m.message_id, "title": m.title,
        "content": m.content, "type": m.type,
        "senderId": m.sender_id, "receiverId": m.receiver_id,
        "status": m.status,
        "sendTime": m.send_time.isoformat() if m.send_time else None,
        "readTime": m.read_time.isoformat() if m.read_time else None,
    }


def _notify_template_dict(t: NotifyTemplate) -> dict[str, object]:
    return {
        "templateId": t.template_id, "templateName": t.template_name,
        "templateCode": t.template_code, "templateContent": t.template_content,
        "type": t.type, "status": t.status,
    }


def _preference_dict(p: NotifyPreference) -> dict[str, object]:
    return {
        "prefId": p.pref_id, "userId": p.user_id,
        "notifyType": p.notify_type, "enabled": bool(p.enabled),
        "channel": p.channel,
    }
