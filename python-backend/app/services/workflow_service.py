"""Lightweight workflow engine — manages process instances without Flowable/Camunda.

Process definitions are defined in-code.  Tasks are stored as ProcessInstance rows
with the current step tracked in ``current_step`` and step metadata in ``variables``
(JSON text column).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.workflow.models import ProcessDefinition, ProcessInstance

# ── Process definitions (hardcoded in-code) ──────────────────────────────

PROCESS_DEFINITIONS: dict[str, dict[str, Any]] = {
    "project_initiation": {
        "name": "项目立项审批",
        "steps": [
            {"key": "pmo_review", "name": "PMO审核", "role": "pmo"},
            {"key": "dept_leader_review", "name": "部门领导审核", "role": "dept_leader"},
            {"key": "company_leader_review", "name": "公司领导审核", "role": "company_leader"},
        ],
    },
    "project_change": {
        "name": "项目变更审批",
        "steps": [
            {"key": "pmo_review", "name": "PMO审核", "role": "pmo"},
            {"key": "dept_leader_review", "name": "部门领导审核", "role": "dept_leader"},
        ],
        "conditional_steps": {
            "condition_field": "budget",
            "condition_op": "gt",
            "condition_value": 500000,
            "steps": [
                {"key": "company_leader_review", "name": "公司领导审核", "role": "company_leader"},
            ],
        },
    },
    "project_close": {
        "name": "项目结项审批",
        "steps": [
            {"key": "pmo_review", "name": "PMO审核", "role": "pmo"},
            {"key": "dept_leader_review", "name": "部门领导审核", "role": "dept_leader"},
        ],
    },
    "settlement_approval": {
        "name": "结算审批",
        "steps": [
            {"key": "pm_review", "name": "项目经理审核", "role": "pm"},
            {"key": "resource_manager_review", "name": "资源经理审核", "role": "resource_manager"},
            {"key": "dept_leader_review", "name": "部门领导审核", "role": "dept_leader"},
        ],
    },
}


def _get_process_def(process_key: str) -> dict[str, Any]:
    """Return the process definition or raise an error."""
    if process_key not in PROCESS_DEFINITIONS:
        raise BusinessError(
            code="WORKFLOW_NOT_FOUND",
            message=f"Unknown process key: {process_key}",
            status_code=404,
        )
    return PROCESS_DEFINITIONS[process_key]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_variables(raw: str | None) -> dict[str, Any]:
    """Parse the variables JSON column, returning a dict."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _dump_variables(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


class WorkflowService:
    """Lightweight workflow engine backed by ProcessInstance rows."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Core workflow methods ──────────────────────────────────────────

    async def start_process(
        self,
        process_key: str,
        business_key: str,
        initiator_id: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Start a new process instance and return its state."""
        proc_def = _get_process_def(process_key)

        # Build full step list, resolving conditional steps
        steps = list(proc_def["steps"])
        if "conditional_steps" in proc_def:
            cond = proc_def["conditional_steps"]
            field_val = (variables or {}).get(cond["condition_field"])
            if field_val is not None and _eval_condition(
                field_val, cond["condition_op"], cond["condition_value"]
            ):
                steps.extend(cond["steps"])

        first_step = steps[0]
        state: dict[str, Any] = {
            "steps": steps,
            "current_step_index": 0,
            "comments": [],
            "business_data": variables or {},
        }

        instance = ProcessInstance(
            instance_id=str(uuid.uuid4()),
            process_def_id=process_key,
            process_key=process_key,
            business_key=business_key,
            submitter_id=initiator_id,
            status="pending",
            current_step=first_step["key"],
            variables=_dump_variables(state),
            create_time=_now(),
        )
        self.db.add(instance)
        await self.db.flush()

        return _instance_to_dict(instance)

    async def get_pending_tasks(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> PageResult:
        """Return paginated pending tasks where the user is responsible for the current step.

        The assignee for each step is resolved from the ``variables`` JSON.  When a
        step has no explicit assignee the instance is still returned (fallback for
        role-based assignment).
        """
        stmt = (
            select(ProcessInstance)
            .where(ProcessInstance.status == "pending")
            .order_by(ProcessInstance.create_time.desc())
        )
        result = await self.db.execute(stmt)
        all_pending = result.scalars().all()

        # Filter in Python: match user_id against step assignee stored in variables
        matched: list[dict[str, Any]] = []
        for inst in all_pending:
            state = _parse_variables(inst.variables)
            steps: list[dict[str, Any]] = state.get("steps", [])
            idx: int = state.get("current_step_index", 0)
            if idx < len(steps):
                step = steps[idx]
                assignee = step.get("assignee_id") or state.get("assignees", {}).get(
                    step["key"]
                )
                # Match: explicit assignee, or fallback to role-based (accept all for now)
                if assignee is None or assignee == user_id:
                    matched.append(_instance_to_dict(inst))

        total = len(matched)
        start = (page - 1) * limit
        page_records = matched[start : start + limit]

        return PageResult(total=total, page=page, size=limit, records=page_records)

    async def approve_task(
        self, task_id: str, user_id: str, comment: str | None = None
    ) -> dict[str, Any]:
        """Approve the current step and advance to the next step, or complete."""
        instance = await self._get_instance_or_404(task_id)
        if instance.status != "pending":
            raise BusinessError(
                code="WORKFLOW_TASK_ALREADY_DONE",
                message="Task has already been processed",
            )

        state = _parse_variables(instance.variables)
        steps: list[dict[str, Any]] = state.get("steps", [])
        idx: int = state.get("current_step_index", 0)

        if idx >= len(steps):
            raise BusinessError(code="WORKFLOW_ERROR", message="No current step found")

        current_step = steps[idx]
        state.setdefault("comments", []).append({
            "step": current_step["key"],
            "step_name": current_step["name"],
            "user_id": user_id,
            "action": "approved",
            "comment": comment or "",
            "time": _now().isoformat(),
        })

        next_idx = idx + 1
        if next_idx >= len(steps):
            # All steps completed
            instance.status = "approved"
            instance.current_step = None
            instance.complete_time = _now()
        else:
            next_step = steps[next_idx]
            state["current_step_index"] = next_idx
            instance.current_step = next_step["key"]

        instance.variables = _dump_variables(state)
        instance.update_time = _now()
        await self.db.flush()

        return _instance_to_dict(instance)

    async def reject_task(
        self, task_id: str, user_id: str, reason: str | None = None
    ) -> dict[str, Any]:
        """Reject the current step — terminates the process."""
        instance = await self._get_instance_or_404(task_id)
        if instance.status != "pending":
            raise BusinessError(
                code="WORKFLOW_TASK_ALREADY_DONE",
                message="Task has already been processed",
            )

        state = _parse_variables(instance.variables)
        steps: list[dict[str, Any]] = state.get("steps", [])
        idx: int = state.get("current_step_index", 0)
        current_step = steps[idx] if idx < len(steps) else {"key": "unknown", "name": "未知"}

        state.setdefault("comments", []).append({
            "step": current_step["key"],
            "step_name": current_step["name"],
            "user_id": user_id,
            "action": "rejected",
            "comment": reason or "",
            "time": _now().isoformat(),
        })

        instance.status = "rejected"
        instance.current_step = None
        instance.variables = _dump_variables(state)
        instance.update_time = _now()
        instance.complete_time = _now()
        await self.db.flush()

        return _instance_to_dict(instance)

    async def get_process_status(self, business_key: str) -> dict[str, Any] | None:
        """Return the latest process instance for a business key."""
        stmt = (
            select(ProcessInstance)
            .where(ProcessInstance.business_key == business_key)
            .order_by(ProcessInstance.create_time.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        inst = result.scalar_one_or_none()
        if not inst:
            return None
        return _instance_to_dict(inst)

    async def get_process_history(self, business_key: str) -> list[dict[str, Any]]:
        """Return all process instances for a business key, earliest first."""
        stmt = (
            select(ProcessInstance)
            .where(ProcessInstance.business_key == business_key)
            .order_by(ProcessInstance.create_time.asc())
        )
        result = await self.db.execute(stmt)
        return [_instance_to_dict(i) for i in result.scalars().all()]

    async def get_my_initiated(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> PageResult:
        """Return processes initiated by the given user, newest first."""
        base = select(ProcessInstance).where(
            ProcessInstance.submitter_id == user_id
        )
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        stmt = base.order_by(ProcessInstance.create_time.desc())
        offset = (page - 1) * limit
        result = await self.db.execute(stmt.offset(offset).limit(limit))
        records = [_instance_to_dict(i) for i in result.scalars().all()]
        return PageResult(total=total or 0, page=page, size=limit, records=records)

    async def get_instance(self, instance_id: str) -> dict[str, Any]:
        """Get a single instance by ID."""
        inst = await self._get_instance_or_404(instance_id)
        return _instance_to_dict(inst)

    # ── Process definitions (read-only) ─────────────────────────────────

    async def list_process_definitions(
        self, category: str | None = None
    ) -> list[dict[str, Any]]:
        """List in-code process definitions, optionally filtered by category."""
        result: list[dict[str, Any]] = []
        for key, pd in PROCESS_DEFINITIONS.items():
            cat = pd.get("category", "")
            if category and cat != category:
                continue
            result.append({
                "defId": key,
                "processKey": key,
                "processName": pd["name"],
                "category": cat,
                "steps": [s["name"] for s in pd["steps"]],
                "status": "active",
            })
        return result

    async def get_process_definition(self, process_key: str) -> dict[str, Any]:
        """Get a single in-code process definition."""
        pd = _get_process_def(process_key)
        return {
            "defId": process_key,
            "processKey": process_key,
            "processName": pd["name"],
            "category": pd.get("category", ""),
            "steps": [
                {"key": s["key"], "name": s["name"], "role": s["role"]}
                for s in pd["steps"]
            ],
            "status": "active",
        }

    # ── Internal helpers ────────────────────────────────────────────────

    async def _get_instance_or_404(self, instance_id: str) -> ProcessInstance:
        inst = await self.db.get(ProcessInstance, instance_id)
        if not inst:
            raise ResourceNotFoundError("流程实例", instance_id)
        return inst


# ── Helper functions ─────────────────────────────────────────────────────


def _eval_condition(field_val: Any, op: str, target: Any) -> bool:
    """Evaluate a simple comparison for conditional step resolution."""
    if op == "gt":
        try:
            return float(field_val) > float(target)
        except (TypeError, ValueError):
            return False
    if op == "gte":
        try:
            return float(field_val) >= float(target)
        except (TypeError, ValueError):
            return False
    if op == "lt":
        try:
            return float(field_val) < float(target)
        except (TypeError, ValueError):
            return False
    if op == "eq":
        return field_val == target
    return False


def _instance_to_dict(inst: ProcessInstance) -> dict[str, Any]:
    state = _parse_variables(inst.variables)
    steps: list[dict[str, Any]] = state.get("steps", [])
    idx: int = state.get("current_step_index", 0)
    current_step_name = ""
    current_step_role = ""
    if idx < len(steps):
        cs = steps[idx]
        current_step_name = cs.get("name", "")
        current_step_role = cs.get("role", "")

    return {
        "instanceId": inst.instance_id,
        "processDefId": inst.process_def_id,
        "processKey": inst.process_key,
        "businessKey": inst.business_key,
        "submitterId": inst.submitter_id,
        "status": inst.status,
        "currentStep": inst.current_step,
        "currentStepName": current_step_name,
        "currentStepRole": current_step_role,
        "variables": state.get("business_data", {}),
        "comments": state.get("comments", []),
        "createdAt": inst.create_time.isoformat() if inst.create_time else None,
        "updatedAt": inst.update_time.isoformat() if inst.update_time else None,
        "completedAt": inst.complete_time.isoformat() if inst.complete_time else None,
    }
