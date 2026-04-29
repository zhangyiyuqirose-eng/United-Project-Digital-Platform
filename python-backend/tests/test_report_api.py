"""Integration tests for report service API."""

import pytest

from app.models.project.models import Project
from app.models.report.models import ReportHistory
from app.models.timesheet.models import Timesheet


# ── Report Generation ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_project_report(client, db_session):
    db_session.add(Project(
        project_id="proj-rpt-1",
        project_name="报表测试项目",
        project_code="RPT-001",
        status="active",
        manager_name="测试经理",
        progress=50,
    ))
    await db_session.flush()

    resp = await client.get("/api/report/project/proj-rpt-1/download")
    # Returns Excel file (binary)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.mark.asyncio
async def test_generate_project_report_all_projects(client, db_session):
    """Generate report for all projects (no specific project_id)."""
    db_session.add(Project(
        project_id="proj-rpt-2",
        project_name="无ID报表项目",
        project_code="RPT-002",
        status="active",
        manager_name="测试经理",
    ))
    await db_session.flush()

    # The report list endpoint works without a specific project
    resp = await client.get("/api/report/list")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_generate_cost_report(client, db_session):
    db_session.add(Project(
        project_id="proj-cost-rpt",
        project_name="成本报表项目",
        project_code="COST-RPT-001",
        status="active",
        budget=100000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/report/cost/proj-cost-rpt/download")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_generate_timesheet_report(client, db_session):
    resp = await client.get("/api/report/timesheet/download", params={"staff_id": "staff-001"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_generate_resource_report(client, db_session):
    resp = await client.get("/api/report/resource/download", params={"pool_id": "pool-001"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_generate_portfolio_report(client, db_session):
    db_session.add(Project(
        project_id="proj-port-1",
        project_name="组合项目1",
        project_code="PORT-001",
        status="active",
        budget=500000.0,
        progress=60,
    ))
    db_session.add(Project(
        project_id="proj-port-2",
        project_name="组合项目2",
        project_code="PORT-002",
        status="active",
        budget=300000.0,
        progress=40,
    ))
    await db_session.flush()

    resp = await client.get("/api/report/portfolio/download")
    assert resp.status_code == 200


# ── Report History List ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_report_history_list_empty(client):
    resp = await client.get("/api/report/list")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_report_history_list_with_data(client, db_session):
    db_session.add(ReportHistory(
        report_id="rpt-hist-1",
        report_type="project",
        target_id="proj-1",
        file_name="project_report.xlsx",
        file_size=1024,
        status="generated",
        created_by="admin",
    ))
    await db_session.flush()

    resp = await client.get("/api/report/list", params={"page": 1, "size": 10})
    data = resp.json()["data"]
    assert data["total"] >= 1
