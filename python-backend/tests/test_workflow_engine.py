"""Unit and integration tests for Python workflow engine."""

import pytest

from app.core.workflow_engine import (
    WORKFLOW_REGISTRY,
    WorkflowEngine,
)
from app.models.workflow.models import ProcessInstance


# ── Workflow Registry ───────────────────────────────────────────────

def test_workflow_registry_has_three_workflows():
    assert len(WORKFLOW_REGISTRY) == 3
    assert "projectInitApproval" in WORKFLOW_REGISTRY
    assert "projectChangeApproval" in WORKFLOW_REGISTRY
    assert "projectCloseApproval" in WORKFLOW_REGISTRY


def test_initiation_workflow_steps():
    wf = WORKFLOW_REGISTRY["projectInitApproval"]
    assert len(wf.steps) == 4
    assert wf.steps[0].name == "pmo_review"
    assert wf.steps[-1].next_step == "end"


def test_change_workflow_steps():
    wf = WORKFLOW_REGISTRY["projectChangeApproval"]
    assert len(wf.steps) == 3
    assert wf.steps[0].name == "pm_review"


def test_close_workflow_steps():
    wf = WORKFLOW_REGISTRY["projectCloseApproval"]
    assert len(wf.steps) == 5
    assert wf.steps[0].name == "pm_confirm"
    assert wf.steps[-1].name == "doc_archive"


# ── Workflow Engine Integration Tests ──────────────────────────────

@pytest.mark.asyncio
async def test_start_initiation_workflow(client, db_session):
    engine = WorkflowEngine(db_session)
    result = await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-init-001",
        submitter_id="user-001",
        variables={"budget": 3000000},
    )
    assert "instanceId" in result
    assert result["status"] == "running"
    assert result["currentStep"] == "pmo_review"


@pytest.mark.asyncio
async def test_start_unknown_workflow(client, db_session):
    engine = WorkflowEngine(db_session)
    result = await engine.start_workflow(
        process_key="nonexistent",
        business_key="proj-001",
        submitter_id="user-001",
    )
    assert "error" in result


@pytest.mark.asyncio
async def test_approve_task_advances_step(client, db_session):
    engine = WorkflowEngine(db_session)
    started = await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-approve-001",
        submitter_id="user-001",
    )
    instance_id = started["instanceId"]

    result = await engine.approve_task(instance_id, "pmo")
    assert result["status"] == "running"
    assert result["currentStep"] == "dept_leader"


@pytest.mark.asyncio
async def test_reject_task_sets_rejected(client, db_session):
    engine = WorkflowEngine(db_session)
    started = await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-reject-001",
        submitter_id="user-001",
    )
    instance_id = started["instanceId"]

    result = await engine.reject_task(instance_id, reason="预算不足")
    assert result["status"] == "rejected"


@pytest.mark.asyncio
async def test_get_workflow_status(client, db_session):
    engine = WorkflowEngine(db_session)
    started = await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-status-001",
        submitter_id="user-001",
    )
    instance_id = started["instanceId"]

    status = await engine.get_status(instance_id)
    assert status["status"] == "running"
    assert status["processKey"] == "projectInitApproval"


@pytest.mark.asyncio
async def test_get_status_not_found(client, db_session):
    engine = WorkflowEngine(db_session)
    status = await engine.get_status("nonexistent-id")
    assert "error" in status


@pytest.mark.asyncio
async def test_cancel_workflow(client, db_session):
    engine = WorkflowEngine(db_session)
    started = await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-cancel-001",
        submitter_id="user-001",
    )
    instance_id = started["instanceId"]

    result = await engine.cancel_workflow(instance_id)
    assert result["status"] == "cancelled"


@pytest.mark.asyncio
async def test_get_history_by_business_key(client, db_session):
    engine = WorkflowEngine(db_session)
    await engine.start_workflow(
        process_key="projectInitApproval",
        business_key="proj-hist-001",
        submitter_id="user-001",
    )
    await engine.start_workflow(
        process_key="projectChangeApproval",
        business_key="proj-hist-001",
        submitter_id="user-001",
    )

    history = await engine.get_history("proj-hist-001")
    assert len(history) == 2


@pytest.mark.asyncio
async def test_get_definitions(client, db_session):
    engine = WorkflowEngine(db_session)
    definitions = engine.get_workflow_definitions()
    assert len(definitions) == 3
    for d in definitions:
        assert "processKey" in d
        assert "steps" in d


# ── API Endpoint Tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_list_processes(client, db_session):
    resp = await client.get("/api/workflow/processes")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_workflow_tasks(client, db_session):
    resp = await client.get("/api/workflow/tasks")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_workflow_audit_log(client, db_session):
    resp = await client.get("/api/workflow/log/some-business-id")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_my_tasks(client, db_session):
    resp = await client.get("/api/workflow/my-tasks")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "records" in data


@pytest.mark.asyncio
async def test_api_workflow_status(client, db_session):
    resp = await client.get("/api/workflow/status/instance-001")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_workflow_history(client, db_session):
    resp = await client.get("/api/workflow/history/biz-key-001")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_start_workflow_alias(client, db_session):
    resp = await client.post("/api/workflow/start", json={
        "process_key": "projectInitApproval",
        "business_key": "proj-alias-001",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "instanceId" in data


@pytest.mark.asyncio
async def test_api_approve_task(client, db_session):
    resp = await client.post("/api/workflow/tasks/task-001/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_reject_task(client, db_session):
    resp = await client.post("/api/workflow/tasks/task-001/reject")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_my_processes(client, db_session):
    resp = await client.get("/api/workflow/my-processes")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_timeout_list(client, db_session):
    resp = await client.get("/api/workflow/timeout/list", params={"threshold_hours": 24})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_api_optimization_suggestions(client, db_session):
    resp = await client.get("/api/workflow/optimization/suggestions")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
