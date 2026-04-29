"""Knowledge domain service — docs, templates, reviews, compliance, versions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.knowledge.models import (
    ComplianceChecklist,
    DocumentVersion,
    KnowledgeDoc,
    KnowledgeReview,
    KnowledgeTemplate,
    Policy,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeService:
    """Encapsulates all knowledge-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Knowledge Document ──────────────────────────────────────────────

    async def list_docs(
        self, page: int = 1, size: int = 20,
        doc_type: str | None = None, status: str | None = None,
    ) -> PageResult:
        base = select(KnowledgeDoc)
        if doc_type:
            base = base.where(KnowledgeDoc.doc_type == doc_type)
        if status:
            base = base.where(KnowledgeDoc.status == status)
        base = base.order_by(KnowledgeDoc.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_doc_dict(d) for d in result.scalars().all()],
        )

    async def search_docs(
        self, keyword: str, page: int = 1, size: int = 20
    ) -> PageResult:
        pattern = f"%{keyword}%"
        base = select(KnowledgeDoc).where(
            KnowledgeDoc.title.ilike(pattern)
            | (KnowledgeDoc.content.ilike(pattern))
            | (KnowledgeDoc.category.ilike(pattern))
        )
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.order_by(KnowledgeDoc.create_time.desc()).offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_doc_dict(d) for d in result.scalars().all()],
        )

    async def get_doc(self, doc_id: str) -> dict[str, object]:
        d = await self._get_doc_or_404(doc_id)
        return _doc_dict(d)

    async def create_doc(self, **kwargs: object) -> dict[str, str]:
        doc = KnowledgeDoc(
            doc_id=str(uuid.uuid4()),
            version_num=kwargs.pop("version_num", 1),
            version=kwargs.pop("version", "1.0"),
            **kwargs,
        )
        self.db.add(doc)
        await self.db.flush()
        return {"docId": doc.doc_id}

    async def update_doc(self, doc_id: str, **kwargs: object) -> None:
        d = await self._get_doc_or_404(doc_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(d, k):
                setattr(d, k, v)
        await self.db.flush()

    async def delete_doc(self, doc_id: str) -> None:
        d = await self._get_doc_or_404(doc_id)
        await self.db.delete(d)
        await self.db.flush()

    async def publish_doc(self, doc_id: str) -> dict[str, str]:
        d = await self._get_doc_or_404(doc_id)
        d.status = "published"
        d.publish_time = _now()
        await self.db.flush()
        return {"docId": doc_id, "status": d.status}

    # ── Document Versions ───────────────────────────────────────────────

    async def create_version(
        self, doc_id: str, content: str, created_by: str | None = None
    ) -> dict[str, str]:
        """Create a new version snapshot of a document."""
        doc = await self._get_doc_or_404(doc_id)
        new_ver_num = (doc.version_num or 0) + 1
        new_ver_str = f"{new_ver_num}.0"

        dv = DocumentVersion(
            version_id=str(uuid.uuid4()),
            doc_id=doc_id,
            version=new_ver_str,
            version_num=new_ver_num,
            content=content,
            created_by=created_by,
        )
        self.db.add(dv)

        # Update the parent doc's version pointer
        doc.version = new_ver_str
        doc.version_num = new_ver_num
        doc.content = content
        await self.db.flush()
        return {"versionId": dv.version_id, "version": new_ver_str}

    async def list_versions(self, doc_id: str) -> list[dict[str, object]]:
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.doc_id == doc_id)
            .order_by(DocumentVersion.version_num.desc())
        )
        result = await self.db.execute(stmt)
        return [_version_dict(v) for v in result.scalars().all()]

    # ── Knowledge Template ──────────────────────────────────────────────

    async def list_templates(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(KnowledgeTemplate)
        if status:
            base = base.where(KnowledgeTemplate.status == status)
        base = base.order_by(KnowledgeTemplate.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_template_dict(t) for t in result.scalars().all()],
        )

    async def list_active_templates(self) -> list[dict[str, object]]:
        stmt = (
            select(KnowledgeTemplate)
            .where(KnowledgeTemplate.status == "active")
            .order_by(KnowledgeTemplate.create_time.desc())
        )
        result = await self.db.execute(stmt)
        return [_template_dict(t) for t in result.scalars().all()]

    async def get_template(self, template_id: str) -> dict[str, object]:
        t = await self._get_template_or_404(template_id)
        return _template_dict(t)

    async def create_template(self, **kwargs: object) -> dict[str, str]:
        t = KnowledgeTemplate(template_id=str(uuid.uuid4()), **kwargs)
        self.db.add(t)
        await self.db.flush()
        return {"templateId": t.template_id}

    async def update_template(self, template_id: str, **kwargs: object) -> None:
        t = await self._get_template_or_404(template_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(t, k):
                setattr(t, k, v)
        await self.db.flush()

    async def delete_template(self, template_id: str) -> None:
        t = await self._get_template_or_404(template_id)
        await self.db.delete(t)
        await self.db.flush()

    # ── Knowledge Review ────────────────────────────────────────────────

    async def list_reviews(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(KnowledgeReview)
        if status:
            base = base.where(KnowledgeReview.review_status == status)
        base = base.order_by(KnowledgeReview.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_review_dict(r) for r in result.scalars().all()],
        )

    async def list_pending_reviews(self, page: int = 1, size: int = 20) -> PageResult:
        return await self.list_reviews(page=page, size=size, status="pending")

    async def get_review(self, review_id: str) -> dict[str, object]:
        r = await self._get_review_or_404(review_id)
        return _review_dict(r)

    async def create_review(self, **kwargs: object) -> dict[str, str]:
        r = KnowledgeReview(review_id=str(uuid.uuid4()), **kwargs)
        self.db.add(r)
        await self.db.flush()
        return {"reviewId": r.review_id}

    async def update_review(self, review_id: str, **kwargs: object) -> None:
        r = await self._get_review_or_404(review_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(r, k):
                setattr(r, k, v)
        await self.db.flush()

    async def approve_review(
        self, review_id: str, reviewer_id: str, comments: str | None = None
    ) -> dict[str, str]:
        r = await self._get_review_or_404(review_id)
        r.review_status = "approved"
        r.reviewer_id = reviewer_id
        if comments:
            r.comments = comments
        await self.db.flush()
        # If the doc has a related document, update its status
        await self._sync_doc_status_from_review(r.doc_id)
        return {"reviewId": review_id, "status": "approved"}

    async def reject_review(
        self, review_id: str, reviewer_id: str, comments: str | None = None
    ) -> dict[str, str]:
        r = await self._get_review_or_404(review_id)
        r.review_status = "rejected"
        r.reviewer_id = reviewer_id
        if comments:
            r.comments = comments
        await self.db.flush()
        return {"reviewId": review_id, "status": "rejected"}

    async def _sync_doc_status_from_review(self, doc_id: str) -> None:
        """If all reviews for a doc are approved, mark the doc as reviewed."""
        stmt = select(func.count()).select_from(KnowledgeReview).where(
            KnowledgeReview.doc_id == doc_id,
            KnowledgeReview.review_status != "approved",
        )
        pending = (await self.db.execute(stmt)).scalar() or 0
        if pending == 0:
            doc = await self.db.get(KnowledgeDoc, doc_id)
            if doc and doc.status == "draft":
                doc.status = "reviewed"
                await self.db.flush()

    async def delete_review(self, review_id: str) -> None:
        r = await self._get_review_or_404(review_id)
        await self.db.delete(r)
        await self.db.flush()

    # ── Compliance Checklist ────────────────────────────────────────────

    async def list_checklists(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(ComplianceChecklist)
        if project_id:
            base = base.where(ComplianceChecklist.project_id == project_id)
        base = base.order_by(ComplianceChecklist.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_checklist_dict(c) for c in result.scalars().all()],
        )

    async def get_checklist(self, checklist_id: str) -> dict[str, object]:
        c = await self._get_checklist_or_404(checklist_id)
        return _checklist_dict(c)

    async def create_checklist(self, **kwargs: object) -> dict[str, str]:
        c = ComplianceChecklist(checklist_id=str(uuid.uuid4()), **kwargs)
        self.db.add(c)
        await self.db.flush()
        return {"checklistId": c.checklist_id}

    async def update_checklist(self, checklist_id: str, **kwargs: object) -> None:
        c = await self._get_checklist_or_404(checklist_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(c, k):
                setattr(c, k, v)
        await self.db.flush()

    async def delete_checklist(self, checklist_id: str) -> None:
        c = await self._get_checklist_or_404(checklist_id)
        await self.db.delete(c)
        await self.db.flush()

    # ── Policies ────────────────────────────────────────────────────────

    async def list_policies(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(Policy)
        if status:
            base = base.where(Policy.status == status)
        base = base.order_by(Policy.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_policy_dict(p) for p in result.scalars().all()],
        )

    async def get_policy(self, policy_id: str) -> dict[str, object]:
        p = await self._get_policy_or_404(policy_id)
        return _policy_dict(p)

    async def create_policy(self, **kwargs: object) -> dict[str, str]:
        p = Policy(policy_id=str(uuid.uuid4()), **kwargs)
        self.db.add(p)
        await self.db.flush()
        return {"policyId": p.policy_id}

    async def update_policy(self, policy_id: str, **kwargs: object) -> None:
        p = await self._get_policy_or_404(policy_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(p, k):
                setattr(p, k, v)
        await self.db.flush()

    async def delete_policy(self, policy_id: str) -> None:
        p = await self._get_policy_or_404(policy_id)
        await self.db.delete(p)
        await self.db.flush()

    # ── Internal helpers ────────────────────────────────────────────────

    async def _get_doc_or_404(self, doc_id: str) -> KnowledgeDoc:
        d = await self.db.get(KnowledgeDoc, doc_id)
        if not d:
            raise ResourceNotFoundError("知识文档", doc_id)
        return d

    async def _get_template_or_404(self, template_id: str) -> KnowledgeTemplate:
        t = await self.db.get(KnowledgeTemplate, template_id)
        if not t:
            raise ResourceNotFoundError("知识模板", template_id)
        return t

    async def _get_review_or_404(self, review_id: str) -> KnowledgeReview:
        r = await self.db.get(KnowledgeReview, review_id)
        if not r:
            raise ResourceNotFoundError("知识审核", review_id)
        return r

    async def _get_checklist_or_404(self, checklist_id: str) -> ComplianceChecklist:
        c = await self.db.get(ComplianceChecklist, checklist_id)
        if not c:
            raise ResourceNotFoundError("合规清单", checklist_id)
        return c

    async def _get_policy_or_404(self, policy_id: str) -> Policy:
        p = await self.db.get(Policy, policy_id)
        if not p:
            raise ResourceNotFoundError("制度", policy_id)
        return p


# ── Dict converters ──────────────────────────────────────────────────────

def _doc_dict(d: KnowledgeDoc) -> dict[str, object]:
    return {
        "docId": d.doc_id, "title": d.title,
        "docType": d.doc_type, "templateType": d.template_type,
        "category": d.category, "content": d.content,
        "authorId": d.author_id, "createdBy": d.created_by,
        "version": d.version, "versionNum": d.version_num,
        "filePath": d.file_path, "status": d.status,
        "publishTime": d.publish_time.isoformat() if d.publish_time else None,
    }


def _template_dict(t: KnowledgeTemplate) -> dict[str, object]:
    return {
        "templateId": t.template_id, "templateName": t.template_name,
        "templateType": t.template_type, "content": t.content,
        "description": t.description, "status": t.status,
    }


def _review_dict(r: KnowledgeReview) -> dict[str, object]:
    return {
        "reviewId": r.review_id, "docId": r.doc_id,
        "reviewerId": r.reviewer_id, "reviewStatus": r.review_status,
        "comments": r.comments,
        "createdAt": r.create_time.isoformat() if r.create_time else None,
    }


def _checklist_dict(c: ComplianceChecklist) -> dict[str, object]:
    return {
        "checklistId": c.checklist_id, "projectId": c.project_id,
        "checklistName": c.checklist_name, "checklistType": c.checklist_type,
        "items": c.items, "status": c.status,
    }


def _version_dict(v: DocumentVersion) -> dict[str, object]:
    return {
        "versionId": v.version_id, "docId": v.doc_id,
        "version": v.version, "versionNum": v.version_num,
        "content": v.content, "createdBy": v.created_by,
    }


def _policy_dict(p: Policy) -> dict[str, object]:
    return {
        "policyId": p.policy_id, "title": p.title,
        "policyType": p.policy_type, "content": p.content,
        "status": p.status,
    }
