"""Integration tests for knowledge API endpoints."""

import pytest

from app.models.knowledge.models import (
    ComplianceChecklist,
    KnowledgeDoc,
    KnowledgeReview,
    KnowledgeTemplate,
    Policy,
)


# ── Knowledge Docs CRUD + Publish ────────────────────────────────────

@pytest.mark.asyncio
async def test_create_doc(client, db_session):
    resp = await client.post("/api/knowledge/docs", json={
        "title": "Test Doc",
        "doc_type": "report",
        "category": "project",
        "content": "Some content",
        "author_id": "user-1",
        "created_by": "admin",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "docId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_docs(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-list-1", title="Doc One", doc_type="guide",
        category="engineering", status="draft", version="1.0", version_num=1,
    ))
    db_session.add(KnowledgeDoc(
        doc_id="doc-list-2", title="Doc Two", doc_type="report",
        category="project", status="published", version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/docs", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_docs_filter_by_status(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-filter-1", title="Draft Doc", status="draft",
        version="1.0", version_num=1,
    ))
    db_session.add(KnowledgeDoc(
        doc_id="doc-filter-2", title="Pub Doc", status="published",
        version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/docs", params={"status": "published", "page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(r["status"] == "published" for r in data["records"])


@pytest.mark.asyncio
async def test_get_doc(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-get-1", title="Get Me", content="Full content here",
        doc_type="guide", category="engineering", status="draft",
        author_id="user-1", version="1.0",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/docs/doc-get-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"]["title"] == "Get Me"
    assert resp.json()["data"]["content"] == "Full content here"


@pytest.mark.asyncio
async def test_get_doc_not_found(client):
    resp = await client.get("/api/knowledge/docs/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_doc(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-update-1", title="Original", content="Old content",
        status="draft", version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.put("/api/knowledge/docs/doc-update-1", json={
        "title": "Updated Title",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_doc(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-delete-1", title="To Delete", status="draft",
        version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.delete("/api/knowledge/docs/doc-delete-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_publish_doc(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-publish-1", title="To Publish", status="draft",
        version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/docs/doc-publish-1/publish")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["message"] == "发布成功"


# ── Templates ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_templates(client, db_session):
    db_session.add(KnowledgeTemplate(
        template_id="tmpl-list-1", template_name="Report Template",
        template_type="report", description="A report template", status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/templates")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_create_template(client, db_session):
    resp = await client.post("/api/knowledge/templates", json={
        "template_name": "New Template",
        "template_type": "guide",
        "content": "Template content",
        "description": "Test template",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "templateId" in resp.json()["data"]


# ── Reviews CRUD + Approve/Reject + Pending List ─────────────────────

@pytest.mark.asyncio
async def test_create_review(client, db_session):
    resp = await client.post("/api/knowledge/reviews", json={
        "doc_id": "doc-review-1",
        "reviewer_id": "reviewer-1",
        "review_status": "pending",
        "comments": "Needs review",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "reviewId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_reviews(client, db_session):
    db_session.add(KnowledgeReview(
        review_id="rev-list-1", doc_id="doc-1", reviewer_id="r-1",
        review_status="pending", comments="Review me",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/reviews", params={"doc_id": "doc-1"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_list_pending_reviews(client, db_session):
    db_session.add(KnowledgeReview(
        review_id="rev-pending-1", doc_id="doc-2", reviewer_id="r-2",
        review_status="pending", comments="Pending review",
    ))
    db_session.add(KnowledgeReview(
        review_id="rev-pending-2", doc_id="doc-3", reviewer_id="r-3",
        review_status="approved", comments="Approved",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/reviews/pending")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    data = resp.json()["data"]
    assert all(r["reviewStatus"] == "pending" for r in data)


@pytest.mark.asyncio
async def test_approve_review(client, db_session):
    db_session.add(KnowledgeReview(
        review_id="rev-approve-1", doc_id="doc-4", reviewer_id="r-4",
        review_status="pending", comments="Looks good",
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/reviews/rev-approve-1/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_review(client, db_session):
    db_session.add(KnowledgeReview(
        review_id="rev-reject-1", doc_id="doc-5", reviewer_id="r-5",
        review_status="pending", comments="",
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/reviews/rev-reject-1/reject", json={
        "comments": "Not approved",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── RAG Search ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_search(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-search-1", title="Searchable Doc",
        content="This document contains the keyword testable for search purposes",
        status="published", version="1.0", version_num=1,
    ))
    db_session.add(KnowledgeDoc(
        doc_id="doc-search-2", title="Draft Doc",
        content="This is a draft doc that should not appear",
        status="draft", version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/search", json={
        "query": "testable",
        "top_k": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    data = resp.json()["data"]
    assert data["query"] == "testable"
    # Only published docs with matching content should appear
    assert len(data["results"]) >= 1
    assert all(d["score"] == 0.9 for d in data["results"])


@pytest.mark.asyncio
async def test_rag_search_no_results(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-search-3", title="Irrelevant Doc",
        content="Nothing matches this query",
        status="published", version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/search", json={
        "query": "xyznonexistent",
        "top_k": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"]["total"] == 0


# ── Document Versions ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_doc_version(client, db_session):
    db_session.add(KnowledgeDoc(
        doc_id="doc-ver-1", title="Versioned Doc", content="Original content",
        status="draft", version="1.0", version_num=1,
    ))
    await db_session.flush()

    resp = await client.post("/api/knowledge/docs/doc-ver-1/version", json={
        "content": "Updated content for v2",
        "created_by": "admin",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "versionId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_doc_versions(client, db_session):
    from app.models.knowledge.models import DocumentVersion

    db_session.add(KnowledgeDoc(
        doc_id="doc-ver-list-1", title="Version List Doc",
        status="draft", version="1.0", version_num=1,
    ))
    db_session.add(DocumentVersion(
        version_id="ver-1", doc_id="doc-ver-list-1",
        version="1.0", version_num=1, content="First version",
        created_by="admin",
    ))
    db_session.add(DocumentVersion(
        version_id="ver-2", doc_id="doc-ver-list-1",
        version="1.0", version_num=2, content="Second version",
        created_by="admin",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/docs/doc-ver-list-1/versions")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_create_version_for_nonexistent_doc(client):
    resp = await client.post("/api/knowledge/docs/nonexistent/version", json={
        "content": "Should fail",
        "created_by": "admin",
    })
    assert resp.status_code == 404


# ── Policy CRUD ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_policy(client, db_session):
    resp = await client.post("/api/knowledge/policies", json={
        "title": "Test Policy",
        "policy_type": "security",
        "content": "Policy content here",
        "status": "draft",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "policyId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_policies(client, db_session):
    db_session.add(Policy(
        policy_id="pol-list-1", title="Existing Policy",
        policy_type="compliance", content="Policy text", status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/policies", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_policy(client, db_session):
    db_session.add(Policy(
        policy_id="pol-update-1", title="Old Title",
        policy_type="security", content="Old content", status="draft",
    ))
    await db_session.flush()

    resp = await client.put("/api/knowledge/policies/pol-update-1", json={
        "title": "New Title",
        "status": "active",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_policy(client, db_session):
    db_session.add(Policy(
        policy_id="pol-delete-1", title="To Delete",
        policy_type="general", content="Will be deleted", status="draft",
    ))
    await db_session.flush()

    resp = await client.delete("/api/knowledge/policies/pol-delete-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── Compliance Checklist ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_compliance_checklist(client, db_session):
    resp = await client.post("/api/knowledge/compliance", json={
        "project_id": "proj-checklist-1",
        "checklist_name": "Security Checklist",
        "checklist_type": "security",
        "items": "item1,item2,item3",
        "status": "pending",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "checklistId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_compliance_checklists(client, db_session):
    db_session.add(ComplianceChecklist(
        checklist_id="chk-list-1", project_id="proj-1",
        checklist_name="Safety Checklist", checklist_type="safety",
        items="item1,item2", status="completed",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/compliance", params={"project_id": "proj-1"})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_list_compliance_no_filter(client, db_session):
    db_session.add(ComplianceChecklist(
        checklist_id="chk-list-2", project_id="proj-2",
        checklist_name="General Checklist", checklist_type="general",
        items="item1", status="pending",
    ))
    await db_session.flush()

    resp = await client.get("/api/knowledge/compliance")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
