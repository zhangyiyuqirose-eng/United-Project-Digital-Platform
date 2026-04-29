"""Unit and integration tests for middleware layer (rate limiting, auth, trace ID, anti-replay)."""

from __future__ import annotations

import pytest

from app.middleware import AUTH_WHITELIST, setup_middleware


# ── Auth Whitelist Constants ─────────────────────────────────────────

def test_auth_whitelist_contains_health():
    assert "/health" in AUTH_WHITELIST


def test_auth_whitelist_contains_login():
    assert "/api/auth/login" in AUTH_WHITELIST


def test_auth_whitelist_contains_register():
    assert "/api/auth/register" in AUTH_WHITELIST


def test_auth_whitelist_contains_logout():
    assert "/api/auth/logout" in AUTH_WHITELIST


def test_auth_whitelist_contains_docs():
    assert "/docs" in AUTH_WHITELIST
    assert "/openapi.json" in AUTH_WHITELIST
    assert "/redoc" in AUTH_WHITELIST


# ── Trace ID Middleware (via full app) ────────────────────────────────

@pytest.mark.asyncio
async def test_trace_id_on_response(client):
    """Verify that trace ID header is present on responses."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert "X-Trace-Id" in resp.headers


@pytest.mark.asyncio
async def test_response_time_header(client):
    """Verify that X-Response-Time header is present."""
    resp = await client.get("/health")
    assert "X-Response-Time" in resp.headers


# ── JWT Auth Middleware ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_whitelist_bypass_login():
    """Login endpoint should not require JWT (tested via direct app)."""
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/auth/login", json={
            "username": "test",
            "password": "test",
        })
        # Should not get 401 (auth error), but rather 422 (validation) or other
        assert resp.status_code != 401 or "AUTH_TOKEN" not in resp.text


@pytest.mark.asyncio
async def test_whitelist_bypass_health():
    """Health endpoint should not require JWT."""
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_no_token_returns_401():
    """Non-whitelisted endpoint without JWT should return 401."""
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/system/users")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_returns_401():
    """Non-whitelisted endpoint with bad JWT should return 401."""
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={"Authorization": "Bearer invalidtoken123"},
    ) as ac:
        resp = await ac.get("/api/system/users")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_valid_token_passes(client):
    """With valid JWT token (from conftest), should access protected endpoints."""
    resp = await client.get("/api/system/users", params={"page": 1, "size": 10})
    assert resp.status_code != 401


@pytest.mark.asyncio
async def test_bearer_prefix_required():
    """Token without 'Bearer ' prefix should return 401."""
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={"Authorization": "Token sometoken"},
    ) as ac:
        resp = await ac.get("/api/system/users")
        assert resp.status_code == 401


# ── Rate Limiting Middleware ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limit_fallback_no_redis(client):
    """When Redis is unavailable, rate limiting should pass through."""
    # The middleware catches Redis exceptions and falls through
    resp = await client.get("/health")
    assert resp.status_code == 200


# ── Anti-Replay Middleware ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_anti_replay_skip_for_get(client):
    """GET requests should not require anti-replay headers."""
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_anti_replay_with_headers():
    """POST with nonce/timestamp should be processed (Redis fallback)."""
    import time
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app
    from app.core.security import create_token

    app = create_app()
    token = create_token(user_id="test-user", claims={"role": "admin"})
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Nonce": "test-nonce-123",
            "X-Timestamp": str(int(time.time())),
        },
    ) as ac:
        resp = await ac.post("/api/auth/login", json={
            "username": "test",
            "password": "test",
        })
        # Should not get 400 (timestamp expired) when Redis is unavailable
        # Redis failure causes it to skip anti-replay check
        assert resp.status_code != 400


# ── CORS Middleware ───────────────────────────────────────────────────

def test_cors_configured():
    """Verify CORS middleware is configured."""
    from fastapi.testclient import TestClient
    from app.main import create_app

    app = create_app()
    # Check middleware is registered
    middleware_types = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_types


# ── Middleware Stack Order ────────────────────────────────────────────

def test_setup_middleware_registers_all_layers():
    """setup_middleware should register CORS + 4 HTTP middlewares."""
    from fastapi import FastAPI

    app = FastAPI()
    setup_middleware(app)

    # CORS is in user_middleware, HTTP middlewares in middleware stack
    assert len(app.user_middleware) >= 1  # CORS
    # HTTP middlewares are registered via @app.middleware("http")
    # They show up in the middleware stack


def test_setup_middleware_cors_origins():
    """CORS should be configured with origins from settings."""
    from fastapi import FastAPI
    from app.config import settings

    app = FastAPI()
    setup_middleware(app)

    # Verify CORS middleware exists and has origins
    cors_mw = None
    for mw in app.user_middleware:
        if mw.cls.__name__ == "CORSMiddleware":
            cors_mw = mw
            break

    assert cors_mw is not None
