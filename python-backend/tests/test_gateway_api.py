"""Integration tests for gateway monitoring API."""

import pytest


# ── Monitor Dashboard ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_monitor_dashboard(client):
    resp = await client.get("/api/gateway/monitor/dashboard")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "totalRoutes" in data
    assert "uptime" in data
    assert data["totalRoutes"] > 0


# ── Routes List ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_monitor_routes(client):
    resp = await client.get("/api/gateway/monitor/routes")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "routes" in data
    assert isinstance(data["routes"], list)
    assert len(data["routes"]) > 0


@pytest.mark.asyncio
async def test_monitor_routes_with_prefix_filter(client):
    resp = await client.get("/api/gateway/monitor/routes", params={"prefix": "/api/auth"})
    assert resp.status_code == 200
    data = resp.json()["data"]["routes"]
    assert all("/api/auth" in r["path"] for r in data)


# ── Filters/Middleware ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_monitor_filters(client):
    resp = await client.get("/api/gateway/monitor/filters")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "filters" in data
    assert isinstance(data["filters"], list)
    assert len(data["filters"]) > 0


# ── Health Check ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_monitor_health(client):
    resp = await client.get("/api/gateway/monitor/health")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["gateway"] == "healthy"
    assert "components" in data
