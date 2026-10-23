"""Unit tests for PentestToolRegistry and MCP tool specifications."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    RiskTier,
    SideEffectClass,
)


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
        resp_headers = {"content-type": "application/json"}
        if "login" in url:
            resp_headers["set-cookie"] = "session=xyz123; Path=/; Secure; HttpOnly; SameSite=Strict"
        resp_obs = HTTPResponseObservation(
            status_code=200,
            headers=resp_headers,
            body='{"status": "ok"}',
            latency_ms=10,
            body_sha256="abc123sha",
        )
        return req_obs, resp_obs


def test_registry_registers_core_suite() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)

    tools = registry.list_tools()
    assert len(tools) >= 6

    tool_names = [t.metadata.name for t in tools]
    assert "audit_security_headers" in tool_names
    assert "audit_cookies" in tool_names
    assert "audit_cors" in tool_names
    assert "audit_login" in tool_names
    assert "audit_race_condition" in tool_names
    assert "audit_graphql" in tool_names
    assert "audit_jwt" in tool_names
    assert "audit_secret_leak" in tool_names
    assert "audit_ai_code" in tool_names
    assert "seed_crapi" in tool_names
    assert "verify_bola" in tool_names
    assert "verify_bfla" in tool_names
    assert "verify_bopla" in tool_names
    assert "mutate_parameter" in tool_names


def test_registry_mcp_specs_compliance() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)

    specs = registry.get_mcp_tools_spec()
    assert len(specs) >= 6

    for spec in specs:
        assert "name" in spec
        assert "description" in spec
        assert "inputSchema" in spec
        assert "metadata" in spec
        assert "sideEffect" in spec["metadata"]
        assert "riskTier" in spec["metadata"]
        assert "idempotent" in spec["metadata"]


def test_tool_risk_tiers_and_side_effects() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)

    headers_tool = registry.get_tool("audit_security_headers")
    assert headers_tool is not None
    assert headers_tool.metadata.risk_tier == RiskTier.T0_SAFE
    assert headers_tool.metadata.side_effect_class == SideEffectClass.READ_ONLY

    bola_tool = registry.get_tool("verify_bola")
    assert bola_tool is not None
    assert bola_tool.metadata.risk_tier == RiskTier.T2_ACTIVE
    assert bola_tool.metadata.side_effect_class == SideEffectClass.READ_ONLY


@pytest.mark.asyncio
async def test_tool_execution_via_registry() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)

    tool = registry.get_tool("audit_security_headers")
    assert tool is not None
    result = await tool.execute(target_url="http://localhost:8888")
    assert result is not None
    assert hasattr(result, "score")
