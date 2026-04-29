"""Tests for app/services/project_service.py — all 67+ methods."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest

from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError
from app.models.project.models import (
    BuildRecord, CodeRepo, PreInitiation, ProgressAlert, Project,
    ProjectChange, ProjectClose, ProjectDependency, ProjectMilestone,
    ProjectRisk, ProjectTask, Sprint, WbsNode,
)
from app.services.project_service import ProjectService
from app.services.project_service import (
    _project_to_dict, _task_to_dict, _task_full_dict,
    _risk_dict, _task_duration,
)


# ── Helper: create a minimal project ─────────────────────────────────

async def _make_project(db, pid="proj-test-1", **overrides):
    defaults = dict(
        project_id=pid,
        project_name="Test Project",
        status="active",
        manager_name="Test Manager",
        progress=50,
        budget=100000.0,
    )
    defaults.update(overrides)
    if "project_code" not in defaults:
        defaults["project_code"] = defaults["project_id"].upper().replace("-", "-CODE-")
    p = Project(**defaults)
    db.add(p)
    await db.flush()
    return p


# ── Project CRUD ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project({
        "project_name": "New Project",
        "project_code": "NP-001",
        "status": "draft",
        "budget": 50000.0,
    })
    assert "projectId" in result

    # Verify in DB
    p = await db_session.get(Project, result["projectId"])
    assert p is not None
    assert p.project_name == "New Project"


@pytest.mark.asyncio
async def test_get_project(client, db_session):
    await _make_project(db_session)
    svc = ProjectService(db_session)
    p = await svc.get_project("proj-test-1")
    assert p.project_id == "proj-test-1"
    assert p.project_name == "Test Project"


@pytest.mark.asyncio
async def test_get_project_not_found(client, db_session):
    svc = ProjectService(db_session)
    with pytest.raises(ResourceNotFoundError):
        await svc.get_project("nonexistent")


@pytest.mark.asyncio
async def test_update_project(client, db_session):
    await _make_project(db_session)
    svc = ProjectService(db_session)
    await svc.update_project("proj-test-1", {"project_name": "Updated", "progress": 75})
    p = await db_session.get(Project, "proj-test-1")
    assert p.project_name == "Updated"
    assert p.progress == 75


@pytest.mark.asyncio
async def test_update_project_not_found(client, db_session):
    svc = ProjectService(db_session)
    with pytest.raises(ResourceNotFoundError):
        await svc.update_project("nonexistent", {"project_name": "x"})


@pytest.mark.asyncio
async def test_delete_project(client, db_session):
    await _make_project(db_session)
    svc = ProjectService(db_session)
    await svc.delete_project("proj-test-1")
    p = await db_session.get(Project, "proj-test-1")
    assert p is None


@pytest.mark.asyncio
async def test_list_projects_empty(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.list_projects()
    assert result.total == 0
    assert result.records == []


@pytest.mark.asyncio
async def test_list_projects_with_filter(client, db_session):
    await _make_project(db_session, pid="proj-f1", status="active")
    await _make_project(db_session, pid="proj-f2", status="closed")
    svc = ProjectService(db_session)
    result = await svc.list_projects(status="active")
    assert result.total >= 1
    assert all(r["status"] == "active" for r in result.records)


@pytest.mark.asyncio
async def test_list_projects_pagination(client, db_session):
    for i in range(5):
        await _make_project(db_session, pid=f"proj-pg-{i}", project_code=f"PG-{i:03d}")
    svc = ProjectService(db_session)
    result = await svc.list_projects(page=1, size=2)
    assert len(result.records) <= 2
    assert result.total >= 5


# ── Health Score ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_health_score(client, db_session):
    await _make_project(db_session, progress=60)
    svc = ProjectService(db_session)
    result = await svc.get_health_score("proj-test-1")
    assert "healthScore" in result
    assert "breakdown" in result
    assert "progress" in result["breakdown"]
    assert "cost" in result["breakdown"]
    assert "risk" in result["breakdown"]
    assert "task" in result["breakdown"]


@pytest.mark.asyncio
async def test_get_health_score_with_risks(client, db_session):
    await _make_project(db_session, project_id="proj-health-risks")
    db_session.add_all([
        ProjectRisk(risk_id="risk-h1", project_id="proj-health-risks",
                     risk_name="Risk 1", status="open", probability=3, impact=3),
        ProjectRisk(risk_id="risk-h2", project_id="proj-health-risks",
                     risk_name="Risk 2", status="open", probability=2, impact=4),
    ])
    await db_session.flush()
    svc = ProjectService(db_session)
    result = await svc.get_health_score("proj-health-risks")
    assert result["breakdown"]["risk"] < 20  # open_risks > 0


# ── Critical Path ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_critical_path_empty(client, db_session):
    await _make_project(db_session, project_id="proj-cp-empty")
    svc = ProjectService(db_session)
    result = await svc.get_critical_path("proj-cp-empty")
    assert result["criticalPath"] == []
    assert result["totalDuration"] == 0


@pytest.mark.asyncio
async def test_get_critical_path_with_tasks(client, db_session):
    await _make_project(db_session, project_id="proj-cp")
    db_session.add_all([
        ProjectTask(task_id="task-cp-1", project_id="proj-cp",
                    task_name="Task 1", start_date=date(2026, 1, 1), end_date=date(2026, 1, 10)),
        ProjectTask(task_id="task-cp-2", project_id="proj-cp",
                    task_name="Task 2", parent_task_id="task-cp-1",
                    start_date=date(2026, 1, 11), end_date=date(2026, 1, 20)),
    ])
    await db_session.flush()
    svc = ProjectService(db_session)
    result = await svc.get_critical_path("proj-cp")
    assert len(result["criticalPath"]) > 0


# ── Task CRUD ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_task(client, db_session):
    await _make_project(db_session, project_id="proj-task")
    svc = ProjectService(db_session)
    result = await svc.create_task("proj-task", {"task_name": "New Task"})
    assert "taskId" in result


@pytest.mark.asyncio
async def test_list_tasks(client, db_session):
    await _make_project(db_session, project_id="proj-ltasks")
    svc = ProjectService(db_session)
    await svc.create_task("proj-ltasks", {"task_name": "Task A"})
    result = await svc.list_tasks("proj-ltasks")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_update_task(client, db_session):
    await _make_project(db_session, project_id="proj-utask")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-utask", {"task_name": "Update Me"})
    tid = task_result["taskId"]
    await svc.update_task(tid, {"task_name": "Updated Task"})
    d = await svc.get_task(tid)
    assert d["taskName"] == "Updated Task"


@pytest.mark.asyncio
async def test_update_task_progress(client, db_session):
    await _make_project(db_session, project_id="proj-tp")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-tp", {"task_name": "Progress Task"})
    tid = task_result["taskId"]
    result = await svc.update_task_progress(tid, 75)
    assert result["progress"] == 75


@pytest.mark.asyncio
async def test_block_task(client, db_session):
    await _make_project(db_session, project_id="proj-block")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-block", {"task_name": "Block Me"})
    tid = task_result["taskId"]
    result = await svc.block_task(tid, "Blocked by dependency")
    assert result["reason"] == "Blocked by dependency"


@pytest.mark.asyncio
async def test_complete_task(client, db_session):
    await _make_project(db_session, project_id="proj-complete")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-complete", {"task_name": "Complete Me"})
    tid = task_result["taskId"]
    result = await svc.complete_task(tid)
    assert result["taskId"] == tid


@pytest.mark.asyncio
async def test_delete_task(client, db_session):
    await _make_project(db_session, project_id="proj-dtask")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-dtask", {"task_name": "Delete Me"})
    tid = task_result["taskId"]
    await svc.delete_task(tid)
    stmt = __import__("sqlalchemy", fromlist=["select"]).select(ProjectTask).where(
        ProjectTask.task_id == tid
    )
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_get_task(client, db_session):
    await _make_project(db_session, project_id="proj-gtask")
    svc = ProjectService(db_session)
    task_result = await svc.create_task("proj-gtask", {"task_name": "Get Me"})
    tid = task_result["taskId"]
    d = await svc.get_task(tid)
    assert d["taskName"] == "Get Me"


@pytest.mark.asyncio
async def test_list_overdue_tasks(client, db_session):
    await _make_project(db_session, project_id="proj-overdue")
    db_session.add(ProjectTask(
        task_id="task-od-1", project_id="proj-overdue",
        task_name="Overdue Task", status="in_progress",
        end_date=date(2020, 1, 1),  # far in the past
    ))
    await db_session.flush()
    svc = ProjectService(db_session)
    result = await svc.list_overdue_tasks("proj-overdue")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_get_task_tree(client, db_session):
    await _make_project(db_session, project_id="proj-tree")
    svc = ProjectService(db_session)
    await svc.create_task("proj-tree", {"task_name": "Root Task"})
    result = await svc.get_task_tree("proj-tree")
    assert "roots" in result
    assert "children" in result


# ── Risk CRUD ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_risk(client, db_session):
    await _make_project(db_session, project_id="proj-risk")
    svc = ProjectService(db_session)
    result = await svc.create_risk("proj-risk", {"risk_name": "New Risk", "probability": 3, "impact": 3})
    assert "riskId" in result


@pytest.mark.asyncio
async def test_list_risks(client, db_session):
    await _make_project(db_session, project_id="proj-lrisks")
    svc = ProjectService(db_session)
    await svc.create_risk("proj-lrisks", {"risk_name": "Risk A", "probability": 2, "impact": 2})
    result = await svc.list_risks("proj-lrisks")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_update_risk(client, db_session):
    await _make_project(db_session, project_id="proj-urisk")
    svc = ProjectService(db_session)
    risk_result = await svc.create_risk("proj-urisk", {"risk_name": "Update Risk", "probability": 3, "impact": 3})
    rid = risk_result["riskId"]
    await svc.update_risk(rid, {"risk_name": "Updated Risk"})
    stmt = __import__("sqlalchemy", fromlist=["select"]).select(ProjectRisk).where(
        ProjectRisk.risk_id == rid
    )
    r = (await db_session.execute(stmt)).scalar_one()
    assert r.risk_name == "Updated Risk"


@pytest.mark.asyncio
async def test_delete_risk(client, db_session):
    await _make_project(db_session, project_id="proj-drisk")
    svc = ProjectService(db_session)
    risk_result = await svc.create_risk("proj-drisk", {"risk_name": "Delete Risk", "probability": 1, "impact": 1})
    rid = risk_result["riskId"]
    await svc.delete_risk(rid)
    stmt = __import__("sqlalchemy", fromlist=["select"]).select(ProjectRisk).where(
        ProjectRisk.risk_id == rid
    )
    assert (await db_session.execute(stmt)).scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_list_risks_paginated(client, db_session):
    await _make_project(db_session, project_id="proj-rp")
    svc = ProjectService(db_session)
    await svc.create_risk("proj-rp", {"risk_name": "Paginated Risk", "probability": 2, "impact": 2})
    result = await svc.list_risks_paginated("proj-rp", page=1, size=10)
    assert isinstance(result, PageResult)


@pytest.mark.asyncio
async def test_risk_stats(client, db_session):
    await _make_project(db_session, project_id="proj-rstats")
    svc = ProjectService(db_session)
    await svc.create_risk("proj-rstats", {"risk_name": "Stat Risk", "probability": 3, "impact": 3, "severity": "high"})
    result = await svc.risk_stats("proj-rstats")
    assert "bySeverity" in result
    assert "open" in result


@pytest.mark.asyncio
async def test_assess_risk(client, db_session):
    await _make_project(db_session, project_id="proj-assess")
    svc = ProjectService(db_session)
    risk_result = await svc.create_risk("proj-assess", {"risk_name": "Assess Risk", "probability": 4, "impact": 5})
    rid = risk_result["riskId"]
    result = await svc.assess_risk(rid)
    assert result["riskId"] == rid
    assert "score" in result


@pytest.mark.asyncio
async def test_update_risk_status(client, db_session):
    await _make_project(db_session, project_id="proj-rstat")
    svc = ProjectService(db_session)
    risk_result = await svc.create_risk("proj-rstat", {"risk_name": "Status Risk", "probability": 2, "impact": 2})
    rid = risk_result["riskId"]
    result = await svc.update_risk_status(rid, "closed")
    assert result["status"] == "closed"


# ── Sprint CRUD ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-sprint")
    svc = ProjectService(db_session)
    result = await svc.create_sprint("proj-sprint", {"sprint_name": "Sprint 1"})
    assert "sprintId" in result


@pytest.mark.asyncio
async def test_list_sprints(client, db_session):
    await _make_project(db_session, project_id="proj-lsprints")
    svc = ProjectService(db_session)
    await svc.create_sprint("proj-lsprints", {"sprint_name": "List Sprint"})
    result = await svc.list_sprints("proj-lsprints")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_get_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-gsprint")
    svc = ProjectService(db_session)
    sprint_result = await svc.create_sprint("proj-gsprint", {"sprint_name": "Get Sprint"})
    sid = sprint_result["sprintId"]
    d = await svc.get_sprint(sid)
    assert d["sprintName"] == "Get Sprint"


@pytest.mark.asyncio
async def test_update_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-usprint")
    svc = ProjectService(db_session)
    sprint_result = await svc.create_sprint("proj-usprint", {"sprint_name": "Update Sprint"})
    sid = sprint_result["sprintId"]
    result = await svc.update_sprint(sid, {"sprint_name": "Updated Sprint"})
    assert result["sprintId"] == sid


@pytest.mark.asyncio
async def test_list_sprints_paginated(client, db_session):
    await _make_project(db_session, project_id="proj-sp")
    svc = ProjectService(db_session)
    await svc.create_sprint("proj-sp", {"sprint_name": "Paginated Sprint"})
    result = await svc.list_sprints_paginated("proj-sp", page=1, size=10)
    assert isinstance(result, PageResult)


@pytest.mark.asyncio
async def test_complete_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-csprint")
    svc = ProjectService(db_session)
    sprint_result = await svc.create_sprint("proj-csprint", {"sprint_name": "Complete Sprint"})
    sid = sprint_result["sprintId"]
    result = await svc.complete_sprint(sid, velocity=30)
    assert result["velocity"] == 30


@pytest.mark.asyncio
async def test_cancel_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-xsprint")
    svc = ProjectService(db_session)
    sprint_result = await svc.create_sprint("proj-xsprint", {"sprint_name": "Cancel Sprint"})
    sid = sprint_result["sprintId"]
    result = await svc.cancel_sprint(sid)
    assert result["sprintId"] == sid


@pytest.mark.asyncio
async def test_get_active_sprint(client, db_session):
    await _make_project(db_session, project_id="proj-asprint")
    svc = ProjectService(db_session)
    result = await svc.get_active_sprint("proj-asprint")
    assert result is None  # no active sprint


@pytest.mark.asyncio
async def test_get_active_sprint_found(client, db_session):
    await _make_project(db_session, project_id="proj-asprint2")
    svc = ProjectService(db_session)
    await svc.create_sprint("proj-asprint2", {"sprint_name": "Active Sprint", "status": "active"})
    result = await svc.get_active_sprint("proj-asprint2")
    assert result is not None


# ── Milestone CRUD ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_milestone(client, db_session):
    await _make_project(db_session, project_id="proj-ms")
    svc = ProjectService(db_session)
    result = await svc.create_milestone("proj-ms", {"milestone_name": "Design Complete"})
    assert "milestoneId" in result


@pytest.mark.asyncio
async def test_list_milestones(client, db_session):
    await _make_project(db_session, project_id="proj-lms")
    svc = ProjectService(db_session)
    await svc.create_milestone("proj-lms", {"milestone_name": "List Milestone"})
    result = await svc.list_milestones("proj-lms")
    assert len(result) >= 1


# ── WBS ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_wbs_empty(client, db_session):
    await _make_project(db_session, project_id="proj-wbs")
    svc = ProjectService(db_session)
    result = await svc.list_wbs("proj-wbs")
    assert result == []


@pytest.mark.asyncio
async def test_create_wbs_node(client, db_session):
    await _make_project(db_session, project_id="proj-wbs2")
    svc = ProjectService(db_session)
    result = await svc.create_wbs_node("proj-wbs2", {"name": "Phase 1", "code": "P1"})
    assert "wbsId" in result


@pytest.mark.asyncio
async def test_wbs_decompose(client, db_session):
    await _make_project(db_session, project_id="proj-wbs3", project_name="Decompose Project")
    svc = ProjectService(db_session)
    result = await svc.wbs_decompose("proj-wbs3")
    assert result["projectId"] == "proj-wbs3"
    assert "wbs" in result


# ── EVM ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calculate_evm(client, db_session):
    await _make_project(db_session, project_id="proj-evm", budget=100000.0, progress=50)
    svc = ProjectService(db_session)
    result = await svc.calculate_evm("proj-evm")
    assert "cpi" in result
    assert "spi" in result
    assert "pv" in result
    assert "ev" in result
    assert "ac" in result


# ── Gantt ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_gantt_data_empty(client, db_session):
    await _make_project(db_session, project_id="proj-gantt")
    svc = ProjectService(db_session)
    result = await svc.get_gantt_data("proj-gantt")
    assert result == []


@pytest.mark.asyncio
async def test_get_gantt_data_with_tasks(client, db_session):
    await _make_project(db_session, project_id="proj-gantt2")
    svc = ProjectService(db_session)
    await svc.create_task("proj-gantt2", {"task_name": "Gantt Task", "start_date": date(2026, 1, 1), "end_date": date(2026, 1, 10)})
    result = await svc.get_gantt_data("proj-gantt2")
    assert len(result) >= 1


# ── Dependencies ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_dependency(client, db_session):
    await _make_project(db_session, project_id="proj-dep")
    await _make_project(db_session, project_id="proj-other-dep2")
    svc = ProjectService(db_session)
    result = await svc.create_dependency({
        "project_id": "proj-dep",
        "depends_on_project_id": "proj-other-dep2",
        "dependency_type": "finish-to-start",
    })
    assert "depId" in result


@pytest.mark.asyncio
async def test_list_dependencies(client, db_session):
    await _make_project(db_session, project_id="proj-ldeps")
    svc = ProjectService(db_session)
    await svc.create_dependency({
        "project_id": "proj-ldeps",
        "depends_on_project_id": "proj-other",
        "dependency_type": "finish-to-start",
    })
    result = await svc.list_dependencies("proj-ldeps")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_delete_dependency(client, db_session):
    await _make_project(db_session, project_id="proj-ddep")
    await _make_project(db_session, project_id="proj-other-dep")
    svc = ProjectService(db_session)
    dep_result = await svc.create_dependency({
        "project_id": "proj-ddep",
        "depends_on_project_id": "proj-other-dep",
        "dependency_type": "finish-to-start",
    })
    dep_id = dep_result["depId"]
    await svc.delete_dependency(dep_id)
    deps = await svc.list_dependencies("proj-ddep")
    assert all(d["depId"] != dep_id for d in deps)


# ── Alerts ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_alerts_empty(client, db_session):
    await _make_project(db_session, project_id="proj-alerts")
    svc = ProjectService(db_session)
    result = await svc.list_alerts("proj-alerts")
    assert result == []


@pytest.mark.asyncio
async def test_list_all_alerts_empty(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.list_all_alerts()
    assert result == []


@pytest.mark.asyncio
async def test_resolve_alert_not_found(client, db_session):
    svc = ProjectService(db_session)
    with pytest.raises(ResourceNotFoundError):
        await svc.resolve_alert("nonexistent-alert")


@pytest.mark.asyncio
async def test_check_and_generate_alerts(client, db_session):
    await _make_project(db_session, project_id="proj-gen-alerts", status="active")
    svc = ProjectService(db_session)
    result = await svc.check_and_generate_alerts()
    assert "generated" in result


# ── Pre-Initiation ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_pre_initiation(client, db_session):
    await _make_project(db_session, project_id="proj-preinit")
    svc = ProjectService(db_session)
    result = await svc.create_pre_initiation("proj-preinit", {"feasibility_study": "Feasible"})
    assert "preId" in result


@pytest.mark.asyncio
async def test_get_pre_initiation(client, db_session):
    await _make_project(db_session, project_id="proj-gpreinit")
    svc = ProjectService(db_session)
    await svc.create_pre_initiation("proj-gpreinit", {"feasibility_study": "Feasible"})
    result = await svc.get_pre_initiation("proj-gpreinit")
    assert result is not None


@pytest.mark.asyncio
async def test_create_pre_initiation_submit(client, db_session):
    await _make_project(db_session, project_id="proj-presub")
    svc = ProjectService(db_session)
    result = await svc.create_pre_initiation_submit("proj-presub", {"feasibility_study": "Submit"})
    assert "preId" in result


@pytest.mark.asyncio
async def test_approve_pre_initiation(client, db_session):
    await _make_project(db_session, project_id="proj-preappr")
    svc = ProjectService(db_session)
    pre_result = await svc.create_pre_initiation_submit("proj-preappr", {"feasibility_study": "Approve"})
    pid = pre_result["preId"]
    result = await svc.approve_pre_initiation(pid, True, "Approved")
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_list_pre_initiation_by_dept(client, db_session):
    await _make_project(db_session, project_id="proj-lpre", department_id="dept-1")
    svc = ProjectService(db_session)
    await svc.create_pre_initiation("proj-lpre", {"feasibility_study": "Dept list"})
    result = await svc.list_pre_initiation_by_dept("dept-1", page=1, size=10)
    assert isinstance(result, PageResult)


# ── Close ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_close_project(client, db_session):
    await _make_project(db_session, project_id="proj-close")
    svc = ProjectService(db_session)
    result = await svc.close_project("proj-close", {"close_type": "normal"})
    assert "closeId" in result


@pytest.mark.asyncio
async def test_complete_close(client, db_session):
    await _make_project(db_session, project_id="proj-cclose")
    svc = ProjectService(db_session)
    close_result = await svc.close_project("proj-cclose", {"close_type": "normal"})
    cid = close_result["closeId"]
    result = await svc.complete_close(cid)
    assert result["status"] == "completed"


# ── Changes ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_change(client, db_session):
    await _make_project(db_session, project_id="proj-change")
    svc = ProjectService(db_session)
    result = await svc.create_change("proj-change", {"change_type": "scope"})
    assert "changeId" in result


@pytest.mark.asyncio
async def test_list_changes(client, db_session):
    await _make_project(db_session, project_id="proj-lchanges")
    svc = ProjectService(db_session)
    await svc.create_change("proj-lchanges", {"change_type": "scope"})
    result = await svc.list_changes("proj-lchanges")
    assert len(result) >= 1


# ── Progress ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_progress(client, db_session):
    await _make_project(db_session, project_id="proj-prog")
    svc = ProjectService(db_session)
    result = await svc.update_progress("proj-prog", '[{"name":"Phase 1"}]')
    assert result["projectId"] == "proj-prog"


@pytest.mark.asyncio
async def test_get_progress(client, db_session):
    await _make_project(db_session, project_id="proj-gprog")
    svc = ProjectService(db_session)
    result = await svc.get_progress("proj-gprog")
    assert result["projectId"] == "proj-gprog"
    assert "progress" in result


# ── Code Repos ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_repo(client, db_session):
    await _make_project(db_session, project_id="proj-repo")
    svc = ProjectService(db_session)
    result = await svc.create_repo("proj-repo", {"repo_name": "main-repo"})
    assert "repoId" in result


@pytest.mark.asyncio
async def test_list_repos(client, db_session):
    await _make_project(db_session, project_id="proj-lrepos")
    svc = ProjectService(db_session)
    await svc.create_repo("proj-lrepos", {"repo_name": "List Repo"})
    result = await svc.list_repos("proj-lrepos")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_sync_repo(client, db_session):
    await _make_project(db_session, project_id="proj-syncrepo")
    svc = ProjectService(db_session)
    repo_result = await svc.create_repo("proj-syncrepo", {"repo_name": "Sync Repo"})
    rid = repo_result["repoId"]
    result = await svc.sync_repo(rid)
    assert result["status"] == "synced"


# ── Build Records ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_build(client, db_session):
    await _make_project(db_session, project_id="proj-build")
    svc = ProjectService(db_session)
    result = await svc.create_build("proj-build", {"build_status": "success"})
    assert "buildId" in result


@pytest.mark.asyncio
async def test_list_builds(client, db_session):
    await _make_project(db_session, project_id="proj-lbuilds")
    svc = ProjectService(db_session)
    await svc.create_build("proj-lbuilds", {"build_status": "success"})
    result = await svc.list_builds("proj-lbuilds")
    assert len(result) >= 1


# ── Portfolio ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_portfolio_empty(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.portfolio()
    assert "byStatus" in result


@pytest.mark.asyncio
async def test_portfolio_summary_empty(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.portfolio_summary()
    assert "totalProjects" in result
    assert result["totalProjects"] == 0


@pytest.mark.asyncio
async def test_resource_conflicts_empty(client, db_session):
    svc = ProjectService(db_session)
    result = await svc.resource_conflicts()
    assert result == []


@pytest.mark.asyncio
async def test_resource_conflicts_no_overlap(client, db_session):
    await _make_project(db_session, project_id="proj-rc1",
                         project_name="Project A", status="active",
                         start_date=date(2026, 1, 1), end_date=date(2026, 2, 1))
    await _make_project(db_session, project_id="proj-rc2",
                         project_name="Project B", status="active",
                         start_date=date(2026, 3, 1), end_date=date(2026, 4, 1))
    svc = ProjectService(db_session)
    result = await svc.resource_conflicts()
    assert isinstance(result, list)


# ── Helper methods ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_or_404_found(client, db_session):
    await _make_project(db_session)
    svc = ProjectService(db_session)
    p = await svc._get_or_404("proj-test-1")
    assert p.project_id == "proj-test-1"


@pytest.mark.asyncio
async def test_get_or_404_not_found(client, db_session):
    svc = ProjectService(db_session)
    with pytest.raises(ResourceNotFoundError):
        await svc._get_or_404("nonexistent")


# ── Pure functions / dict converters ─────────────────────────────────

def test_project_to_dict():
    p = Project(
        project_id="p1", project_name="Test", project_code="T-001",
        status="active", manager_name="MGR", progress=50,
        budget=100000.0, evm_cpi=1.1, evm_spi=0.95,
    )
    d = _project_to_dict(p)
    assert d["projectId"] == "p1"
    assert d["projectName"] == "Test"
    assert d["status"] == "active"


def test_task_to_dict():
    t = ProjectTask(task_id="t1", task_name="Task", progress=50, status="in_progress")
    d = _task_to_dict(t)
    assert d["taskId"] == "t1"
    assert d["taskName"] == "Task"


def test_task_full_dict():
    t = ProjectTask(task_id="t2", task_name="Full Task", progress=100, status="completed",
                    start_date=date(2026, 1, 1), end_date=date(2026, 1, 10))
    d = _task_full_dict(t)
    assert d["taskId"] == "t2"
    assert d["status"] == "completed"


def test_risk_dict():
    r = ProjectRisk(risk_id="r1", risk_name="Test Risk", probability=3, impact=4, status="open")
    d = _risk_dict(r)
    assert d["riskId"] == "r1"
    assert d["riskName"] == "Test Risk"
    assert d["probability"] == 3
    assert d["impact"] == 4


def test_task_duration():
    t = ProjectTask(task_id="td", task_name="Duration Task",
                    start_date=date(2026, 1, 1), end_date=date(2026, 1, 10))
    dur = _task_duration(t)
    assert dur == 9  # inclusive

    t_no_dates = ProjectTask(task_id="td2", task_name="No Dates")
    assert _task_duration(t_no_dates) == 1
