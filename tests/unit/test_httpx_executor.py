"""Unit tests for Async HTTPX Executor and Scope Guard."""

import pytest
import respx
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor
from httpx import Response

from agentic_pentest.application.interfaces.executor import ScopeViolationError
from agentic_pentest.domain.entities import HTTPMethod, Principal, Role


@pytest.mark.asyncio
@respx.mock
async def test_execute_authorized_request() -> None:
    respx.get("http://localhost:8888/identity/api/auth/v1/health").mock(
        return_value=Response(200, json={"status": "UP"})
    )

    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    req, resp = await executor.execute_request(
        method="GET",
        url="http://localhost:8888/identity/api/auth/v1/health",
    )

    assert req.method == HTTPMethod.GET
    assert resp.status_code == 200
    assert "UP" in resp.body
    assert len(resp.body_sha256) == 64


@pytest.mark.asyncio
async def test_scope_guard_blocks_unauthorized_host() -> None:
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    with pytest.raises(ScopeViolationError):
        await executor.execute_request(
            method="GET",
            url="http://malicious-external-target.com/api",
        )


@pytest.mark.asyncio
@respx.mock
async def test_execute_request_with_principal_auth() -> None:
    respx.get("http://localhost:8888/api/user").mock(
        return_value=Response(200, json={"user": "Alice"})
    )

    principal = Principal(
        id="u1",
        name="Alice",
        role=Role.USER,
        jwt_token="mock_jwt_token_alice",
        session_headers={"X-Custom-Header": "CustomVal"},
    )

    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    req, resp = await executor.execute_request(
        method="GET",
        url="http://localhost:8888/api/user",
        principal=principal,
    )

    assert req.headers["Authorization"] == "Bearer mock_jwt_token_alice"
    assert req.headers["X-Custom-Header"] == "CustomVal"
