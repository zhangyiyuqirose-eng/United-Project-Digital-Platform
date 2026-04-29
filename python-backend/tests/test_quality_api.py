"""Integration tests for /api/quality/* endpoints."""

import pytest

from app.models.quality.models import QualityDefect, QualityMetric


# ── Defects ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_defects_empty(client):
    resp = await client.get("/api/quality/defects")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_list_defects_with_data(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-1", project_id="proj-1", defect_name="Defect 1",
        severity="high", status="open",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/defects")
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_defects_filter_project(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-fp-1", project_id="proj-a", defect_name="A",
        severity="high", status="open",
    ))
    db_session.add(QualityDefect(
        defect_id="def-fp-2", project_id="proj-b", defect_name="B",
        severity="low", status="open",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/defects", params={"project_id": "proj-a"})
    records = resp.json()["data"]["records"]
    assert all(r["projectId"] == "proj-a" for r in records)


@pytest.mark.asyncio
async def test_list_defects_filter_severity(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-fs-1", project_id="proj-1", defect_name="Critical",
        severity="critical", status="open",
    ))
    db_session.add(QualityDefect(
        defect_id="def-fs-2", project_id="proj-1", defect_name="Minor",
        severity="low", status="open",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/defects", params={"severity": "critical"})
    records = resp.json()["data"]["records"]
    assert all(r["severity"] == "critical" for r in records)


@pytest.mark.asyncio
async def test_list_defects_filter_status(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-fst-1", project_id="proj-1", defect_name="Open",
        severity="high", status="open",
    ))
    db_session.add(QualityDefect(
        defect_id="def-fst-2", project_id="proj-1", defect_name="Closed",
        severity="high", status="closed",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/defects", params={"status": "closed"})
    records = resp.json()["data"]["records"]
    assert all(r["status"] == "closed" for r in records)


@pytest.mark.asyncio
async def test_list_defects_pagination(client, db_session):
    for i in range(5):
        db_session.add(QualityDefect(
            defect_id=f"def-pag-{i}", project_id="proj-1", defect_name=f"D{i}",
            severity="medium", status="open",
        ))
    await db_session.flush()

    resp = await client.get("/api/quality/defects", params={"page": 1, "size": 2})
    data = resp.json()["data"]
    assert data["total"] >= 5
    assert len(data["records"]) == 2


@pytest.mark.asyncio
async def test_create_defect(client, db_session):
    resp = await client.post("/api/quality/defects", json={
        "project_id": "proj-1",
        "defect_name": "New Defect",
        "defect_type": "functional",
        "severity": "high",
        "found_by": "tester-1",
    })
    assert resp.status_code == 200
    assert "defectId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_update_defect(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-upd-1", project_id="proj-1", defect_name="Old Name",
        severity="high", status="open",
    ))
    await db_session.flush()

    resp = await client.put("/api/quality/defects/def-upd-1", json={
        "defect_name": "Updated Name",
        "status": "in_progress",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_defect_not_found(client):
    resp = await client.put("/api/quality/defects/nonexistent", json={"defect_name": "X"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_close_defect(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-close-1", project_id="proj-1", defect_name="Close Me",
        severity="medium", status="open",
    ))
    await db_session.flush()

    resp = await client.post("/api/quality/defect/def-close-1/close")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_close_defect_not_found(client):
    resp = await client.post("/api/quality/defect/nonexistent/close")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_resolve_defect(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-res-1", project_id="proj-1", defect_name="Resolve Me",
        severity="low", status="open",
    ))
    await db_session.flush()

    resp = await client.post("/api/quality/defect/def-res-1/resolve")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_resolve_defect_not_found(client):
    resp = await client.post("/api/quality/defect/nonexistent/resolve")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_defects_alias(client, db_session):
    db_session.add(QualityDefect(
        defect_id="def-alias-1", project_id="proj-1", defect_name="Alias",
        severity="high", status="open",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/defect/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1


# ── Metrics ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_metrics_empty(client):
    resp = await client.get("/api/quality/metrics")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_metrics_with_data(client, db_session):
    db_session.add(QualityMetric(
        metric_id="met-1", project_id="proj-1", metric_name="Code Coverage",
        metric_value=85.5, target_value=90.0, unit="percent",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/metrics")
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["metricName"] == "Code Coverage"


@pytest.mark.asyncio
async def test_list_metrics_filter_project(client, db_session):
    db_session.add(QualityMetric(
        metric_id="met-fp-1", project_id="proj-a", metric_name="A",
        metric_value=80, target_value=90, unit="percent",
    ))
    db_session.add(QualityMetric(
        metric_id="met-fp-2", project_id="proj-b", metric_name="B",
        metric_value=70, target_value=80, unit="percent",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/metrics", params={"project_id": "proj-a"})
    data = resp.json()["data"]
    assert len(data) == 1


@pytest.mark.asyncio
async def test_create_metric(client, db_session):
    resp = await client.post("/api/quality/metrics", json={
        "project_id": "proj-1",
        "metric_name": "Bug Density",
        "metric_value": 2.5,
        "target_value": 1.0,
        "unit": "bugs/KLOC",
    })
    assert resp.status_code == 200
    assert "metricId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_get_metrics_by_project(client, db_session):
    db_session.add(QualityMetric(
        metric_id="met-bp-1", project_id="proj-metrics", metric_name="Coverage",
        metric_value=78.0, target_value=80.0, unit="percent",
    ))
    await db_session.flush()

    resp = await client.get("/api/quality/metrics/proj-metrics")
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["metricName"] == "Coverage"


# ── Compliance Check ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_compliance_check_pass(client, db_session):
    resp = await client.post("/api/quality/compliance/check", json={
        "project_id": "proj-clean",
        "check_scope": "full",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "checks" in data
    assert data["overall"] in ("pass", "fail")


@pytest.mark.asyncio
async def test_compliance_check_with_defects(client, db_session):
    for i in range(6):
        db_session.add(QualityDefect(
            defect_id=f"def-cc-{i}", project_id="proj-many-defects",
            defect_name=f"Open Def {i}", severity="high", status="open",
        ))
    await db_session.flush()

    resp = await client.post("/api/quality/compliance/check", json={
        "project_id": "proj-many-defects",
    })
    data = resp.json()["data"]
    # With 6 open defects, should get "warning" status (>= 5 but < 10)
    assert resp.status_code == 200
    assert any("未关闭缺陷" in c["item"] for c in data["checks"])


# ── Risk Report ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_quality_risk_report(client, db_session):
    for sev in ["critical", "high", "medium", "low"]:
        db_session.add(QualityDefect(
            defect_id=f"def-risk-{sev}", project_id="proj-risk",
            defect_name=f"{sev} defect", severity=sev, status="open",
        ))
    await db_session.flush()

    resp = await client.get("/api/quality/risk-report", params={"project_id": "proj-risk"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["totalDefects"] == 4
    assert len(data["severityBreakdown"]) == 4
    assert data["severityBreakdown"][0]["severity"] == "critical"
    assert data["severityBreakdown"][0]["count"] == 1
