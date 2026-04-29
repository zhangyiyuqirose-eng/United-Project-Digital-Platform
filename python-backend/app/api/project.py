"""Project API router — thin request/response layer over ProjectService."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.dependencies import get_current_user
from app.services.project_service import ProjectService

router = APIRouter(tags=["project"])


def _service(db: AsyncSession) -> ProjectService:
    return ProjectService(db)


def _model_dump(m: BaseModel) -> dict:
    return m.model_dump(exclude_unset=True)


# ── Projects ─────────────────────────────────────────────────────────

@router.get("")
async def list_projects(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    status: str | None = None, project_type: str | None = None,
    manager_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    result = await _service(db).list_projects(page=page, size=size, status=status, project_type=project_type, manager_id=manager_id)
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.get("/list")
async def list_projects_alias(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    status: str | None = None, project_type: str | None = None,
    manager_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    return await list_projects(page=page, size=size, status=status, project_type=project_type, manager_id=manager_id, db=db)


@router.post("/create")
async def create_project_alias(req: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_project(req, db)


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _service(db).get_project(project_id)
    from app.services.project_service import _project_to_dict
    return ApiResponse(code="SUCCESS", message="success", data=_project_to_dict(project))


@router.post("")
async def create_project(req: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    result = await _service(db).create_project(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=result)


@router.put("/{project_id}")
async def update_project(project_id: str, req: ProjectUpdateRequest, db: AsyncSession = Depends(get_db)):
    await _service(db).update_project(project_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    await _service(db).delete_project(project_id)
    return ApiResponse(code="SUCCESS", message="success")


# ── Tasks ────────────────────────────────────────────────────────────

@router.get("/{project_id}/tasks")
async def list_tasks(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_tasks(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/tasks")
async def create_task(project_id: str, req: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_task(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/tasks/{task_id}")
async def update_task(task_id: str, req: TaskUpdateRequest, db: AsyncSession = Depends(get_db)):
    await _service(db).update_task(task_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    await _service(db).delete_task(task_id)
    return ApiResponse(code="SUCCESS", message="success")


# ── Risks ────────────────────────────────────────────────────────────

@router.get("/{project_id}/risks")
async def list_risks(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_risks(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/risks")
async def create_risk(project_id: str, req: RiskCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_risk(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/risks/{risk_id}")
async def update_risk(risk_id: str, req: RiskUpdateRequest, db: AsyncSession = Depends(get_db)):
    await _service(db).update_risk(risk_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/risks/{risk_id}")
async def delete_risk(risk_id: str, db: AsyncSession = Depends(get_db)):
    await _service(db).delete_risk(risk_id)
    return ApiResponse(code="SUCCESS", message="success")


# ── Health / Critical Path / Gantt ───────────────────────────────────

@router.get("/{project_id}/health-score")
async def get_health_score(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_health_score(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/{project_id}/critical-path")
async def get_critical_path(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_critical_path(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/{project_id}/gantt")
async def get_gantt_data(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_gantt_data(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── WBS ──────────────────────────────────────────────────────────────

@router.get("/{project_id}/wbs")
async def get_wbs(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_wbs(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/wbs")
async def create_wbs_node(project_id: str, req: WbsCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_wbs_node(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Sprints ──────────────────────────────────────────────────────────

@router.get("/{project_id}/sprints")
async def list_sprints(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_sprints(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/sprints")
async def create_sprint(project_id: str, req: SprintCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_sprint(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Milestones ───────────────────────────────────────────────────────

@router.get("/{project_id}/milestones")
async def list_milestones(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_milestones(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/milestones")
async def create_milestone(project_id: str, req: MilestoneCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_milestone(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Changes ──────────────────────────────────────────────────────────

@router.get("/{project_id}/changes")
async def list_changes(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_changes(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/changes")
async def create_change(project_id: str, req: ChangeCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_change(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Close ────────────────────────────────────────────────────────────

@router.post("/{project_id}/close")
async def close_project(project_id: str, req: CloseProjectRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).close_project(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Pre-Initiation ───────────────────────────────────────────────────

@router.get("/{project_id}/pre-initiation")
async def get_pre_initiation(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_pre_initiation(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/pre-initiation")
async def create_pre_initiation(project_id: str, req: PreInitiationRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_pre_initiation(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Alerts ───────────────────────────────────────────────────────────

@router.get("/{project_id}/alerts")
async def list_alerts(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_alerts(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Repos ────────────────────────────────────────────────────────────

@router.get("/{project_id}/repos")
async def list_repos(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_repos(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/repos")
async def create_repo(project_id: str, req: RepoCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_repo(project_id, req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Builds ───────────────────────────────────────────────────────────

@router.get("/{project_id}/builds")
async def list_builds(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_builds(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/build")
async def create_build(req: BuildCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_build(req.project_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Dependencies ─────────────────────────────────────────────────────

@router.get("/{project_id}/dependencies")
async def list_dependencies(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_dependencies(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/dependency")
async def create_dependency(req: DependencyCreateRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_dependency(req.model_dump())
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.delete("/dependency/{dep_id}")
async def delete_dependency(dep_id: str, db: AsyncSession = Depends(get_db)):
    await _service(db).delete_dependency(dep_id)
    return ApiResponse(code="SUCCESS", message="success")


# ── Portfolio ────────────────────────────────────────────────────────

@router.get("/portfolio")
async def portfolio(db: AsyncSession = Depends(get_db)):
    data = await _service(db).portfolio()
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/portfolio/summary")
async def portfolio_summary(db: AsyncSession = Depends(get_db)):
    data = await _service(db).portfolio_summary()
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/portfolio/resource-conflicts")
async def resource_conflicts(db: AsyncSession = Depends(get_db)):
    data = await _service(db).resource_conflicts()
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Project Progress ─────────────────────────────────────────────────

@router.put("/{project_id}/progress")
async def update_project_progress(
    project_id: str, req: ProjectProgressRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).update_progress(project_id, req.wbs_json)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/{project_id}/progress")
async def get_project_progress(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_progress(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/evm")
async def calculate_evm(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).calculate_evm(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/{project_id}/wbs/decompose")
async def wbs_decompose(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).wbs_decompose(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Close Settlement ─────────────────────────────────────────────────

@router.put("/close/{close_id}/complete")
async def complete_close(close_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).complete_close(close_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Task Extensions ──────────────────────────────────────────────────

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_task(task_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/tasks/{task_id}/progress")
async def update_task_progress(
    task_id: str, req: TaskProgressRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).update_task_progress(task_id, req.progress)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/tasks/{task_id}/block")
async def block_task(
    task_id: str, req: TaskBlockRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).block_task(task_id, req.reason)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/tasks/{task_id}/complete")
async def complete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).complete_task(task_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/tasks/project/{project_id}/overdue")
async def list_overdue_tasks(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_overdue_tasks(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/tasks/project/{project_id}/tree")
async def get_task_tree(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_task_tree(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Sprint Extensions ────────────────────────────────────────────────

@router.put("/sprints/{sprint_id}")
async def update_sprint(
    sprint_id: str, req: SprintUpdateRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).update_sprint(sprint_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/sprints/{sprint_id}")
async def get_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_sprint(sprint_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/sprints/project/{project_id}/page")
async def list_sprints_paginated(
    project_id: str,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    data = await _service(db).list_sprints_paginated(project_id, page=page, size=size)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/sprints/{sprint_id}/complete")
async def complete_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).complete_sprint(sprint_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/sprints/{sprint_id}/cancel")
async def cancel_sprint(sprint_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).cancel_sprint(sprint_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/sprints/project/{project_id}/active")
async def get_active_sprint(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).get_active_sprint(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Alert Extensions ─────────────────────────────────────────────────

@router.get("/progress-alerts")
async def list_all_alerts(db: AsyncSession = Depends(get_db)):
    data = await _service(db).list_all_alerts()
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/progress-alerts/check")
async def check_and_generate_alerts(db: AsyncSession = Depends(get_db)):
    data = await _service(db).check_and_generate_alerts()
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/progress-alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).resolve_alert(alert_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Risk Extensions ──────────────────────────────────────────────────

@router.get("/risks/project/{project_id}/stats")
async def risk_stats(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).risk_stats(project_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/risks/{risk_id}/assess")
async def assess_risk(risk_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).assess_risk(risk_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/risks/{risk_id}/status")
async def update_risk_status(
    risk_id: str, req: RiskStatusRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).update_risk_status(risk_id, req.status)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Code Repo Sync ───────────────────────────────────────────────────

@router.post("/code-repo/{repo_id}/sync")
async def sync_repo(repo_id: str, db: AsyncSession = Depends(get_db)):
    data = await _service(db).sync_repo(repo_id)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Pre-Initiation Extensions ────────────────────────────────────────

@router.post("/pre-init")
async def create_pre_init_submit(req: PreInitiationSubmitRequest, db: AsyncSession = Depends(get_db)):
    data = await _service(db).create_pre_initiation_submit(req.project_id, req.model_dump(exclude_unset=True))
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.put("/pre-init/{pre_id}/submit")
async def submit_pre_init(pre_id: str, db: AsyncSession = Depends(get_db)):
    svc = _service(db)
    stmt = __import__("sqlalchemy", fromlist=["select"]).select(
        __import__("app.models.project.models", fromlist=["PreInitiation"]).PreInitiation
    ).where(
        __import__("app.models.project.models", fromlist=["PreInitiation"]).PreInitiation.pre_id == pre_id
    )
    from sqlalchemy import select
    from app.models.project.models import PreInitiation
    result = await svc.db.execute(select(PreInitiation).where(PreInitiation.pre_id == pre_id))
    pi = result.scalar_one_or_none()
    if not pi:
        from app.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("预立项", pre_id)
    pi.status = "submitted"
    await svc.db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"preId": pre_id})


@router.put("/pre-init/{pre_id}/approve")
async def approve_pre_init(
    pre_id: str, req: PreInitiationApproveRequest, db: AsyncSession = Depends(get_db),
):
    data = await _service(db).approve_pre_initiation(pre_id, req.approved, req.comment)
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/pre-init/{pre_id}")
async def get_pre_init_detail(pre_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.project.models import PreInitiation
    result = await db.execute(select(PreInitiation).where(PreInitiation.pre_id == pre_id))
    pi = result.scalar_one_or_none()
    if not pi:
        from app.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("预立项", pre_id)
    data = {
        "preId": pi.pre_id, "projectId": pi.project_id,
        "feasibilityStudy": pi.feasibility_study, "businessCase": pi.business_case,
        "initialBudget": float(pi.initial_budget) if pi.initial_budget else None,
        "expectedRoi": float(pi.expected_roi) if pi.expected_roi else None,
        "status": pi.status,
    }
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.get("/pre-init/dept/{dept_id}")
async def list_pre_init_by_dept(
    dept_id: str,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    data = await _service(db).list_pre_initiation_by_dept(dept_id, page=page, size=size, status=status)
    return ApiResponse(code="SUCCESS", message="success", data=data)


# ── Request schemas ──────────────────────────────────────────────────

class ProjectCreateRequest(BaseModel):
    project_name: str
    project_code: str | None = None
    project_type: str | None = None
    status: str | None = None
    manager_id: str | None = None
    manager_name: str | None = None
    department_id: str | None = None
    department_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    budget: float | None = None
    customer: str | None = None
    description: str | None = None
    progress: int | None = None

class ProjectUpdateRequest(BaseModel):
    project_name: str | None = None
    project_code: str | None = None
    project_type: str | None = None
    status: str | None = None
    manager_id: str | None = None
    manager_name: str | None = None
    budget: float | None = None
    customer: str | None = None
    description: str | None = None
    progress: int | None = None
    health_score: float | None = None

class TaskCreateRequest(BaseModel):
    task_name: str
    assignee_id: str | None = None
    assignee_name: str | None = None
    status: str | None = None
    priority: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    progress: int | None = None
    wbs_id: str | None = None
    parent_task_id: str | None = None

class TaskUpdateRequest(BaseModel):
    task_name: str | None = None
    assignee_id: str | None = None
    assignee_name: str | None = None
    status: str | None = None
    priority: str | None = None
    progress: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

class RiskCreateRequest(BaseModel):
    risk_code: str | None = None
    risk_name: str
    risk_type: str | None = None
    category: str | None = None
    description: str | None = None
    probability: int | None = None
    impact: int | None = None
    level: str | None = None
    severity: str | None = None
    status: str | None = None
    mitigation: str | None = None
    mitigation_plan: str | None = None
    contingency_plan: str | None = None
    owner_id: str | None = None
    owner_name: str | None = None

class RiskUpdateRequest(BaseModel):
    risk_name: str | None = None
    probability: int | None = None
    impact: int | None = None
    level: str | None = None
    severity: str | None = None
    status: str | None = None
    mitigation: str | None = None
    mitigation_plan: str | None = None
    contingency_plan: str | None = None

class WbsCreateRequest(BaseModel):
    name: str
    code: str | None = None
    parent_id: str | None = None
    level: int | None = None
    sort_order: int | None = None

class SprintCreateRequest(BaseModel):
    sprint_name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    goal: str | None = None

class MilestoneCreateRequest(BaseModel):
    milestone_name: str
    planned_date: datetime | None = None
    actual_date: datetime | None = None
    status: str | None = None

class ChangeCreateRequest(BaseModel):
    change_type: str | None = None
    change_reason: str | None = None
    impact_analysis: str | None = None
    status: str | None = None
    approver_id: str | None = None

class CloseProjectRequest(BaseModel):
    close_type: str | None = None
    summary: str | None = None
    lessons_learned: str | None = None

class PreInitiationRequest(BaseModel):
    feasibility_study: str | None = None
    business_case: str | None = None
    initial_budget: float | None = None
    expected_roi: float | None = None
    status: str | None = None

class RepoCreateRequest(BaseModel):
    repo_name: str
    repo_url: str | None = None
    branch: str | None = None
    last_commit: str | None = None


class BuildCreateRequest(BaseModel):
    project_id: str
    build_number: str | None = None
    build_status: str | None = None
    build_time: datetime | None = None
    duration: int | None = None
    log_url: str | None = None


class DependencyCreateRequest(BaseModel):
    project_id: str
    depends_on_project_id: str
    dependency_type: str | None = None
    description: str | None = None


class ProjectProgressRequest(BaseModel):
    wbs_json: str


class TaskProgressRequest(BaseModel):
    progress: int = 0


class TaskBlockRequest(BaseModel):
    reason: str


class SprintUpdateRequest(BaseModel):
    sprint_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    goal: str | None = None


class RiskStatusRequest(BaseModel):
    status: str


class PreInitiationSubmitRequest(BaseModel):
    project_id: str
    feasibility_study: str | None = None
    business_case: str | None = None
    initial_budget: float | None = None
    expected_roi: float | None = None


class PreInitiationApproveRequest(BaseModel):
    approved: bool
    comment: str | None = None
