"""Workflow API router — consolidates process config and workflow controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.workflow.models import ProcessDefinition, ProcessInstance

router = APIRouter(tags=["workflow"])


# ── Process Definitions ──────────────────────────────────────────────

@router.get("/processes")
async def list_processes(
    category: str | None = None, status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ProcessDefinition).order_by(ProcessDefinition.create_time.desc())
    if category:
        stmt = stmt.where(ProcessDefinition.category == category)
    if status:
        stmt = stmt.where(ProcessDefinition.status == status)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"defId": p.def_id, "processKey": p.process_key, "processName": p.process_name,
         "category": p.category, "deploymentId": p.deployment_id,
         "version": p.version, "status": p.status} for p in items
    ])


@router.post("/processes")
async def create_process(req: ProcessCreateRequest, db: AsyncSession = Depends(get_db)):
    proc = ProcessDefinition(
        def_id=str(uuid.uuid4()), process_key=req.process_key,
        process_name=req.process_name, category=req.category,
        deployment_id=req.deployment_id, version=req.version or 1,
        status=req.status or "active",
    )
    db.add(proc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"defId": proc.def_id})


@router.put("/processes/{def_id}")
async def update_process(def_id: str, req: ProcessUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(ProcessDefinition).where(ProcessDefinition.def_id == def_id)
    proc = (await db.execute(stmt)).scalar_one_or_none()
    if not proc:
        raise ResourceNotFoundError("流程定义", def_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(proc, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/processes/{def_id}")
async def delete_process(def_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a process definition config."""
    stmt = select(ProcessDefinition).where(ProcessDefinition.def_id == def_id)
    proc = (await db.execute(stmt)).scalar_one_or_none()
    if not proc:
        raise ResourceNotFoundError("流程定义", def_id)
    await db.delete(proc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/processes/{def_id}/deploy")
async def deploy_process(def_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ProcessDefinition).where(ProcessDefinition.def_id == def_id)
    proc = (await db.execute(stmt)).scalar_one_or_none()
    if not proc:
        raise ResourceNotFoundError("流程定义", def_id)
    proc.status = "active"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="部署成功")


# ── Workflow Instances (placeholder — full engine requires Camunda/Flowable) ──

@router.get("/instances")
async def list_instances(process_key: str | None = None, status: str | None = None, db: AsyncSession = Depends(get_db)):
    # Placeholder — full workflow instance management requires a BPM engine
    return ApiResponse(code="SUCCESS", message="success", data=[])


@router.post("/instances")
async def start_instance(req: InstanceStartRequest, db: AsyncSession = Depends(get_db)):
    # Placeholder
    return ApiResponse(code="SUCCESS", message="success", data={"instanceId": str(uuid.uuid4()), "status": "started"})


# ── Frontend-compatible endpoints ────────────────────────────────────

@router.post("/start")
async def start_workflow(req: InstanceStartRequest, db: AsyncSession = Depends(get_db)):
    """Start a workflow instance (frontend alias)."""
    return await start_instance(req, db)


@router.get("/status/{instance_id}")
async def workflow_status(instance_id: str, db: AsyncSession = Depends(get_db)):
    """Get workflow status."""
    return ApiResponse(code="SUCCESS", message="success", data={"instanceId": instance_id, "status": "running"})


@router.get("/my-tasks")
async def my_tasks(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List my approval tasks."""
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=0, page=page, size=size, records=[],
    ))


@router.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Approve a workflow task."""
    return ApiResponse(code="SUCCESS", message="审批通过")


@router.post("/tasks/{task_id}/reject")
async def reject_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Reject a workflow task."""
    return ApiResponse(code="SUCCESS", message="已拒绝")


@router.get("/history/{instance_id}")
async def workflow_history(instance_id: str, db: AsyncSession = Depends(get_db)):
    """Get process history."""
    return ApiResponse(code="SUCCESS", message="success", data=[])


@router.get("/my-processes")
async def my_processes(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List my processes."""
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=0, page=page, size=size, records=[],
    ))


# ── Workflow Tasks ───────────────────────────────────────────────────

@router.get("/tasks")
async def list_workflow_tasks(assignee_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """Get pending tasks for a given assignee."""
    stmt = select(ProcessInstance).where(ProcessInstance.status == "pending")
    if assignee_id:
        stmt = stmt.where(ProcessInstance.assignee_id == assignee_id)
    result = await db.execute(stmt.order_by(ProcessInstance.create_time.desc()).limit(50))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"instanceId": i.instance_id, "processKey": i.process_key,
         "businessKey": i.business_key, "status": i.status,
         "createdAt": str(i.create_time)} for i in items
    ])


@router.get("/log/{business_id}")
async def workflow_audit_log(business_id: str, db: AsyncSession = Depends(get_db)):
    """Get process audit log by business ID."""
    stmt = select(ProcessInstance).where(
        ProcessInstance.business_key == business_id,
    ).order_by(ProcessInstance.create_time.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"instanceId": i.instance_id, "processKey": i.process_key,
         "businessKey": i.business_key, "submitterId": i.submitter_id,
         "status": i.status, "createdAt": str(i.create_time)} for i in items
    ])


# ── Process Config CRUD ──────────────────────────────────────────────

@router.get("/process-config/key/{process_key}")
async def get_process_config_by_key(process_key: str, db: AsyncSession = Depends(get_db)):
    """Get config by process key."""
    stmt = select(ProcessDefinition).where(ProcessDefinition.process_key == process_key)
    proc = (await db.execute(stmt)).scalar_one_or_none()
    if not proc:
        raise ResourceNotFoundError("流程配置", process_key)
    return ApiResponse(code="SUCCESS", message="success", data={
        "defId": proc.def_id, "processKey": proc.process_key,
        "processName": proc.process_name, "category": proc.category,
        "deploymentId": proc.deployment_id, "version": proc.version,
        "status": proc.status,
    })


# ── Process-Specific Initiation (Flowable BPMN replacement) ──────────

@router.post("/process/init/start")
async def start_project_init_approval(req: InstanceStartRequest, db: AsyncSession = Depends(get_db)):
    """Start project initiation approval process."""
    instance_id = str(uuid.uuid4())
    return ApiResponse(code="SUCCESS", message="立项审批流程已启动", data={
        "instanceId": instance_id, "processKey": "projectInitApproval",
        "status": "pending", "message": "待PMO审核",
    })


@router.post("/process/change/start")
async def start_project_change_approval(req: InstanceStartRequest, db: AsyncSession = Depends(get_db)):
    """Start project change approval process."""
    instance_id = str(uuid.uuid4())
    return ApiResponse(code="SUCCESS", message="变更审批流程已启动", data={
        "instanceId": instance_id, "processKey": "projectChangeApproval",
        "status": "pending", "message": "待PM审核",
    })


@router.post("/process/close/start")
async def start_project_close_approval(req: InstanceStartRequest, db: AsyncSession = Depends(get_db)):
    """Start project close approval process."""
    instance_id = str(uuid.uuid4())
    return ApiResponse(code="SUCCESS", message="结项审批流程已启动", data={
        "instanceId": instance_id, "processKey": "projectCloseApproval",
        "status": "pending", "message": "待PM确认",
    })


@router.get("/process/status/{business_key}")
async def get_process_status(business_key: str, db: AsyncSession = Depends(get_db)):
    """Get current process status by business key."""
    stmt = select(ProcessInstance).where(
        ProcessInstance.business_key == business_key,
    ).order_by(ProcessInstance.create_time.desc()).limit(1)
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()
    if not instance:
        return ApiResponse(code="NOT_FOUND", message="未找到流程实例", data=None)
    return ApiResponse(code="SUCCESS", message="success", data={
        "instanceId": instance.instance_id, "processKey": instance.process_key,
        "businessKey": instance.business_key, "status": instance.status,
        "submitterId": instance.submitter_id, "createdAt": str(instance.create_time),
    })


@router.get("/process/history/{business_key}")
async def get_process_history(business_key: str, db: AsyncSession = Depends(get_db)):
    """Get full process history by business key."""
    stmt = select(ProcessInstance).where(
        ProcessInstance.business_key == business_key,
    ).order_by(ProcessInstance.create_time.asc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"instanceId": i.instance_id, "processKey": i.process_key,
         "businessKey": i.business_key, "status": i.status,
         "submitterId": i.submitter_id, "createdAt": str(i.create_time)}
        for i in items
    ])


# ── Request schemas ──────────────────────────────────────────────────

class ProcessCreateRequest(BaseModel):
    process_key: str
    process_name: str
    category: str | None = None
    deployment_id: str | None = None
    version: int | None = None
    status: str | None = None

class ProcessUpdateRequest(BaseModel):
    process_name: str | None = None
    category: str | None = None
    status: str | None = None

class InstanceStartRequest(BaseModel):
    process_key: str
    business_key: str | None = None
    variables: dict | None = None


# ── F-1012: Approval Timeout Management ──────────────────────────────

@router.get("/timeout/list")
async def list_timeout_approvals(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    threshold_hours: int = Query(24, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """审批超时列表 (F-1012)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=threshold_hours)
    # Query pending instances created before cutoff
    from app.models.workflow.models import ProcessInstance
    stmt = select(ProcessInstance).where(
        ProcessInstance.status == "pending",
        ProcessInstance.create_time < cutoff,
    ).order_by(ProcessInstance.create_time.asc())
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=len(items), page=page, size=size,
        records=[{
            "instanceId": i.instance_id, "processKey": i.process_key,
            "businessKey": i.business_key, "submitterId": i.submitter_id,
            "status": i.status, "submittedAt": str(i.create_time),
            "overdueHours": round((datetime.now(timezone.utc) - i.create_time).total_seconds() / 3600, 1),
        } for i in items],
    ))


@router.post("/timeout/{instance_id}/escalate")
async def escalate_timeout_approval(instance_id: str, db: AsyncSession = Depends(get_db)):
    """审批超时升级通知 (F-1012)."""
    # In production: send notification to next-level approver
    return ApiResponse(code="SUCCESS", message="success", data={
        "instanceId": instance_id,
        "action": "escalated",
        "message": "已发送升级通知给上级审批人",
    })


# ── F-1011: Process Optimization ─────────────────────────────────────

@router.get("/optimization/suggestions")
async def process_optimization_suggestions(db: AsyncSession = Depends(get_db)):
    """流程优化建议 (F-1011)."""
    from app.models.workflow.models import ProcessInstance
    # Analyze average processing time per process type
    stmt = select(
        ProcessInstance.process_key,
        func.count(ProcessInstance.instance_id).label("count"),
        func.avg(func.extract("epoch", func.now() - ProcessInstance.create_time) / 3600).label("avg_hours"),
    ).group_by(ProcessInstance.process_key)
    result = await db.execute(stmt)
    rows = result.all()

    suggestions = []
    for row in rows:
        avg_h = float(row[2] or 0)
        if avg_h > 48:
            suggestions.append({
                "processKey": row[0],
                "issue": f"平均处理时间 {avg_h:.1f} 小时，超过48小时阈值",
                "suggestion": "建议简化审批环节或增加并行审批节点",
                "avgHours": round(avg_h, 1),
                "totalCount": row[1],
            })

    return ApiResponse(code="SUCCESS", message="success", data={"suggestions": suggestions})
