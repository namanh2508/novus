"""Unit tests for InterceptionProxyDashboard."""

from __future__ import annotations

import pytest
from aiohttp.test_utils import TestClient, TestServer

from agentic_pentest.infrastructure.proxy.interception_dashboard import (
    InterceptionProxyDashboard,
)


@pytest.mark.asyncio
async def test_interception_dashboard_endpoints() -> None:
    """Test dashboard status, flows API, and toggle intercept."""
    dashboard = InterceptionProxyDashboard(host="127.0.0.1", port=8099)
    client = TestClient(TestServer(dashboard._app))
    await client.start_server()

    try:
        # 1. Check HTML dashboard
        resp = await client.get("/")
        assert resp.status == 200
        text = await resp.text()
        assert "Agentic Pentest" in text

        # 2. Check API status
        resp = await client.get("/api/status")
        assert resp.status == 200
        data = await resp.json()
        assert data["intercept_enabled"] is False

        # 3. Toggle intercept on
        resp = await client.post("/api/intercept", json={"enabled": True})
        assert resp.status == 200
        data = await resp.json()
        assert data["intercept_enabled"] is True

        # 4. Check flows list
        resp = await client.get("/api/flows")
        assert resp.status == 200
        flows = await resp.json()
        assert isinstance(flows, list)

        # 5. Clear flows
        resp = await client.delete("/api/flows")
        assert resp.status == 200
        data = await resp.json()
        assert data["cleared"] is True
    finally:
        await client.close()
