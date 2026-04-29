"""FastAPI application factory and lifespan setup."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.core.logging import bind_trace_id, get_logger, setup_logging
from app.exceptions import register_exception_handlers
from app.middleware import setup_middleware

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging(json_logs=False, log_level="INFO")
    bind_trace_id("startup")
    logger.info(event="UPDG Digital Platform starting up")
    logger.info(event="database_url", db=settings.database_url.split("@")[-1] if "@" in settings.database_url else "sqlite")
    yield
    logger.info(event="Shutting down")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="UPDG Digital Platform",
        description="Project Digital Operations Management Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    setup_middleware(app)
    register_exception_handlers(app)

    # ── Register routers ─────────────────────────────────────────────
    from app.api.auth import router as auth_router
    from app.api.system import router as system_router
    from app.api.project import router as project_router
    from app.api.business import router as business_router
    from app.api.cost import router as cost_router
    from app.api.resource import router as resource_router
    from app.api.timesheet import router as timesheet_router
    from app.api.knowledge import router as knowledge_router
    from app.api.notify import router as notify_router
    from app.api.workflow import router as workflow_router
    from app.api.audit import router as audit_router
    from app.api.quality import router as quality_router
    from app.api.file import router as file_router
    from app.api.ai import router as ai_router
    from app.api.report import router as report_router
    from app.api.integration import router as integration_router
    from app.api.gateway import router as gateway_router

    api_prefix = "/api"
    app.include_router(auth_router, prefix=f"{api_prefix}/auth")
    app.include_router(system_router, prefix=f"{api_prefix}/system")
    app.include_router(project_router, prefix=f"{api_prefix}/project")
    app.include_router(business_router, prefix=f"{api_prefix}/business")
    app.include_router(cost_router, prefix=f"{api_prefix}/cost")
    app.include_router(resource_router, prefix=f"{api_prefix}/resource")
    app.include_router(timesheet_router, prefix=f"{api_prefix}/timesheet")
    app.include_router(knowledge_router, prefix=f"{api_prefix}/knowledge")
    app.include_router(notify_router, prefix=f"{api_prefix}/notify")
    app.include_router(workflow_router, prefix=f"{api_prefix}/workflow")
    app.include_router(audit_router, prefix=f"{api_prefix}/audit")
    app.include_router(quality_router, prefix=f"{api_prefix}/quality")
    app.include_router(file_router, prefix=f"{api_prefix}/file")
    app.include_router(ai_router, prefix=f"{api_prefix}/ai")
    app.include_router(report_router, prefix=f"{api_prefix}/report")
    app.include_router(integration_router, prefix=f"{api_prefix}/integration")
    app.include_router(gateway_router, prefix=f"{api_prefix}/gateway")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
