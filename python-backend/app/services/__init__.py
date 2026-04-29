"""Service layer — business logic extracted from API routers.

Domain services encapsulate all database operations so that API routers
become thin request/response translation layers.

Usage in routers::

    from fastapi import Depends
    from app.services.dependencies import get_project_service

    @router.get("/list")
    async def list_projects(
        page: int = 1,
        service: ProjectService = Depends(get_project_service),
    ):
        result = await service.list_projects(page=page)
        return ApiResponse.success(data=result)
"""

from app.services.base import BaseService
from app.services.project_service import ProjectService
from app.services.ai_service import AIService
from app.services.report_service import ReportService
from app.services.timesheet_service import TimesheetService
from app.services.quality_service import QualityService
from app.services.audit_service import AuditService
from app.services.file_service import FileService

__all__ = [
    "BaseService",
    "ProjectService",
    "AIService",
    "ReportService",
    "TimesheetService",
    "QualityService",
    "AuditService",
    "FileService",
]
