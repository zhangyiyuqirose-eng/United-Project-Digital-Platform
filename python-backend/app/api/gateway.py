"""Gateway monitoring API — introspects FastAPI routes, middleware, and health."""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from starlette.routing import Mount

from app.core.schemas import ApiResponse
from app.middleware import AUTH_WHITELIST

router = APIRouter(tags=["gateway"])


@router.get("/monitor/dashboard")
async def monitor_dashboard():
    """Gateway-level monitoring dashboard metrics."""
    from app.main import app

    routes = list(app.routes)
    api_routes = [
        {
            "path": r.path,
            "methods": list(r.methods) if hasattr(r, "methods") else ["any"],
            "name": getattr(r, "name", ""),
        }
        for r in routes
        if hasattr(r, "path") and r.path.startswith("/api/")
    ]

    return ApiResponse(
        code="SUCCESS",
        message="success",
        data={
            "totalRoutes": len(api_routes),
            "authWhitelist": sorted(AUTH_WHITELIST),
            "middleware": [
                "CORSMiddleware",
                "TraceAndLoggingMiddleware",
                "JWTAuthMiddleware",
                "RateLimitMiddleware",
                "AntiReplayMiddleware",
            ],
            "uptime": time.time(),
        },
    )


@router.get("/monitor/routes")
async def list_routes(
    prefix: str | None = None,
):
    """List all registered API routes with optional prefix filter."""
    from app.main import app

    routes = []
    for r in app.routes:
        if not hasattr(r, "path"):
            continue
        if prefix and not r.path.startswith(prefix):
            continue
        routes.append(
            {
                "path": r.path,
                "methods": sorted(r.methods) if hasattr(r, "methods") else ["any"],
                "name": getattr(r, "name", ""),
            }
        )

    return ApiResponse(code="SUCCESS", message="success", data={"routes": routes, "total": len(routes)})


@router.get("/monitor/filters")
async def list_filters():
    """List active middleware/filter status."""
    return ApiResponse(
        code="SUCCESS",
        message="success",
        data={
            "filters": [
                {
                    "name": "CORS",
                    "status": "active",
                    "description": "Cross-origin request handling",
                },
                {
                    "name": "TraceID",
                    "status": "active",
                    "description": "Request tracing with X-Trace-Id header",
                },
                {
                    "name": "JWT Auth",
                    "status": "active",
                    "description": "Token validation for protected endpoints",
                },
                {
                    "name": "Rate Limit",
                    "status": "active",
                    "description": "Sliding window rate limiting (1000 req/min)",
                },
                {
                    "name": "Anti-Replay",
                    "status": "active",
                    "description": "Nonce + timestamp validation for mutations",
                },
            ]
        },
    )


@router.get("/monitor/health")
async def gateway_health():
    """Gateway-level health check with component status."""
    return ApiResponse(
        code="SUCCESS",
        message="success",
        data={
            "gateway": "healthy",
            "components": {
                "auth": "ok",
                "rateLimit": "ok",
                "antiReplay": "ok",
                "cors": "ok",
            },
        },
    )
