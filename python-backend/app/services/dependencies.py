"""Service dependency injection for FastAPI.

Provides ``Depends(get_*_service)`` callables that router functions can use
instead of directly importing and constructing service instances.

Usage::

    @router.get("/list")
    async def list_items(service: SomeService = Depends(get_some_service)):
        return await service.list_page()
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

# ── Existing services ───────────────────────────────────────────────────

from app.services.project_service import ProjectService
from app.services.ai_service import AIService
from app.services.report_service import ReportService

# ── New services created in this phase ──────────────────────────────────

from app.services.timesheet_service import TimesheetService
from app.services.quality_service import QualityService
from app.services.audit_service import AuditService
from app.services.file_service import FileService
from app.services.workflow_service import WorkflowService
from app.services.cost_service import CostService
from app.services.business_service import BusinessService
from app.services.knowledge_service import KnowledgeService
from app.services.notify_service import NotifyService
from app.services.resource_service import ResourceService
from app.services.auth_service import AuthService
from app.services.system_service import SystemService


# ── Dependency factories ────────────────────────────────────────────────


async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)


async def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


async def get_timesheet_service(db: AsyncSession = Depends(get_db)) -> TimesheetService:
    return TimesheetService(db)


async def get_quality_service(db: AsyncSession = Depends(get_db)) -> QualityService:
    return QualityService(db)


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


async def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    return FileService(db)


async def get_workflow_service(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)


async def get_cost_service(db: AsyncSession = Depends(get_db)) -> CostService:
    return CostService(db)


async def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    return BusinessService(db)


async def get_knowledge_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


async def get_notify_service(db: AsyncSession = Depends(get_db)) -> NotifyService:
    return NotifyService(db)


async def get_resource_service(db: AsyncSession = Depends(get_db)) -> ResourceService:
    return ResourceService(db)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_system_service(db: AsyncSession = Depends(get_db)) -> SystemService:
    return SystemService(db)
