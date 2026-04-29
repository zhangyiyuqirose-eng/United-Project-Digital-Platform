"""Knowledge API router — consolidates knowledge, compliance, and review controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.knowledge.models import (
    ComplianceChecklist, KnowledgeDoc, KnowledgeReview, KnowledgeTemplate,
)

router = APIRouter(tags=["knowledge"])


# ── Knowledge Docs ───────────────────────────────────────────────────

@router.get("/docs")
async def list_docs(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    doc_type: str | None = None, category: str | None = None,
    status: str | None = None, db: AsyncSession = Depends(get_db),
):
    stmt = select(KnowledgeDoc).order_by(KnowledgeDoc.create_time.desc())
    if doc_type:
        stmt = stmt.where(KnowledgeDoc.doc_type == doc_type)
    if category:
        stmt = stmt.where(KnowledgeDoc.category == category)
    if status:
        stmt = stmt.where(KnowledgeDoc.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"docId": d.doc_id, "title": d.title, "docType": d.doc_type,
                 "templateType": d.template_type, "category": d.category,
                 "authorId": d.author_id, "createdBy": d.created_by,
                 "version": d.version, "versionNum": d.version_num,
                 "filePath": d.file_path, "status": d.status,
                 "publishTime": str(d.publish_time) if d.publish_time else None} for d in items],
    ))


@router.get("/docs/{doc_id}")
async def get_doc(doc_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.doc_id == doc_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise ResourceNotFoundError("文档", doc_id)
    return ApiResponse(code="SUCCESS", message="success", data={
        "docId": doc.doc_id, "title": doc.title, "content": doc.content,
        "docType": doc.doc_type, "category": doc.category, "status": doc.status,
        "authorId": doc.author_id, "version": doc.version, "filePath": doc.file_path,
    })


@router.post("/docs")
async def create_doc(req: DocCreateRequest, db: AsyncSession = Depends(get_db)):
    doc = KnowledgeDoc(
        doc_id=str(uuid.uuid4()), title=req.title, doc_type=req.doc_type,
        template_type=req.template_type, category=req.category,
        content=req.content, author_id=req.author_id, created_by=req.created_by,
        version=req.version or "1.0", version_num=req.version_num or 1,
        file_path=req.file_path, status=req.status or "draft",
    )
    db.add(doc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"docId": doc.doc_id})


@router.put("/docs/{doc_id}")
async def update_doc(doc_id: str, req: DocUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.doc_id == doc_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise ResourceNotFoundError("文档", doc_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/docs/{doc_id}")
async def delete_doc(doc_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.doc_id == doc_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise ResourceNotFoundError("文档", doc_id)
    await db.delete(doc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/docs/{doc_id}/publish")
async def publish_doc(doc_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.doc_id == doc_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise ResourceNotFoundError("文档", doc_id)
    doc.status = "published"
    doc.publish_time = datetime.now(timezone.utc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="发布成功")


# ── Templates ────────────────────────────────────────────────────────

@router.get("/templates")
async def list_templates(db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeTemplate)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"templateId": t.template_id, "templateName": t.template_name,
         "templateType": t.template_type, "description": t.description,
         "status": t.status, "content": t.content} for t in items
    ])


@router.post("/templates")
async def create_template(req: TemplateCreateRequest, db: AsyncSession = Depends(get_db)):
    t = KnowledgeTemplate(
        template_id=str(uuid.uuid4()), template_name=req.template_name,
        template_type=req.template_type, content=req.content,
        description=req.description, status=req.status or "active",
    )
    db.add(t)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"templateId": t.template_id})


# ── Reviews ──────────────────────────────────────────────────────────

@router.get("/reviews")
async def list_reviews(doc_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeReview)
    if doc_id:
        stmt = stmt.where(KnowledgeReview.doc_id == doc_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"reviewId": r.review_id, "docId": r.doc_id, "reviewerId": r.reviewer_id,
         "reviewStatus": r.review_status, "comments": r.comments} for r in items
    ])


@router.post("/reviews")
async def create_review(req: ReviewCreateRequest, db: AsyncSession = Depends(get_db)):
    r = KnowledgeReview(
        review_id=str(uuid.uuid4()), doc_id=req.doc_id,
        reviewer_id=req.reviewer_id, review_status=req.review_status,
        comments=req.comments,
    )
    db.add(r)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"reviewId": r.review_id})


# ── Compliance Checklists ────────────────────────────────────────────

@router.get("/compliance")
async def list_compliance(project_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ComplianceChecklist)
    if project_id:
        stmt = stmt.where(ComplianceChecklist.project_id == project_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"checklistId": c.checklist_id, "projectId": c.project_id,
         "checklistName": c.checklist_name, "checklistType": c.checklist_type,
         "items": c.items, "status": c.status} for c in items
    ])


@router.post("/compliance")
async def create_compliance(req: ComplianceCreateRequest, db: AsyncSession = Depends(get_db)):
    c = ComplianceChecklist(
        checklist_id=str(uuid.uuid4()), project_id=req.project_id,
        checklist_name=req.checklist_name, checklist_type=req.checklist_type,
        items=req.items, status=req.status or "pending",
    )
    db.add(c)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"checklistId": c.checklist_id})


# ── RAG Search ───────────────────────────────────────────────────────

@router.post("/search")
async def rag_search(req: RagSearchRequest, db: AsyncSession = Depends(get_db)):
    """RAG-style semantic search over knowledge docs."""
    stmt = select(KnowledgeDoc).where(
        KnowledgeDoc.status == "published",
    )
    if req.category:
        stmt = stmt.where(KnowledgeDoc.category == req.category)
    result = await db.execute(stmt.limit(req.top_k or 10))
    docs = result.scalars().all()
    results = []
    for d in docs:
        if req.query and d.content and req.query.lower() in d.content.lower():
            results.append({
                "docId": d.doc_id, "title": d.title,
                "snippet": d.content[:200] if d.content else "",
                "score": 0.9,
            })
    return ApiResponse(code="SUCCESS", message="success", data={
        "query": req.query, "results": results, "total": len(results),
    })


# ── Document Versions ────────────────────────────────────────────────

@router.get("/docs/{doc_id}/versions")
async def list_doc_versions(doc_id: str, db: AsyncSession = Depends(get_db)):
    """List all versions of a document."""
    from app.models.knowledge.models import DocumentVersion
    stmt = select(DocumentVersion).where(
        DocumentVersion.doc_id == doc_id
    ).order_by(DocumentVersion.version_num.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"versionId": v.version_id, "versionNum": v.version_num,
         "version": v.version, "content": v.content[:200] if v.content else "",
         "createdBy": v.created_by,
         "createdAt": str(v.create_time) if v.create_time else None}
        for v in items
    ])


@router.post("/docs/{doc_id}/version")
async def create_doc_version(
    doc_id: str, req: DocVersionRequest, db: AsyncSession = Depends(get_db),
):
    """Create a new version of a document."""
    from app.models.knowledge.models import DocumentVersion
    doc = await db.get(KnowledgeDoc, doc_id)
    if not doc:
        raise ResourceNotFoundError("文档", doc_id)
    max_version = (await db.execute(
        select(func.max(DocumentVersion.version_num)).where(
            DocumentVersion.doc_id == doc_id
        )
    )).scalar() or 0
    version = DocumentVersion(
        version_id=str(uuid.uuid4()), doc_id=doc_id,
        version=doc.version, version_num=max_version + 1,
        content=req.content, created_by=req.created_by,
    )
    db.add(version)
    doc.content = req.content
    doc.version_num = max_version + 1
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"versionId": version.version_id})


# ── Review Workflow ──────────────────────────────────────────────────

@router.get("/reviews/pending")
async def list_pending_reviews(db: AsyncSession = Depends(get_db)):
    """List all pending reviews."""
    stmt = select(KnowledgeReview).where(KnowledgeReview.review_status == "pending")
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"reviewId": r.review_id, "docId": r.doc_id, "reviewerId": r.reviewer_id,
         "reviewStatus": r.review_status, "comments": r.comments} for r in items
    ])


@router.post("/reviews/{review_id}/approve")
async def approve_review(review_id: str, db: AsyncSession = Depends(get_db)):
    """Approve a review."""
    r = await db.get(KnowledgeReview, review_id)
    if not r:
        raise ResourceNotFoundError("审核", review_id)
    r.review_status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str, req: ReviewRejectRequest, db: AsyncSession = Depends(get_db),
):
    """Reject a review."""
    r = await db.get(KnowledgeReview, review_id)
    if not r:
        raise ResourceNotFoundError("审核", review_id)
    r.review_status = "rejected"
    r.comments = req.comments or r.comments
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Policy Management ────────────────────────────────────────────────

@router.get("/policies")
async def list_policies(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List policies."""
    from app.models.knowledge.models import Policy
    stmt = select(Policy).order_by(Policy.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "policyId": p.policy_id, "title": p.title,
            "policyType": p.policy_type, "content": p.content[:200] if p.content else "",
            "status": p.status,
        } for p in items],
    ))


@router.post("/policies")
async def create_policy(req: PolicyCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a policy."""
    from app.models.knowledge.models import Policy
    p = Policy(
        policy_id=str(uuid.uuid4()), title=req.title,
        policy_type=req.policy_type, content=req.content,
        status=req.status or "draft",
    )
    db.add(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"policyId": p.policy_id})


@router.put("/policies/{policy_id}")
async def update_policy(
    policy_id: str, req: PolicyUpdateRequest, db: AsyncSession = Depends(get_db),
):
    """Update a policy."""
    from app.models.knowledge.models import Policy
    p = await db.get(Policy, policy_id)
    if not p:
        raise ResourceNotFoundError("政策", policy_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a policy."""
    from app.models.knowledge.models import Policy
    p = await db.get(Policy, policy_id)
    if not p:
        raise ResourceNotFoundError("政策", policy_id)
    await db.delete(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/docs/list")
async def list_docs_alias(
    doc_type: str | None = None, category: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_docs(doc_type=doc_type, category=category, status=status, page=page, size=size, db=db)


@router.get("/template/list")
async def list_templates_singular(db: AsyncSession = Depends(get_db)):
    return await list_templates(db=db)


@router.get("/templates/list")
async def list_templates_alias(db: AsyncSession = Depends(get_db)):
    return await list_templates(db=db)


@router.get("/document/list")
async def list_docs_alias2(
    doc_type: str | None = None, category: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_docs(doc_type=doc_type, category=category, status=status, page=page, size=size, db=db)


@router.post("/document/upload")
async def upload_document(title: str = Form(...), project_id: str = Form(None),
                           file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload a knowledge document."""
    import uuid
    from datetime import datetime, timezone
    doc = KnowledgeDoc(
        doc_id=str(uuid.uuid4()), title=title, project_id=project_id,
        file_name=file.filename, file_size=file.size,
        uploaded_by="system", status="draft",
        upload_time=datetime.now(timezone.utc),
    )
    db.add(doc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"docId": doc.doc_id})


@router.get("/document/{doc_id}/download")
async def download_doc(doc_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    doc = await db.get(KnowledgeDoc, doc_id)
    if not doc:
        raise ResourceNotFoundError("Document", doc_id)
    return ApiResponse(code="SUCCESS", message="success", data={"docId": doc_id, "fileName": doc.file_name})


@router.get("/template/{template_id}/download")
async def download_template(template_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    t = await db.get(KnowledgeTemplate, template_id)
    if not t:
        raise ResourceNotFoundError("Template", template_id)
    return ApiResponse(code="SUCCESS", message="success", data={"templateId": template_id, "name": t.template_name})


# ── Request schemas ──────────────────────────────────────────────────

class DocCreateRequest(BaseModel):
    title: str
    doc_type: str | None = None
    template_type: str | None = None
    category: str | None = None
    content: str | None = None
    author_id: str | None = None
    created_by: str | None = None
    version: str | None = None
    version_num: int | None = None
    file_path: str | None = None
    status: str | None = None

class DocUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    doc_type: str | None = None
    category: str | None = None
    status: str | None = None
    version: str | None = None

class TemplateCreateRequest(BaseModel):
    template_name: str
    template_type: str | None = None
    content: str | None = None
    description: str | None = None
    status: str | None = None

class ReviewCreateRequest(BaseModel):
    doc_id: str
    reviewer_id: str | None = None
    review_status: str | None = None
    comments: str | None = None

class ComplianceCreateRequest(BaseModel):
    project_id: str
    checklist_name: str
    checklist_type: str | None = None
    items: str | None = None
    status: str | None = None


class RagSearchRequest(BaseModel):
    query: str
    category: str | None = None
    top_k: int | None = 10


class DocVersionRequest(BaseModel):
    content: str
    created_by: str | None = None


class ReviewRejectRequest(BaseModel):
    comments: str | None = None


class PolicyCreateRequest(BaseModel):
    title: str
    policy_type: str | None = None
    content: str | None = None
    status: str | None = None


class PolicyUpdateRequest(BaseModel):
    title: str | None = None
    policy_type: str | None = None
    content: str | None = None
    status: str | None = None
