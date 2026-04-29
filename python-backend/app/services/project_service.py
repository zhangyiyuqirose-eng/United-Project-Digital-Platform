"""Project domain service — extracted business logic from router.

All DB operations live here; the router becomes a thin request/response layer.
"""

from __future__ import annotations

import uuid
from collections import defaultdict, deque
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError
from app.models.project.models import (
    BuildRecord, CodeRepo, PreInitiation, ProgressAlert, Project,
    ProjectChange, ProjectClose, ProjectDependency, ProjectMilestone,
    ProjectRisk, ProjectTask, Sprint, WbsNode,
)


class ProjectService:
    """Encapsulates all project-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Project CRUD ─────────────────────────────────────────────────

    async def list_projects(
        self, page: int = 1, size: int = 10,
        status: str | None = None, project_type: str | None = None,
        manager_id: str | None = None,
    ) -> PageResult:
        base = select(Project)
        filters: list = []
        if status:
            filters.append(Project.status == status)
        if project_type:
            filters.append(Project.project_type == project_type)
        if manager_id:
            filters.append(Project.manager_id == manager_id)
        if filters:
            base = base.where(*filters)

        total_stmt = select(func.count(Project.project_id))
        if filters:
            total_stmt = total_stmt.where(*filters)
        total = (await self.db.execute(total_stmt)).scalar() or 0

        stmt = base.order_by(Project.create_time.desc().nullslast())
        offset = (page - 1) * size
        result = await self.db.execute(stmt.offset(offset).limit(size))
        items = result.scalars().all()
        return PageResult(total=total, page=page, size=size, records=[_project_to_dict(p) for p in items])

    async def get_project(self, project_id: str) -> Project:
        return await self._get_or_404(project_id)

    async def create_project(self, req: dict) -> dict:
        project = Project(
            project_id=str(uuid.uuid4()),
            project_name=req["project_name"],
            project_code=req.get("project_code"),
            project_type=req.get("project_type"),
            status=req.get("status", "draft"),
            manager_id=req.get("manager_id"),
            manager_name=req.get("manager_name"),
            department_id=req.get("department_id"),
            department_name=req.get("department_name"),
            start_date=req.get("start_date"),
            end_date=req.get("end_date"),
            budget=req.get("budget"),
            customer=req.get("customer"),
            description=req.get("description"),
            progress=req.get("progress", 0),
        )
        self.db.add(project)
        await self.db.flush()
        return {"projectId": project.project_id}

    async def update_project(self, project_id: str, updates: dict) -> None:
        project = await self._get_or_404(project_id)
        for field, value in updates.items():
            if hasattr(project, field):
                setattr(project, field, value)
        await self.db.flush()

    async def delete_project(self, project_id: str) -> None:
        project = await self._get_or_404(project_id)
        await self.db.delete(project)
        await self.db.flush()

    # ── Health Score ─────────────────────────────────────────────────

    async def get_health_score(self, project_id: str) -> dict:
        project = await self._get_or_404(project_id)
        progress_score = (project.progress or 0) / 100 * 30

        cpi = float(project.evm_cpi or 1.0)
        cost_score = min(cpi, 1.0) * 30

        risk_stmt = select(func.count()).select_from(ProjectRisk).where(
            ProjectRisk.project_id == project_id, ProjectRisk.status == "open"
        )
        open_risks = (await self.db.execute(risk_stmt)).scalar() or 0
        risk_score = max(0, 20 - open_risks * 2)

        task_stmt = select(
            func.count().label("total"),
            func.sum(case((ProjectTask.status == "completed", 1), else_=0)).label("completed"),
        ).where(ProjectTask.project_id == project_id)
        task_result = await self.db.execute(task_stmt)
        row = task_result.first()
        total_tasks = row[0] if row and row[0] else 0
        completed_tasks = row[1] if row and row[1] else 0
        task_completion = (completed_tasks / total_tasks * 20) if total_tasks > 0 else 20

        health = progress_score + cost_score + risk_score + task_completion
        return {
            "projectId": project_id,
            "healthScore": round(health, 2),
            "breakdown": {
                "progress": round(progress_score, 2),
                "cost": round(cost_score, 2),
                "risk": round(risk_score, 2),
                "task": round(task_completion, 2),
            },
        }

    # ── Critical Path (CPM) ──────────────────────────────────────────

    async def get_critical_path(self, project_id: str) -> dict:
        stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()

        children: dict[str, list[str]] = defaultdict(list)
        task_map = {t.task_id: t for t in tasks}
        roots: list[str] = []
        for t in tasks:
            if t.parent_task_id and t.parent_task_id in task_map:
                children[t.parent_task_id].append(t.task_id)
            else:
                roots.append(t.task_id)

        in_degree: dict[str, int] = defaultdict(int)
        for t in tasks:
            if t.parent_task_id and t.parent_task_id in task_map:
                in_degree[t.task_id] += 1

        queue = deque([r for r in roots if in_degree[r] == 0])
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for child in children[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        dist = {t.task_id: 0 for t in tasks}
        pred = {t.task_id: None for t in tasks}
        for node in order:
            task = task_map[node]
            duration = _task_duration(task)
            for child in children[node]:
                if dist[node] + duration > dist[child]:
                    dist[child] = dist[node] + duration
                    pred[child] = node

        if not order:
            return {"criticalPath": [], "totalDuration": 0}

        end = max(order, key=lambda x: dist[x])
        path: list[str] = []
        current: str | None = end
        while current is not None:
            path.append(current)
            current = pred[current]
        path.reverse()

        return {
            "criticalPath": path,
            "totalDuration": dist[end],
            "tasks": [_task_to_dict(task_map[tid]) for tid in path],
        }

    # ── Task CRUD ─────────────────────────────────────────────────────

    async def list_tasks(self, project_id: str) -> list[dict]:
        stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
        result = await self.db.execute(stmt)
        return [_task_full_dict(t) for t in result.scalars().all()]

    async def create_task(self, project_id: str, req: dict) -> dict:
        task = ProjectTask(
            task_id=str(uuid.uuid4()), project_id=project_id,
            task_name=req["task_name"],
            assignee_id=req.get("assignee_id"),
            assignee_name=req.get("assignee_name"),
            status=req.get("status", "pending"),
            priority=req.get("priority", "medium"),
            start_date=req.get("start_date"),
            end_date=req.get("end_date"),
            progress=req.get("progress", 0),
            wbs_id=req.get("wbs_id"),
            parent_task_id=req.get("parent_task_id"),
        )
        self.db.add(task)
        await self.db.flush()
        return {"taskId": task.task_id}

    async def update_task(self, task_id: str, updates: dict) -> None:
        task = await self._task_or_404(task_id)
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)
        await self.db.flush()

    async def update_task_progress(self, task_id: str, progress: int) -> dict:
        task = await self._task_or_404(task_id)
        task.progress = max(0, min(100, progress))
        if task.progress == 100:
            task.status = "completed"
        await self.db.flush()
        return {"taskId": task.task_id, "progress": task.progress}

    async def block_task(self, task_id: str, reason: str) -> dict:
        task = await self._task_or_404(task_id)
        task.status = "blocked"
        await self.db.flush()
        return {"taskId": task.task_id, "reason": reason}

    async def complete_task(self, task_id: str) -> dict:
        task = await self._task_or_404(task_id)
        task.progress = 100
        task.status = "completed"
        await self.db.flush()
        return {"taskId": task.task_id}

    async def get_task(self, task_id: str) -> dict:
        task = await self._task_or_404_task_id(task_id)
        return _task_full_dict(task)

    async def list_overdue_tasks(self, project_id: str) -> list[dict]:
        stmt = select(ProjectTask).where(
            ProjectTask.project_id == project_id,
            ProjectTask.status.notin_(["completed", "cancelled"]),
            ProjectTask.end_date < date.today(),
        )
        result = await self.db.execute(stmt)
        return [_task_full_dict(t) for t in result.scalars().all()]

    async def get_task_tree(self, project_id: str) -> dict:
        stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        nodes = [_task_full_dict(t) for t in tasks]
        children_map: dict[str, list] = defaultdict(list)
        roots: list = []
        for n in nodes:
            pid = n.get("parentTaskId")
            if pid:
                children_map[pid].append(n)
            else:
                roots.append(n)
        return {"roots": roots, "children": dict(children_map)}

    async def delete_task(self, task_id: str) -> None:
        task = await self._task_or_404(task_id)
        await self.db.delete(task)
        await self.db.flush()

    # ── Risk CRUD ─────────────────────────────────────────────────────

    async def list_risks(self, project_id: str) -> list[dict]:
        stmt = select(ProjectRisk).where(ProjectRisk.project_id == project_id)
        result = await self.db.execute(stmt)
        return [_risk_dict(r) for r in result.scalars().all()]

    async def create_risk(self, project_id: str, req: dict) -> dict:
        risk_score = (req.get("probability") or 0) * (req.get("impact") or 0)
        risk = ProjectRisk(
            risk_id=str(uuid.uuid4()), project_id=project_id,
            risk_code=req.get("risk_code"), risk_name=req["risk_name"],
            risk_type=req.get("risk_type"), category=req.get("category"),
            description=req.get("description"),
            probability=req.get("probability"), impact=req.get("impact"),
            level=req.get("level"), severity=req.get("severity"),
            risk_score=risk_score, status=req.get("status", "open"),
            mitigation=req.get("mitigation"), mitigation_plan=req.get("mitigation_plan"),
            contingency_plan=req.get("contingency_plan"),
            owner_id=req.get("owner_id"), owner_name=req.get("owner_name"),
        )
        self.db.add(risk)
        await self.db.flush()
        return {"riskId": risk.risk_id}

    async def update_risk(self, risk_id: str, updates: dict) -> None:
        risk = await self._risk_or_404(risk_id)
        for field, value in updates.items():
            if hasattr(risk, field):
                setattr(risk, field, value)
        await self.db.flush()

    async def delete_risk(self, risk_id: str) -> None:
        risk = await self._risk_or_404(risk_id)
        await self.db.delete(risk)
        await self.db.flush()

    # ── Gantt Data ────────────────────────────────────────────────────

    async def get_gantt_data(self, project_id: str) -> list[dict]:
        stmt = select(ProjectTask).where(ProjectTask.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"taskId": t.task_id, "taskName": t.task_name, "parentTaskId": t.parent_task_id,
             "startDate": str(t.start_date) if t.start_date else None,
             "endDate": str(t.end_date) if t.end_date else None,
             "progress": t.progress, "status": t.status}
            for t in result.scalars().all()
        ]

    # ── WBS ───────────────────────────────────────────────────────────

    async def list_wbs(self, project_id: str) -> list[dict]:
        stmt = select(WbsNode).where(WbsNode.project_id == project_id).order_by(WbsNode.sort_order)
        result = await self.db.execute(stmt)
        return [
            {"wbsId": n.wbs_id, "projectId": n.project_id, "name": n.name,
             "code": n.code, "parentId": n.parent_id, "level": n.level,
             "sortOrder": n.sort_order}
            for n in result.scalars().all()
        ]

    async def create_wbs_node(self, project_id: str, req: dict) -> dict:
        node = WbsNode(
            wbs_id=str(uuid.uuid4()), project_id=project_id,
            name=req["name"], code=req.get("code"),
            parent_id=req.get("parent_id"), level=req.get("level"),
            sort_order=req.get("sort_order"),
        )
        self.db.add(node)
        await self.db.flush()
        return {"wbsId": node.wbs_id}

    # ── Sprints ───────────────────────────────────────────────────────

    async def list_sprints(self, project_id: str) -> list[dict]:
        stmt = select(Sprint).where(Sprint.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"sprintId": s.sprint_id, "projectId": s.project_id, "sprintName": s.sprint_name,
             "startDate": str(s.start_date) if s.start_date else None,
             "endDate": str(s.end_date) if s.end_date else None,
             "status": s.status, "goal": s.goal}
            for s in result.scalars().all()
        ]

    async def create_sprint(self, project_id: str, req: dict) -> dict:
        sprint = Sprint(
            sprint_id=str(uuid.uuid4()), project_id=project_id,
            sprint_name=req["sprint_name"],
            start_date=req.get("start_date"), end_date=req.get("end_date"),
            status=req.get("status", "planning"), goal=req.get("goal"),
        )
        self.db.add(sprint)
        await self.db.flush()
        return {"sprintId": sprint.sprint_id}

    async def update_sprint(self, sprint_id: str, updates: dict) -> dict:
        sprint = await self._sprint_or_404(sprint_id)
        for field, value in updates.items():
            if hasattr(sprint, field):
                setattr(sprint, field, value)
        await self.db.flush()
        return {"sprintId": sprint.sprint_id}

    async def get_sprint(self, sprint_id: str) -> dict:
        sprint = await self._sprint_or_404(sprint_id)
        return {
            "sprintId": sprint.sprint_id, "projectId": sprint.project_id,
            "sprintName": sprint.sprint_name,
            "startDate": str(sprint.start_date) if sprint.start_date else None,
            "endDate": str(sprint.end_date) if sprint.end_date else None,
            "status": sprint.status, "goal": sprint.goal,
        }

    async def list_sprints_paginated(
        self, project_id: str, page: int = 1, size: int = 10
    ) -> PageResult:
        base = select(Sprint).where(Sprint.project_id == project_id)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(base.order_by(Sprint.create_time.desc()).offset(offset).limit(size))
        items = result.scalars().all()
        records = [
            {"sprintId": s.sprint_id, "sprintName": s.sprint_name,
             "startDate": str(s.start_date) if s.start_date else None,
             "endDate": str(s.end_date) if s.end_date else None,
             "status": s.status, "goal": s.goal}
            for s in items
        ]
        return PageResult(total=total, page=page, size=size, records=records)

    async def complete_sprint(self, sprint_id: str, velocity: int | None = None) -> dict:
        sprint = await self._sprint_or_404(sprint_id)
        sprint.status = "completed"
        await self.db.flush()
        return {"sprintId": sprint.sprint_id, "velocity": velocity}

    async def cancel_sprint(self, sprint_id: str) -> dict:
        sprint = await self._sprint_or_404(sprint_id)
        sprint.status = "cancelled"
        await self.db.flush()
        return {"sprintId": sprint.sprint_id}

    async def get_active_sprint(self, project_id: str) -> dict | None:
        stmt = select(Sprint).where(
            Sprint.project_id == project_id, Sprint.status == "active"
        )
        result = await self.db.execute(stmt)
        sprint = result.scalar_one_or_none()
        if not sprint:
            return None
        return {
            "sprintId": sprint.sprint_id, "sprintName": sprint.sprint_name,
            "startDate": str(sprint.start_date) if sprint.start_date else None,
            "endDate": str(sprint.end_date) if sprint.end_date else None,
            "goal": sprint.goal,
        }

    # ── Milestones ────────────────────────────────────────────────────

    async def list_milestones(self, project_id: str) -> list[dict]:
        stmt = select(ProjectMilestone).where(ProjectMilestone.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"milestoneId": m.milestone_id, "projectId": m.project_id,
             "milestoneName": m.milestone_name,
             "plannedDate": str(m.planned_date) if m.planned_date else None,
             "actualDate": str(m.actual_date) if m.actual_date else None,
             "status": m.status}
            for m in result.scalars().all()
        ]

    async def create_milestone(self, project_id: str, req: dict) -> dict:
        m = ProjectMilestone(
            milestone_id=str(uuid.uuid4()), project_id=project_id,
            milestone_name=req["milestone_name"],
            planned_date=req.get("planned_date"), actual_date=req.get("actual_date"),
            status=req.get("status", "pending"),
        )
        self.db.add(m)
        await self.db.flush()
        return {"milestoneId": m.milestone_id}

    # ── Changes ───────────────────────────────────────────────────────

    async def list_changes(self, project_id: str) -> list[dict]:
        stmt = select(ProjectChange).where(ProjectChange.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"changeId": c.change_id, "projectId": c.project_id,
             "changeType": c.change_type, "changeReason": c.change_reason,
             "impactAnalysis": c.impact_analysis, "status": c.status,
             "approverId": c.approver_id}
            for c in result.scalars().all()
        ]

    async def create_change(self, project_id: str, req: dict) -> dict:
        c = ProjectChange(
            change_id=str(uuid.uuid4()), project_id=project_id,
            change_type=req.get("change_type"), change_reason=req.get("change_reason"),
            impact_analysis=req.get("impact_analysis"),
            status=req.get("status", "pending"), approver_id=req.get("approver_id"),
        )
        self.db.add(c)
        await self.db.flush()
        return {"changeId": c.change_id}

    # ── Close ─────────────────────────────────────────────────────────

    async def close_project(self, project_id: str, req: dict) -> dict:
        project = await self._get_or_404(project_id)
        project.status = "closed"
        project.actual_end_time = datetime.now(timezone.utc)
        pc = ProjectClose(
            close_id=str(uuid.uuid4()), project_id=project_id,
            close_type=req.get("close_type"),
            close_date=datetime.now(timezone.utc),
            summary=req.get("summary"), lessons_learned=req.get("lessons_learned"),
            status="pending",
        )
        self.db.add(pc)
        await self.db.flush()
        return {"closeId": pc.close_id}

    # ── Pre-Initiation ────────────────────────────────────────────────

    async def get_pre_initiation(self, project_id: str) -> dict | None:
        stmt = select(PreInitiation).where(PreInitiation.project_id == project_id)
        result = await self.db.execute(stmt)
        pi = result.scalar_one_or_none()
        if not pi:
            return None
        return {
            "preId": pi.pre_id, "projectId": pi.project_id,
            "feasibilityStudy": pi.feasibility_study, "businessCase": pi.business_case,
            "initialBudget": float(pi.initial_budget) if pi.initial_budget else None,
            "expectedRoi": float(pi.expected_roi) if pi.expected_roi else None,
            "status": pi.status,
        }

    async def create_pre_initiation(self, project_id: str, req: dict) -> dict:
        pi = PreInitiation(
            pre_id=str(uuid.uuid4()), project_id=project_id,
            feasibility_study=req.get("feasibility_study"),
            business_case=req.get("business_case"),
            initial_budget=req.get("initial_budget"),
            expected_roi=req.get("expected_roi"),
            status=req.get("status", "draft"),
        )
        self.db.add(pi)
        await self.db.flush()
        return {"preId": pi.pre_id}

    # ── Alerts ────────────────────────────────────────────────────────

    async def list_alerts(self, project_id: str) -> list[dict]:
        stmt = select(ProgressAlert).where(ProgressAlert.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"alertId": a.alert_id, "projectId": a.project_id, "taskId": a.task_id,
             "alertType": a.alert_type, "alertLevel": a.alert_level,
             "message": a.message, "isHandled": a.is_handled}
            for a in result.scalars().all()
        ]

    # ── Code Repos ────────────────────────────────────────────────────

    async def list_repos(self, project_id: str) -> list[dict]:
        stmt = select(CodeRepo).where(CodeRepo.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"repoId": r.repo_id, "projectId": r.project_id,
             "repoName": r.repo_name, "repoUrl": r.repo_url,
             "branch": r.branch, "lastCommit": r.last_commit}
            for r in result.scalars().all()
        ]

    async def create_repo(self, project_id: str, req: dict) -> dict:
        repo = CodeRepo(
            repo_id=str(uuid.uuid4()), project_id=project_id,
            repo_name=req["repo_name"], repo_url=req.get("repo_url"),
            branch=req.get("branch"), last_commit=req.get("last_commit"),
        )
        self.db.add(repo)
        await self.db.flush()
        return {"repoId": repo.repo_id}

    # ── Build Records ─────────────────────────────────────────────────

    async def list_builds(self, project_id: str) -> list[dict]:
        stmt = select(BuildRecord).where(BuildRecord.project_id == project_id).order_by(
            BuildRecord.create_time.desc()
        )
        result = await self.db.execute(stmt)
        return [
            {"buildId": b.build_id, "projectId": b.project_id,
             "buildNumber": b.build_number, "buildStatus": b.build_status,
             "buildTime": str(b.build_time) if b.build_time else None,
             "duration": b.duration, "logUrl": b.log_url}
            for b in result.scalars().all()
        ]

    # ── Dependencies ──────────────────────────────────────────────────

    async def list_dependencies(self, project_id: str) -> list[dict]:
        stmt = select(ProjectDependency).where(ProjectDependency.project_id == project_id)
        result = await self.db.execute(stmt)
        return [
            {"depId": d.dep_id, "projectId": d.project_id,
             "dependsOnProjectId": d.depends_on_project_id,
             "dependencyType": d.dependency_type, "description": d.description}
            for d in result.scalars().all()
        ]

    # ── Portfolio ─────────────────────────────────────────────────────

    async def portfolio(self) -> dict:
        stmt = select(Project.status, func.count(Project.project_id), func.sum(Project.budget)).group_by(
            Project.status
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        total_budget = (await self.db.execute(select(func.sum(Project.budget)))).scalar() or 0
        return {
            "byStatus": [
                {"status": r[0], "count": r[1], "budget": float(r[2]) if r[2] else 0}
                for r in rows
            ],
            "totalBudget": float(total_budget),
        }

    async def portfolio_summary(self) -> dict:
        stmt = select(Project)
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        total = len(projects)
        by_status: dict[str, int] = defaultdict(int)
        total_budget = Decimal("0")
        total_actual = Decimal("0")
        for p in projects:
            by_status[p.status] += 1
            total_budget += p.budget or Decimal("0")
        risk_stmt = select(func.count()).select_from(ProjectRisk).where(
            ProjectRisk.severity == "high", ProjectRisk.status == "open"
        )
        high_risks = (await self.db.execute(risk_stmt)).scalar() or 0
        return {
            "totalProjects": total,
            "byStatus": dict(by_status),
            "totalBudget": float(total_budget),
            "totalActual": float(total_actual),
            "highRisks": high_risks,
        }

    async def resource_conflicts(self) -> list[dict]:
        stmt = select(Project).where(Project.status.in_(["active", "in_progress"]))
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        conflicts = []
        for i, a in enumerate(projects):
            for b in projects[i + 1:]:
                if (
                    a.start_date and b.end_date and a.start_date <= b.end_date
                    and b.start_date and a.end_date and b.start_date <= a.end_date
                    and a.manager_id == b.manager_id
                ):
                    conflicts.append({
                        "projectA": a.project_name,
                        "projectB": b.project_name,
                        "manager": a.manager_name,
                        "overlapStart": str(max(a.start_date, b.start_date)),
                        "overlapEnd": str(min(a.end_date, b.end_date)),
                    })
        return conflicts

    # ── Project Progress ──────────────────────────────────────────────

    async def update_progress(self, project_id: str, wbs_json: str) -> dict:
        project = await self._get_or_404(project_id)
        project.wbs_json = wbs_json
        await self.db.flush()
        return {"projectId": project_id}

    async def get_progress(self, project_id: str) -> dict:
        project = await self._get_or_404(project_id)
        return {
            "projectId": project_id,
            "progress": project.progress,
            "wbsJson": project.wbs_json,
            "status": project.status,
        }

    async def calculate_evm(self, project_id: str) -> dict:
        project = await self._get_or_404(project_id)
        pv = project.evm_pv or Decimal("0")
        ev = project.evm_ev or Decimal("0")
        ac = project.evm_ac or Decimal("0")
        cpi = (ev / ac) if ac > 0 else Decimal("1.0")
        spi = (ev / pv) if pv > 0 else Decimal("1.0")
        project.evm_cpi = cpi
        project.evm_spi = spi
        await self.db.flush()
        return {"cpi": float(cpi), "spi": float(spi), "pv": float(pv), "ev": float(ev), "ac": float(ac)}

    async def wbs_decompose(self, project_id: str) -> dict:
        project = await self._get_or_404(project_id)
        nodes = [
            {"name": "Initiation", "level": 1, "children": [
                {"name": "Requirements", "level": 2},
                {"name": "Feasibility", "level": 2},
            ]},
            {"name": "Design", "level": 1, "children": [
                {"name": "Architecture", "level": 2},
                {"name": "UI/UX", "level": 2},
            ]},
            {"name": "Development", "level": 1, "children": [
                {"name": "Frontend", "level": 2},
                {"name": "Backend", "level": 2},
                {"name": "Testing", "level": 2},
            ]},
            {"name": "Deployment", "level": 1},
        ]
        return {"projectId": project_id, "projectName": project.project_name, "wbs": nodes}

    async def complete_close(self, close_id: str) -> dict:
        stmt = select(ProjectClose).where(ProjectClose.close_id == close_id)
        result = await self.db.execute(stmt)
        pc = result.scalar_one_or_none()
        if not pc:
            raise ResourceNotFoundError("Close", close_id)
        pc.status = "completed"
        project = await self._get_or_404(pc.project_id)
        project.status = "closed"
        await self.db.flush()
        return {"closeId": close_id, "status": "completed"}

    # ── Alerts (cross-project) ────────────────────────────────────────

    async def list_all_alerts(self) -> list[dict]:
        stmt = select(ProgressAlert).where(ProgressAlert.is_handled == 0)
        result = await self.db.execute(stmt)
        return [
            {"alertId": a.alert_id, "projectId": a.project_id, "taskId": a.task_id,
             "alertType": a.alert_type, "alertLevel": a.alert_level,
             "message": a.message, "isHandled": a.is_handled}
            for a in result.scalars().all()
        ]

    async def check_and_generate_alerts(self) -> dict:
        stmt = select(Project).where(Project.status.in_(["active", "in_progress"]))
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        count = 0
        for p in projects:
            overdue_stmt = select(func.count()).select_from(ProjectTask).where(
                ProjectTask.project_id == p.project_id,
                ProjectTask.status.notin_(["completed", "cancelled"]),
                ProjectTask.end_date < date.today(),
            )
            overdue = (await self.db.execute(overdue_stmt)).scalar() or 0
            if overdue > 0:
                alert = ProgressAlert(
                    alert_id=str(uuid.uuid4()),
                    project_id=p.project_id,
                    alert_type="overdue",
                    alert_level="warning",
                    message=f"{overdue} overdue tasks in {p.project_name}",
                    is_handled=0,
                )
                self.db.add(alert)
                count += 1
        await self.db.flush()
        return {"generated": count}

    async def resolve_alert(self, alert_id: str) -> dict:
        stmt = select(ProgressAlert).where(ProgressAlert.alert_id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()
        if not alert:
            raise ResourceNotFoundError("告警", alert_id)
        alert.is_handled = 1
        await self.db.flush()
        return {"alertId": alert_id, "status": "resolved"}

    # ── Risk extended ─────────────────────────────────────────────────

    async def list_risks_paginated(
        self, project_id: str, page: int = 1, size: int = 10, status: str | None = None
    ) -> PageResult:
        base = select(ProjectRisk).where(ProjectRisk.project_id == project_id)
        if status:
            base = base.where(ProjectRisk.status == status)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(
            base.order_by(ProjectRisk.create_time.desc()).offset(offset).limit(size)
        )
        return PageResult(
            total=total, page=page, size=size,
            records=[_risk_dict(r) for r in result.scalars().all()],
        )

    async def risk_stats(self, project_id: str) -> dict:
        stmt = select(ProjectRisk.severity, func.count()).where(
            ProjectRisk.project_id == project_id
        ).group_by(ProjectRisk.severity)
        result = await self.db.execute(stmt)
        by_severity = {r[0]: r[1] for r in result.all()}
        open_stmt = select(func.count()).select_from(ProjectRisk).where(
            ProjectRisk.project_id == project_id, ProjectRisk.status == "open"
        )
        open_count = (await self.db.execute(open_stmt)).scalar() or 0
        return {"bySeverity": by_severity, "open": open_count}

    async def assess_risk(self, risk_id: str) -> dict:
        risk = await self._risk_or_404(risk_id)
        score = (risk.probability or 0) * (risk.impact or 0)
        risk.risk_score = score
        if score >= 16:
            risk.severity = "high"
        elif score >= 8:
            risk.severity = "medium"
        else:
            risk.severity = "low"
        await self.db.flush()
        return {"riskId": risk_id, "score": score, "severity": risk.severity}

    async def update_risk_status(self, risk_id: str, status: str) -> dict:
        risk = await self._risk_or_404(risk_id)
        risk.status = status
        await self.db.flush()
        return {"riskId": risk_id, "status": status}

    # ── Code repo sync ────────────────────────────────────────────────

    async def sync_repo(self, repo_id: str) -> dict:
        stmt = select(CodeRepo).where(CodeRepo.repo_id == repo_id)
        result = await self.db.execute(stmt)
        repo = result.scalar_one_or_none()
        if not repo:
            raise ResourceNotFoundError("仓库", repo_id)
        repo.last_commit = "synced-" + str(uuid.uuid4())[:8]
        await self.db.flush()
        return {"repoId": repo_id, "status": "synced", "lastCommit": repo.last_commit}

    async def create_build(self, project_id: str, req: dict) -> dict:
        build = BuildRecord(
            build_id=str(uuid.uuid4()), project_id=project_id,
            build_number=req.get("build_number"),
            build_status=req.get("build_status", "success"),
            build_time=req.get("build_time"),
            duration=req.get("duration"),
            log_url=req.get("log_url"),
        )
        self.db.add(build)
        await self.db.flush()
        return {"buildId": build.build_id}

    async def create_dependency(self, req: dict) -> dict:
        dep = ProjectDependency(
            dep_id=str(uuid.uuid4()),
            project_id=req["project_id"],
            depends_on_project_id=req["depends_on_project_id"],
            dependency_type=req.get("dependency_type"),
            description=req.get("description"),
        )
        self.db.add(dep)
        await self.db.flush()
        return {"depId": dep.dep_id}

    async def delete_dependency(self, dep_id: str) -> None:
        stmt = select(ProjectDependency).where(ProjectDependency.dep_id == dep_id)
        result = await self.db.execute(stmt)
        dep = result.scalar_one_or_none()
        if dep:
            await self.db.delete(dep)
            await self.db.flush()

    async def create_pre_initiation_submit(self, project_id: str, req: dict) -> dict:
        pi = PreInitiation(
            pre_id=str(uuid.uuid4()), project_id=project_id,
            feasibility_study=req.get("feasibility_study"),
            business_case=req.get("business_case"),
            initial_budget=req.get("initial_budget"),
            expected_roi=req.get("expected_roi"),
            status="submitted",
        )
        self.db.add(pi)
        await self.db.flush()
        return {"preId": pi.pre_id}

    async def approve_pre_initiation(self, pre_id: str, approved: bool, comment: str | None = None) -> dict:
        stmt = select(PreInitiation).where(PreInitiation.pre_id == pre_id)
        result = await self.db.execute(stmt)
        pi = result.scalar_one_or_none()
        if not pi:
            raise ResourceNotFoundError("预立项", pre_id)
        pi.status = "approved" if approved else "rejected"
        await self.db.flush()
        return {"preId": pre_id, "status": pi.status}

    async def list_pre_initiation_by_dept(
        self, dept_id: str, page: int = 1, size: int = 10, status: str | None = None
    ) -> PageResult:
        base = select(PreInitiation).where(PreInitiation.project_id.like(f"{dept_id}%"))
        if status:
            base = base.where(PreInitiation.status == status)
        total = (await self.db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar() or 0
        offset = (page - 1) * size
        result = await self.db.execute(base.order_by(PreInitiation.create_time.desc()).offset(offset).limit(size))
        items = result.scalars().all()
        records = [
            {"preId": pi.pre_id, "projectId": pi.project_id,
             "status": pi.status, "initialBudget": float(pi.initial_budget) if pi.initial_budget else None}
            for pi in items
        ]
        return PageResult(total=total, page=page, size=size, records=records)

    # ── Internal helpers ──────────────────────────────────────────────

    async def _get_or_404(self, project_id: str) -> Project:
        stmt = select(Project).where(Project.project_id == project_id)
        p = (await self.db.execute(stmt)).scalar_one_or_none()
        if not p:
            raise ResourceNotFoundError("项目", project_id)
        return p

    async def _task_or_404(self, task_id: str) -> ProjectTask:
        stmt = select(ProjectTask).where(ProjectTask.task_id == task_id)
        t = (await self.db.execute(stmt)).scalar_one_or_none()
        if not t:
            raise ResourceNotFoundError("任务", task_id)
        return t

    async def _risk_or_404(self, risk_id: str) -> ProjectRisk:
        stmt = select(ProjectRisk).where(ProjectRisk.risk_id == risk_id)
        r = (await self.db.execute(stmt)).scalar_one_or_none()
        if not r:
            raise ResourceNotFoundError("风险", risk_id)
        return r

    async def _sprint_or_404(self, sprint_id: str) -> Sprint:
        stmt = select(Sprint).where(Sprint.sprint_id == sprint_id)
        s = (await self.db.execute(stmt)).scalar_one_or_none()
        if not s:
            raise ResourceNotFoundError("Sprint", sprint_id)
        return s

    async def _task_or_404_task_id(self, task_id: str) -> ProjectTask:
        stmt = select(ProjectTask).where(ProjectTask.task_id == task_id)
        t = (await self.db.execute(stmt)).scalar_one_or_none()
        if not t:
            raise ResourceNotFoundError("任务", task_id)
        return t


# ── Dict converters (pure functions) ─────────────────────────────────

def _project_to_dict(p: Project) -> dict:
    return {
        "projectId": p.project_id, "projectName": p.project_name,
        "projectCode": p.project_code, "projectType": p.project_type,
        "status": p.status, "managerId": p.manager_id, "managerName": p.manager_name,
        "departmentId": p.department_id, "departmentName": p.department_name,
        "startDate": str(p.start_date) if p.start_date else None,
        "endDate": str(p.end_date) if p.end_date else None,
        "budget": float(p.budget) if p.budget else None,
        "customer": p.customer, "description": p.description,
        "progress": p.progress,
        "healthScore": float(p.health_score) if p.health_score else None,
        "evmPv": float(p.evm_pv) if p.evm_pv else None,
        "evmEv": float(p.evm_ev) if p.evm_ev else None,
        "evmAc": float(p.evm_ac) if p.evm_ac else None,
        "evmCpi": float(p.evm_cpi) if p.evm_cpi else None,
        "evmSpi": float(p.evm_spi) if p.evm_spi else None,
    }


def _task_to_dict(t: ProjectTask) -> dict:
    return {
        "taskId": t.task_id, "taskName": t.task_name,
        "startDate": str(t.start_date) if t.start_date else None,
        "endDate": str(t.end_date) if t.end_date else None,
        "progress": t.progress, "status": t.status,
    }


def _task_full_dict(t: ProjectTask) -> dict:
    return {
        "taskId": t.task_id, "projectId": t.project_id, "taskName": t.task_name,
        "assigneeId": t.assignee_id, "assigneeName": t.assignee_name,
        "status": t.status, "priority": t.priority,
        "startDate": str(t.start_date) if t.start_date else None,
        "endDate": str(t.end_date) if t.end_date else None,
        "progress": t.progress, "wbsId": t.wbs_id, "parentTaskId": t.parent_task_id,
    }


def _risk_dict(r: ProjectRisk) -> dict:
    return {
        "riskId": r.risk_id, "projectId": r.project_id, "riskCode": r.risk_code,
        "riskName": r.risk_name, "riskType": r.risk_type, "category": r.category,
        "description": r.description, "probability": r.probability,
        "impact": r.impact, "level": r.level, "severity": r.severity,
        "riskScore": float(r.risk_score) if r.risk_score else None,
        "status": r.status, "ownerId": r.owner_id, "ownerName": r.owner_name,
    }


def _task_duration(t: ProjectTask) -> int:
    if t.start_date and t.end_date:
        d1 = t.start_date if isinstance(t.start_date, date) else date.fromisoformat(str(t.start_date)[:10])
        d2 = t.end_date if isinstance(t.end_date, date) else date.fromisoformat(str(t.end_date)[:10])
        return (d2 - d1).days
    return 1
