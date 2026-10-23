"""Unit tests for AutonomousPentestLoop, Anti-Loop Adviser, and ReAct cycle."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.agent_loop import AutonomousPentestLoop
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    AgentGoal,
    AgentTurn,
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    LoopState,
    Principal,
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
        resp_obs = HTTPResponseObservation(
            status_code=200,
            headers=resp_headers,
            body='{"status": "ok", "token": "ey123.456.789"}',
            latency_ms=15,
            body_sha256="dummy_sha",
        )
        return req_obs, resp_obs


@pytest.mark.asyncio
async def test_agent_loop_runs_heuristic_turns() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)
    goal = AgentGoal(
        target_url="http://localhost:8888", max_turns=4, permission_mode="auto-approve"
    )

    loop = AutonomousPentestLoop(goal=goal, tool_registry=registry)

    # Step 1: Security headers
    turn1 = await loop.step()
    assert turn1.turn_number == 1
    assert turn1.tool_name == "audit_security_headers"
    assert turn1.is_success is True

    # Step 2: Cookies
    turn2 = await loop.step()
    assert turn2.turn_number == 2
    assert turn2.tool_name == "audit_cookies"

    # Step 3: CORS
    turn3 = await loop.step()
    assert turn3.turn_number == 3
    assert turn3.tool_name == "audit_cors"


@pytest.mark.asyncio
async def test_anti_loop_detector_triggers_alert() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)
    goal = AgentGoal(target_url="http://localhost:8888", max_turns=5)

    loop = AutonomousPentestLoop(goal=goal, tool_registry=registry)

    # Manually append 2 identical turns
    loop.turns.append(
        AgentTurn(
            turn_number=1,
            thought="Probe endpoint",
            tool_name="audit_cors",
            tool_arguments={"target_url": "http://localhost:8888"},
            observation_summary="Safe",
            is_success=True,
        )
    )
    loop.turns.append(
        AgentTurn(
            turn_number=2,
            thought="Probe endpoint again",
            tool_name="audit_cors",
            tool_arguments={"target_url": "http://localhost:8888"},
            observation_summary="Safe",
            is_success=True,
        )
    )

    warning = loop._check_anti_loop()
    assert warning is not None
    assert "ANTI-LOOP ADVISER ALERT: Repeated execution" in warning


@pytest.mark.asyncio
async def test_agent_loop_max_turns_budget_halting() -> None:
    executor = DummyMockExecutor()
    registry = PentestToolRegistry(executor)
    goal = AgentGoal(target_url="http://localhost:8888", max_turns=2)

    loop = AutonomousPentestLoop(goal=goal, tool_registry=registry)

    await loop.step()
    await loop.step()

    # Step 3 should exceed budget
    turn3 = await loop.step()
    assert loop.state == LoopState.COMPLETED
    assert turn3.tool_name == "FINISH"
    assert "budget reached" in turn3.thought.lower()
