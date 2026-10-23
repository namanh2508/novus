"""Unit tests for MultiAgentRootOrchestrator delegation pattern."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.multi_agent_orchestrator import (
    MultiAgentRootOrchestrator,
)
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
)


class MockMultiAgentExecutor(IHTTPExecutor):
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
        # Simulate crAPI responses
        if "location" in url:
            # BOLA endpoint
            resp_body = '{"carId": "f89b5f21-7829-45cb-a650-299a61090378", "latitude": 32.7}'
            if principal is None:
                return req_obs, HTTPResponseObservation(
                    status_code=401,
                    headers=resp_headers,
                    body='{"error": "Unauthorized"}',
                    latency_ms=10,
                    body_sha256="anon_401",
                )
            return req_obs, HTTPResponseObservation(
                status_code=200,
                headers=resp_headers,
                body=resp_body,
                latency_ms=12,
                body_sha256="sha_loc_200",
            )

        if "coupon" in url:
            # BFLA endpoint
            return req_obs, HTTPResponseObservation(
                status_code=200,
                headers=resp_headers,
                body='{"status": "Coupon Added in database"}',
                latency_ms=14,
                body_sha256="sha_coupon_200",
            )

        return req_obs, HTTPResponseObservation(
            status_code=200,
            headers=resp_headers,
            body='{"status": "ok"}',
            latency_ms=5,
            body_sha256="sha_ok",
        )


@pytest.mark.asyncio
async def test_multi_agent_orchestrator_delegation() -> None:
    executor = MockMultiAgentExecutor()
    registry = PentestToolRegistry(executor)
    orchestrator = MultiAgentRootOrchestrator(registry)

    findings = await orchestrator.run_mission("http://localhost:8888")

    # Invariants: 4 subagents executed
    assert len(orchestrator.reports) == 4
    subagent_names = [r.agent_name for r in orchestrator.reports]
    assert "ReconSubagent" in subagent_names
    assert "IdentitySubagent" in subagent_names
    assert "BolaSubagent" in subagent_names
    assert "BflaSubagent" in subagent_names

    # All subagents completed successfully
    assert all(r.status == "COMPLETED" for r in orchestrator.reports)

    # Findings discovered across scopes
    assert len(findings) >= 2
    categories = [f.category.value for f in findings]
    assert "BOLA" in categories
    assert "BFLA" in categories
