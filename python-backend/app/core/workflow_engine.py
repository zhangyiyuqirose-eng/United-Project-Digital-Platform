"""Python state machine workflow engine — replaces Flowable BPMN.

Implements 3 approval workflows as Python state machines:
1. Project Initiation Approval (projectInitApproval)
2. Project Change Approval (projectChangeApproval)
3. Project Close Approval (projectCloseApproval)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow.models import ProcessDefinition, ProcessInstance


class WorkflowStep:
    def __init__(self, name, approver_role, condition=None,
                 next_step=None, reject_to="start", description=""):
        self.name = name
        self.approver_role = approver_role
        self.condition = condition
        self.next_step = next_step
        self.reject_to = reject_to
        self.description = description


class WorkflowDefinition:
    def __init__(self, process_key, process_name, category, steps=None, description=""):
        self.process_key = process_key
        self.process_name = process_name
        self.category = category
        self.steps = steps or []
        self.description = description


# ── Workflow Definitions ────────────────────────────────────────────

def _build_workflows() -> dict[str, WorkflowDefinition]:
    init_wf = WorkflowDefinition(
        process_key="projectInitApproval",
        process_name="项目立项审批",
        category="project",
        description="PMO审核 → 部门领导审核 → 预算判断(>500万需UPDG领导审批) → 财务审核",
        steps=[
            WorkflowStep("pmo_review", "pmo", next_step="dept_leader", description="PMO审核"),
            WorkflowStep("dept_leader", "dept_leader", next_step="budget_check", description="部门领导审核"),
            WorkflowStep("budget_check", "updg_leader", condition="budget > 5000000",
                        next_step="finance_review", description="预算>500万需UPDG领导审批"),
            WorkflowStep("finance_review", "finance", next_step="end", description="财务审核"),
        ],
    )

    change_wf = WorkflowDefinition(
        process_key="projectChangeApproval",
        process_name="项目变更审批",
        category="project",
        description="PM审核 → PMO审核 → 重大变更判断 → 结束",
        steps=[
            WorkflowStep("pm_review", "pm", next_step="pmo_review", description="PM审核"),
            WorkflowStep("pmo_review", "pmo", next_step="major_check", description="PMO审核"),
            WorkflowStep("major_check", "updg_leader", condition="is_major_change == true",
                        next_step="end", description="重大变更需UPDG领导审批"),
        ],
    )

    close_wf = WorkflowDefinition(
        process_key="projectCloseApproval",
        process_name="项目结项审批",
        category="project",
        description="PM确认 → QA审核 → 财务结算 → PMO审核 → 文档归档",
        steps=[
            WorkflowStep("pm_confirm", "pm", next_step="qa_review", description="PM确认"),
            WorkflowStep("qa_review", "qa", next_step="finance_settlement", description="QA审核"),
            WorkflowStep("finance_settlement", "finance", next_step="pmo_review", description="财务结算"),
            WorkflowStep("pmo_review", "pmo", next_step="doc_archive", description="PMO审核"),
            WorkflowStep("doc_archive", "pmo", next_step="end", description="文档归档"),
        ],
    )

    return {w.process_key: w for w in [init_wf, change_wf, close_wf]}


WORKFLOW_REGISTRY = _build_workflows()


# ── Workflow Engine ─────────────────────────────────────────────────

class WorkflowEngine:
    """State machine engine for approval workflows."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_workflow(self, process_key: str, business_key: str,
                             submitter_id: str, variables: dict | None = None) -> dict:
        """Start a new workflow instance."""
        wf_def = WORKFLOW_REGISTRY.get(process_key)
        if not wf_def:
            return {"error": f"Unknown workflow: {process_key}"}

        instance_id = str(uuid.uuid4())
        first_step = wf_def.steps[0].name if wf_def.steps else None

        instance = ProcessInstance(
            instance_id=instance_id,
            process_def_id=process_key,
            process_key=process_key,
            business_key=business_key,
            submitter_id=submitter_id,
            status="running",
            current_step=first_step,
            variables=json.dumps(variables or {}, ensure_ascii=False),
        )
        self.db.add(instance)
        await self.db.flush()

        return {
            "instanceId": instance_id,
            "processKey": process_key,
            "businessKey": business_key,
            "currentStep": first_step,
            "status": "running",
            "stepDescription": wf_def.steps[0].description if wf_def.steps else "",
        }

    async def approve_task(self, instance_id: str, approver_role: str,
                           comment: str | None = None) -> dict:
        """Approve current step and advance to next."""
        instance = await self._get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}

        wf_def = WORKFLOW_REGISTRY.get(instance.process_key)
        if not wf_def:
            return {"error": "Unknown workflow"}

        current_step = self._find_step(wf_def, instance.current_step)
        if not current_step:
            return {"error": "Invalid current step"}

        next_step_name = current_step.next_step
        if next_step_name == "end" or not next_step_name:
            instance.status = "completed"
            instance.current_step = "end"
            instance.complete_time = datetime.now(timezone.utc)
        else:
            instance.current_step = next_step_name
            next_step = self._find_step(wf_def, next_step_name)
            if next_step:
                # Check condition-based routing
                if next_step.condition:
                    variables = json.loads(instance.variables or "{}")
                    if not self._evaluate_condition(next_step.condition, variables):
                        # Skip to next next step
                        instance.current_step = next_step.next_step or "end"

        instance.update_time = datetime.now(timezone.utc)
        await self.db.flush()

        step_desc = ""
        next_s = self._find_step(wf_def, instance.current_step)
        if next_s:
            step_desc = next_s.description

        return {
            "instanceId": instance_id,
            "status": instance.status,
            "currentStep": instance.current_step,
            "stepDescription": step_desc,
            "message": "审批通过" if instance.status == "running" else "流程已完成",
        }

    async def reject_task(self, instance_id: str, reason: str | None = None) -> dict:
        """Reject current step and return to start."""
        instance = await self._get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}

        instance.status = "rejected"
        instance.update_time = datetime.now(timezone.utc)
        await self.db.flush()

        return {
            "instanceId": instance_id,
            "status": "rejected",
            "reason": reason or "审批未通过",
            "message": "已退回到发起人",
        }

    async def cancel_workflow(self, instance_id: str) -> dict:
        """Cancel a workflow instance."""
        instance = await self._get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}

        instance.status = "cancelled"
        instance.complete_time = datetime.now(timezone.utc)
        await self.db.flush()

        return {"instanceId": instance_id, "status": "cancelled"}

    async def get_status(self, instance_id: str) -> dict:
        """Get current workflow status."""
        instance = await self._get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}

        wf_def = WORKFLOW_REGISTRY.get(instance.process_key)
        current_step_obj = self._find_step(wf_def, instance.current_step)

        return {
            "instanceId": instance_id,
            "processKey": instance.process_key,
            "processName": wf_def.process_name if wf_def else "",
            "businessKey": instance.business_key,
            "status": instance.status,
            "currentStep": instance.current_step,
            "stepDescription": current_step_obj.description if current_step_obj else "",
            "submitterId": instance.submitter_id,
            "createdAt": str(instance.create_time),
            "completedAt": str(instance.complete_time) if instance.complete_time else None,
        }

    async def get_history(self, business_key: str) -> list[dict]:
        """Get all workflow instances for a business key."""
        stmt = select(ProcessInstance).where(
            ProcessInstance.business_key == business_key
        ).order_by(ProcessInstance.create_time.asc())
        result = await self.db.execute(stmt)
        items = result.scalars().all()

        return [
            {
                "instanceId": i.instance_id,
                "processKey": i.process_key,
                "status": i.status,
                "currentStep": i.current_step,
                "submitterId": i.submitter_id,
                "createdAt": str(i.create_time),
            }
            for i in items
        ]

    def get_workflow_definitions(self) -> list[dict]:
        """List all registered workflow definitions."""
        return [
            {
                "processKey": wf.process_key,
                "processName": wf.process_name,
                "category": wf.category,
                "description": wf.description,
                "steps": [
                    {
                        "name": s.name,
                        "approverRole": s.approver_role,
                        "description": s.description,
                        "condition": s.condition,
                    }
                    for s in wf.steps
                ],
            }
            for wf in WORKFLOW_REGISTRY.values()
        ]

    # ── Internal helpers ────────────────────────────────────────────

    async def _get_instance(self, instance_id: str) -> ProcessInstance | None:
        stmt = select(ProcessInstance).where(
            ProcessInstance.instance_id == instance_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    def _find_step(self, wf_def: WorkflowDefinition | None, step_name: str | None) -> WorkflowStep | None:
        if not wf_def or not step_name:
            return None
        for step in wf_def.steps:
            if step.name == step_name:
                return step
        return None

    def _evaluate_condition(self, condition: str, variables: dict) -> bool:
        """Evaluate a condition string against workflow variables."""
        if not condition:
            return True
        try:
            expr = condition
            for key, value in variables.items():
                expr = expr.replace(key, str(value).lower() if isinstance(value, bool) else str(value))
            expr = expr.replace("== true", "== True").replace("== false", "== False")
            return bool(eval(expr))
        except Exception:
            return False
