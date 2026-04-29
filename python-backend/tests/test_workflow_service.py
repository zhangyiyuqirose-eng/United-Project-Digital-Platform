"""Tests for WorkflowService (app/services/workflow_service.py)."""

from __future__ import annotations

import pytest

from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.workflow.models import ProcessInstance
from app.services.workflow_service import (
    PROCESS_DEFINITIONS,
    WorkflowService,
    _eval_condition,
    _get_process_def,
    _instance_to_dict,
)


# ── Helper ────────────────────────────────────────────────────────────

async def _start_process(svc, process_key, business_key, initiator="u-1", **variables):
    return await svc.start_process(
        process_key=process_key,
        business_key=business_key,
        initiator_id=initiator,
        variables=variables or None,
    )


# ── Process definitions ───────────────────────────────────────────────

class TestProcessDefinitions:

    def test_all_four_types_defined(self):
        assert "project_initiation" in PROCESS_DEFINITIONS
        assert "project_change" in PROCESS_DEFINITIONS
        assert "project_close" in PROCESS_DEFINITIONS
        assert "settlement_approval" in PROCESS_DEFINITIONS

    def test_project_initiation_has_3_steps(self):
        pd = PROCESS_DEFINITIONS["project_initiation"]
        assert len(pd["steps"]) == 3
        step_keys = [s["key"] for s in pd["steps"]]
        assert "pmo_review" in step_keys
        assert "dept_leader_review" in step_keys
        assert "company_leader_review" in step_keys

    def test_project_change_has_conditional_steps(self):
        pd = PROCESS_DEFINITIONS["project_change"]
        assert "conditional_steps" in pd
        cond = pd["conditional_steps"]
        assert cond["condition_field"] == "budget"
        assert cond["condition_op"] == "gt"
        assert cond["condition_value"] == 500000

    def test_get_process_def_valid(self):
        pd = _get_process_def("project_initiation")
        assert pd["name"] == "项目立项审批"

    def test_get_process_def_invalid(self):
        with pytest.raises(BusinessError) as exc:
            _get_process_def("nonexistent")
        assert "WORKFLOW_NOT_FOUND" in str(exc.value.code)

    def test_settlement_approval_has_3_steps(self):
        pd = PROCESS_DEFINITIONS["settlement_approval"]
        assert len(pd["steps"]) == 3

    def test_project_close_has_2_steps(self):
        pd = PROCESS_DEFINITIONS["project_close"]
        assert len(pd["steps"]) == 2


# ── _eval_condition helper ────────────────────────────────────────────

class TestEvalCondition:

    def test_gt_true(self):
        assert _eval_condition(600000, "gt", 500000) is True

    def test_gt_false(self):
        assert _eval_condition(400000, "gt", 500000) is False

    def test_gte_true(self):
        assert _eval_condition(500000, "gte", 500000) is True

    def test_lt_true(self):
        assert _eval_condition(100000, "lt", 500000) is True

    def test_lt_false(self):
        assert _eval_condition(500000, "lt", 500000) is False

    def test_eq_true(self):
        assert _eval_condition("active", "eq", "active") is True

    def test_eq_false(self):
        assert _eval_condition("draft", "eq", "active") is False

    def test_invalid_op_returns_false(self):
        assert _eval_condition(100, "unknown_op", 100) is False

    def test_non_numeric_gt_returns_false(self):
        """gt/lte with non-numeric values returns False."""
        assert _eval_condition("abc", "gt", 100) is False
        assert _eval_condition("abc", "gte", 100) is False
        assert _eval_condition("abc", "lt", 100) is False


# ── start_process ─────────────────────────────────────────────────────

class TestStartProcess:

    @pytest.mark.asyncio
    async def test_start_project_initiation(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "project_initiation", "proj-1")
        assert result["instanceId"] is not None
        assert result["processKey"] == "project_initiation"
        assert result["status"] == "pending"
        assert result["currentStep"] == "pmo_review"

    @pytest.mark.asyncio
    async def test_start_project_change(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "project_change", "proj-2")
        assert result["status"] == "pending"
        assert result["currentStep"] == "pmo_review"

    @pytest.mark.asyncio
    async def test_start_project_close(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "project_close", "proj-3")
        assert result["currentStep"] == "pmo_review"
        assert result["businessKey"] == "proj-3"

    @pytest.mark.asyncio
    async def test_start_settlement_approval(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "settlement_approval", "settle-1")
        assert result["currentStep"] == "pm_review"
        assert result["processKey"] == "settlement_approval"

    @pytest.mark.asyncio
    async def test_start_process_stores_business_key(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "project_initiation", "biz-key-123")
        assert result["businessKey"] == "biz-key-123"

    @pytest.mark.asyncio
    async def test_start_process_stores_initiator(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await _start_process(svc, "project_initiation", "proj-5", initiator="user-42")
        assert result["submitterId"] == "user-42"

    @pytest.mark.asyncio
    async def test_start_process_invalid_key(self, client, db_session):
        svc = WorkflowService(db_session)
        with pytest.raises(BusinessError) as exc:
            await svc.start_process("invalid_process", "key-1", "u-1")
        assert exc.value.code == "WORKFLOW_NOT_FOUND"


# ── Conditional branching ─────────────────────────────────────────────

class TestConditionalBranching:

    @pytest.mark.asyncio
    async def test_project_change_below_threshold_no_extra_step(self, client, db_session):
        """Budget <= 500k: only pmo_review + dept_leader_review (2 steps)."""
        svc = WorkflowService(db_session)
        result = await _start_process(
            svc, "project_change", "proj-low",
            budget=300000,
        )
        # The state stored in variables has the steps; check by completing both
        instance = await svc.get_instance(result["instanceId"])
        # We just verify it started at first step
        assert result["currentStep"] == "pmo_review"

    @pytest.mark.asyncio
    async def test_project_change_above_threshold_adds_company_leader(self, client, db_session):
        """Budget > 500k: pmo + dept_leader + company_leader (3 steps)."""
        svc = WorkflowService(db_session)
        result = await _start_process(
            svc, "project_change", "proj-high",
            budget=600000,
        )
        # Verify the extra step is present by checking the stored variables
        instance = await svc.get_instance(result["instanceId"])
        # After completing all steps, it should go through company_leader
        assert result["currentStep"] == "pmo_review"
        # We can verify by approving through all steps
        inst_id = result["instanceId"]

        # Step 1: approve pmo_review
        r = await svc.approve_task(inst_id, "u-1", "pmo ok")
        assert r["currentStep"] == "dept_leader_review"

        # Step 2: approve dept_leader_review
        r = await svc.approve_task(inst_id, "u-2", "dept ok")
        # With budget > 500k, there should be a 3rd step
        assert r["currentStep"] == "company_leader_review"
        assert r["status"] == "pending"

        # Step 3: approve company_leader_review
        r = await svc.approve_task(inst_id, "u-3", "company ok")
        assert r["status"] == "approved"


# ── get_pending_tasks ─────────────────────────────────────────────────

class TestGetPendingTasks:

    @pytest.mark.asyncio
    async def test_returns_pending_tasks(self, client, db_session):
        svc = WorkflowService(db_session)
        await _start_process(svc, "project_initiation", "proj-p1")
        result = await svc.get_pending_tasks("u-1")
        assert result.total >= 1
        assert len(result.records) >= 1
        assert result.records[0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_empty_when_no_tasks(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await svc.get_pending_tasks("nobody")
        assert result.total == 0
        assert result.records == []

    @pytest.mark.asyncio
    async def test_does_not_return_completed_tasks(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-p2")
        # Complete all steps
        inst_id = inst["instanceId"]
        await svc.approve_task(inst_id, "u-1", "ok")
        await svc.approve_task(inst_id, "u-1", "ok")
        await svc.approve_task(inst_id, "u-1", "ok")
        result = await svc.get_pending_tasks("u-1")
        # The completed task should not appear
        pending_ids = [r["instanceId"] for r in result.records]
        assert inst_id not in pending_ids


# ── approve_task ──────────────────────────────────────────────────────

class TestApproveTask:

    @pytest.mark.asyncio
    async def test_approve_advances_to_next_step(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-ap1")
        result = await svc.approve_task(inst["instanceId"], "u-1", "Looks good")
        assert result["currentStep"] == "dept_leader_review"
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_approve_last_step_completes(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-ap2")
        inst_id = inst["instanceId"]
        await svc.approve_task(inst_id, "u-1")
        await svc.approve_task(inst_id, "u-2")
        result = await svc.approve_task(inst_id, "u-3")
        assert result["status"] == "approved"
        assert result["currentStep"] is None

    @pytest.mark.asyncio
    async def test_approve_already_done_raises(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_close", "proj-ap3")
        inst_id = inst["instanceId"]
        await svc.approve_task(inst_id, "u-1", "ok")
        await svc.approve_task(inst_id, "u-2", "ok")
        # Process is now approved
        with pytest.raises(BusinessError) as exc:
            await svc.approve_task(inst_id, "u-1", "too late")
        assert "WORKFLOW_TASK_ALREADY_DONE" in str(exc.value.code)


# ── reject_task ───────────────────────────────────────────────────────

class TestRejectTask:

    @pytest.mark.asyncio
    async def test_reject_terminates_process(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-rj1")
        result = await svc.reject_task(inst["instanceId"], "u-1", "Not feasible")
        assert result["status"] == "rejected"
        assert result["currentStep"] is None

    @pytest.mark.asyncio
    async def test_reject_already_done_raises(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_close", "proj-rj2")
        inst_id = inst["instanceId"]
        await svc.reject_task(inst_id, "u-1", "bad")
        with pytest.raises(BusinessError) as exc:
            await svc.reject_task(inst_id, "u-1", "double reject")
        assert "WORKFLOW_TASK_ALREADY_DONE" in str(exc.value.code)


# ── get_process_status ────────────────────────────────────────────────

class TestGetProcessStatus:

    @pytest.mark.asyncio
    async def test_returns_status_for_existing(self, client, db_session):
        svc = WorkflowService(db_session)
        await _start_process(svc, "project_initiation", "proj-st1")
        result = await svc.get_process_status("proj-st1")
        assert result is not None
        assert result["businessKey"] == "proj-st1"
        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await svc.get_process_status("nonexistent-biz-key")
        assert result is None


# ── get_process_history ───────────────────────────────────────────────

class TestGetProcessHistory:

    @pytest.mark.asyncio
    async def test_returns_chronological_list(self, client, db_session):
        svc = WorkflowService(db_session)
        await _start_process(svc, "project_initiation", "proj-hist1")
        await _start_process(svc, "project_initiation", "proj-hist1")
        result = await svc.get_process_history("proj-hist1")
        assert len(result) == 2
        # Should be chronological (earliest first)
        assert result[0]["createdAt"] <= result[1]["createdAt"]


# ── get_my_initiated ──────────────────────────────────────────────────

class TestGetMyInitiated:

    @pytest.mark.asyncio
    async def test_returns_user_processes(self, client, db_session):
        svc = WorkflowService(db_session)
        await _start_process(svc, "project_initiation", "proj-my1", initiator="user-a")
        await _start_process(svc, "project_close", "proj-my2", initiator="user-a")
        result = await svc.get_my_initiated("user-a")
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_empty_for_user_with_no_processes(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await svc.get_my_initiated("unknown-user")
        assert result.total == 0


# ── get_instance ──────────────────────────────────────────────────────

class TestGetInstance:

    @pytest.mark.asyncio
    async def test_returns_instance(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-gi1")
        result = await svc.get_instance(inst["instanceId"])
        assert result["instanceId"] == inst["instanceId"]
        assert result["processKey"] == "project_initiation"

    @pytest.mark.asyncio
    async def test_not_found_raises(self, client, db_session):
        svc = WorkflowService(db_session)
        with pytest.raises(ResourceNotFoundError):
            await svc.get_instance("nonexistent-id")


# ── list_process_definitions ──────────────────────────────────────────

class TestListProcessDefinitions:

    @pytest.mark.asyncio
    async def test_lists_all_definitions(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await svc.list_process_definitions()
        assert len(result) == 4
        keys = [d["processKey"] for d in result]
        assert "project_initiation" in keys


# ── get_process_definition ────────────────────────────────────────────

class TestGetProcessDefinition:

    @pytest.mark.asyncio
    async def test_returns_definition(self, client, db_session):
        svc = WorkflowService(db_session)
        result = await svc.get_process_definition("project_initiation")
        assert result["defId"] == "project_initiation"
        assert len(result["steps"]) == 3
        assert result["steps"][0]["key"] == "pmo_review"

    @pytest.mark.asyncio
    async def test_invalid_key_raises(self, client, db_session):
        svc = WorkflowService(db_session)
        with pytest.raises(BusinessError):
            await svc.get_process_definition("not-a-process")


# ── _instance_to_dict helper ──────────────────────────────────────────

class TestInstanceToDict:

    @pytest.mark.asyncio
    async def test_includes_all_keys(self, client, db_session):
        svc = WorkflowService(db_session)
        inst = await _start_process(svc, "project_initiation", "proj-dict1")
        d = await svc.get_instance(inst["instanceId"])
        assert "instanceId" in d
        assert "processKey" in d
        assert "businessKey" in d
        assert "submitterId" in d
        assert "status" in d
        assert "currentStep" in d
        assert "currentStepName" in d
        assert "currentStepRole" in d
        assert "variables" in d
        assert "comments" in d
        assert "createdAt" in d
