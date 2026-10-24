"""Unit tests for AutonomousAttackOrchestrator on generic web targets."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from agentic_pentest.application.orchestration.autonomous_orchestrator import (
    AutonomousAttackOrchestrator,
    TargetFingerprint,
    TargetProfile,
)
from agentic_pentest.application.orchestration.dynamic_auth import (
    AuthMechanism,
    AuthProvisionResult,
)
from agentic_pentest.application.orchestration.dynamic_harvester import (
    HarvestedEndpoint,
    HarvestResult,
)
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
)
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor


@pytest.mark.asyncio
async def test_synthesize_and_execute_plan_generic_web_target() -> None:
    executor = HTTPXExecutor(allowed_hosts=["generic.app"])
    registry = PentestToolRegistry(executor)

    now = datetime.now(UTC)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://generic.app",
        headers={},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Server": "nginx", "Content-Type": "text/html"},
        body="<html><body><h1>Test</h1></body></html>",
        latency_ms=10,
        body_sha256="abc",
        timestamp=now,
    )
    executor.execute_request = AsyncMock(return_value=(req, resp))  # type: ignore[method-assign]

    # Mock dynamic_auth execution
    mock_auth_tool = AsyncMock()
    mock_auth_tool.metadata.name = "dynamic_auth"
    alice = Principal(id="alice", name="Alice", role=Role.USER, jwt_token="token_alice")
    bob = Principal(id="bob", name="Bob", role=Role.USER, jwt_token="token_bob")
    mock_auth_tool.execute.return_value = AuthProvisionResult(
        success=True,
        mechanism=AuthMechanism.JWT_BEARER,
        principal_alice=alice,
        principal_bob=bob,
        details="Provisioned dual tenants via auto-registration",
    )
    registry.register_tool(mock_auth_tool)

    # Mock dynamic_harvester execution
    mock_harvester_tool = AsyncMock()
    mock_harvester_tool.metadata.name = "dynamic_harvester"
    mock_harvester_tool.execute.return_value = HarvestResult(
        endpoints=[
            HarvestedEndpoint(
                path="/api/v1/user/101",
                full_url="http://generic.app/api/v1/user/101",
                method="GET",
            )
        ],
        harvested_identifiers={"integer_id": {"101"}},
        details="Discovered 1 endpoint and 1 object ID",
    )
    registry.register_tool(mock_harvester_tool)

    # Mock remaining tools for smooth execution
    for tool in registry.list_tools():
        if tool.metadata.name not in {"dynamic_auth", "dynamic_harvester"}:
            mock_t = AsyncMock()
            mock_t.metadata = tool.metadata
            mock_t.execute.return_value = "OK"
            registry.register_tool(mock_t)

    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = AutonomousAttackOrchestrator(
            tool_registry=registry,
            executor=executor,
            output_dir=tmpdir,
        )

        fp = TargetFingerprint(
            profile=TargetProfile.GENERIC_WEB_API,
            detected_technologies=["Generic Web API"],
        )

        plan = await orchestrator.synthesize_attack_chain_plan(
            target_str="http://generic.app",
            fingerprint=fp,
        )

        assert any(n.tool_name == "dynamic_auth" for n in plan.nodes)
        assert any(n.tool_name == "dynamic_harvester" for n in plan.nodes)

        report = await orchestrator.execute_attack_chain(plan)
        assert report.completed_steps > 0
        assert report.json_path.exists()
