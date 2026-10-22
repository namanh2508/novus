"""Unit tests for Go fastprobe subprocess adapter."""

import pytest
import respx
from httpx import Response

from agentic_pentest.application.interfaces.executor import ScopeViolationError
from agentic_pentest.infrastructure.adapters.go_prober import GoFastProbeAdapter


@pytest.mark.asyncio
async def test_go_prober_scope_guard() -> None:
    adapter = GoFastProbeAdapter(allowed_hosts=["localhost:8888"])
    with pytest.raises(ScopeViolationError):
        await adapter.execute_request(method="GET", url="http://unauthorized-domain.com")


@pytest.mark.asyncio
@respx.mock
async def test_go_prober_httpx_fallback() -> None:
    respx.get("http://localhost:8888/identity/api/auth/v1/health").mock(
        return_value=Response(200, json={"status": "OK"})
    )

    # Point to nonexistent binary to trigger fallback
    adapter = GoFastProbeAdapter(
        binary_path="nonexistent_binary.exe",
        fallback_httpx=True,
        allowed_hosts=["localhost:8888"],
    )
    req, resp = await adapter.execute_request(
        method="GET",
        url="http://localhost:8888/identity/api/auth/v1/health",
    )
    assert resp.status_code == 200
    assert "OK" in resp.body
