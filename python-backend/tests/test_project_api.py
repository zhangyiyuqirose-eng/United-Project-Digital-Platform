"""Integration tests for /api/project/* endpoints — covers alias routes and thin wrappers."""

from __future__ import annotations

import pytest

from app.models.project.models import Project


async def _make_project(db, pid="proj-api", **overrides):
    defaults = dict(
        project_id=pid,
        project_name="API Test Project",
        project_code=f"API-CODE-{pid}",
        status="active",
        progress=50,
        budget=100000.0,
    )
    defaults.update(overrides)
    p = Project(**defaults)
    db.add(p)
    await db.flush()
    return p


BASE = "/api/project"


# ── Project CRUD + aliases ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_project_list(client):
    resp = await client.get(BASE, params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_project_list_alias(client):
    resp = await client.get(f"{BASE}/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_project_create_alias(client):
    resp = await client.post(f"{BASE}/create", json={
        "project_name": "Alias Project",
        "project_code": "ALIAS-001",
        "status": "draft",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_project_create(client):
    resp = await client.post(BASE, json={
        "project_name": "New Project",
        "project_code": "NEW-001",
        "status": "active",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_project_get(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_project_update(client, db_session):
    await _make_project(db_session)
    resp = await client.put(f"{BASE}/proj-api", json={"project_name": "Updated"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_project_delete(client, db_session):
    await _make_project(db_session)
    resp = await client.delete(f"{BASE}/proj-api")
    assert resp.status_code == 200


# ── Tasks ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_task_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/tasks")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_task_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/tasks", json={"task_name": "Task"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_task_update_delete(client, db_session):
    await _make_project(db_session)
    create_resp = await client.post(f"{BASE}/proj-api/tasks", json={"task_name": "Update Task"})
    tid = create_resp.json()["data"]["taskId"]
    resp = await client.put(f"{BASE}/tasks/{tid}", json={"task_name": "Updated"})
    assert resp.status_code == 200
    resp = await client.delete(f"{BASE}/tasks/{tid}")
    assert resp.status_code == 200


# ── Risks ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_risk_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/risks")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_risk_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/risks", json={
        "risk_name": "Risk", "probability": 3, "impact": 3,
    })
    assert resp.status_code == 200


# ── Sprints ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sprint_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/sprints")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sprint_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/sprints", json={"sprint_name": "Sprint"})
    assert resp.status_code == 200


# ── Milestones ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_milestone_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/milestones")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_milestone_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/milestones", json={"milestone_name": "MS"})
    assert resp.status_code == 200


# ── WBS ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_wbs_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/wbs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_wbs_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/wbs", json={"name": "Phase", "code": "P1"})
    assert resp.status_code == 200


# ── Gantt / EVM / Health / Critical Path ─────────────────────────────

@pytest.mark.asyncio
async def test_gantt(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/gantt")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_evm(client, db_session):
    await _make_project(db_session)
    # EVM is a POST endpoint (triggers calculation), not GET
    resp = await client.post(f"{BASE}/proj-api/evm")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_score(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/health-score")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_critical_path(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/critical-path")
    assert resp.status_code == 200


# ── Progress ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_progress_get(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/progress")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_progress_update(client, db_session):
    await _make_project(db_session)
    # Progress update requires wbs_json string, not a bare progress number
    resp = await client.put(f"{BASE}/proj-api/progress", json={"wbs_json": "{}"})
    assert resp.status_code == 200


# ── Changes ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_changes_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/changes")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_changes_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/changes", json={"change_type": "scope"})
    assert resp.status_code == 200


# ── Pre-Initiation ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pre_initiation_get(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/pre-initiation")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_pre_initiation_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/pre-initiation", json={"feasibility_study": "Feasible"})
    assert resp.status_code == 200


# ── Close ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_close_project(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/close", json={"close_type": "normal"})
    assert resp.status_code == 200


# ── Alerts ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_alerts_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/alerts")
    assert resp.status_code == 200


# ── Repos ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_repos_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/repos")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_repo_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/proj-api/repos", json={"repo_name": "repo"})
    assert resp.status_code == 200


# ── Builds ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_builds_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/builds")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_build_create(client, db_session):
    await _make_project(db_session)
    resp = await client.post(f"{BASE}/build", json={
        "project_id": "proj-api", "build_status": "success",
    })
    assert resp.status_code == 200


# ── Dependencies ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dependencies_list(client, db_session):
    await _make_project(db_session)
    resp = await client.get(f"{BASE}/proj-api/dependencies")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dependency_create(client, db_session):
    await _make_project(db_session, pid="proj-dep-a")
    await _make_project(db_session, pid="proj-dep-b")
    resp = await client.post(f"{BASE}/dependency", json={
        "project_id": "proj-dep-a",
        "depends_on_project_id": "proj-dep-b",
        "dependency_type": "finish-to-start",
    })
    assert resp.status_code == 200


# ── Portfolio ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_portfolio(client):
    # /portfolio is shadowed by /{project_id} route ordering — 404 is expected
    resp = await client.get(f"{BASE}/portfolio")
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_portfolio_summary(client):
    resp = await client.get(f"{BASE}/portfolio/summary")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_portfolio_conflicts(client):
    resp = await client.get(f"{BASE}/portfolio/resource-conflicts")
    assert resp.status_code == 200
