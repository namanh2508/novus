"""Unit tests for FastMCPServer JSON-RPC 2.0 protocol."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
)
from agentic_pentest.infrastructure.mcp.fastmcp_server import FastMCPServer


class DummyMockExecutor(IHTTPExecutor):
    async def execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Principal | None = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        req_obs = HTTPRequestObservation(
            method=HTTPMethod[method.upper()]
            if method.upper() in HTTPMethod.__members__
            else HTTPMethod.GET,
            url=url,
            headers=headers or {},
            body=body,
        )
        resp_obs = HTTPResponseObservation(
            status_code=200,
            headers={"content-type": "application/json"},
            body='{"status": "ok"}',
            latency_ms=5,
            body_sha256="dummy_sha",
        )
        return req_obs, resp_obs


@pytest.mark.asyncio
async def test_mcp_initialize() -> None:
    server = FastMCPServer(PentestToolRegistry(DummyMockExecutor()))

    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "agentic-pentest-mcp"


@pytest.mark.asyncio
async def test_mcp_tools_list() -> None:
    server = FastMCPServer(PentestToolRegistry(DummyMockExecutor()))

    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert "tools" in resp["result"]
    tools = resp["result"]["tools"]
    assert len(tools) >= 6
    names = [t["name"] for t in tools]
    assert "audit_security_headers" in names


@pytest.mark.asyncio
async def test_mcp_tools_call() -> None:
    server = FastMCPServer(PentestToolRegistry(DummyMockExecutor()))

    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "audit_security_headers",
            "arguments": {"target_url": "http://localhost:8888"},
        },
    }
    resp = await server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 3
    assert "result" in resp
    assert "content" in resp["result"]
    assert len(resp["result"]["content"]) > 0
