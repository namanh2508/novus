"""Unit tests for AutonomousAttackOrchestrator and AttackChainPlan."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from agentic_pentest.application.orchestration.autonomous_orchestrator import (
    AutonomousAttackOrchestrator,
    TargetInfo,
)
from agentic_pentest.application.use_cases.tool_registry import PentestToolRegistry
from agentic_pentest.domain.entities import (
    DifferentialTriplet,
    Finding,
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
    Severity,
    TargetObject,
    VulnerabilityCategory,
)
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor
from agentic_pentest.presentation.chat import InteractiveChatSession


def test_target_info_parsing_variations() -> None:
    # 1. Full URL with port
    t1 = TargetInfo.parse("http://127.0.0.1:8888")
    assert t1.scheme == "http"
    assert t1.host == "127.0.0.1"
    assert t1.port == 8888
    assert t1.base_url == "http://127.0.0.1:8888"

    # 2. Host with port and no scheme
    t2 = TargetInfo.parse("192.168.1.50:8000")
    assert t2.scheme == "http"
    assert t2.host == "192.168.1.50"
    assert t2.port == 8000
    assert t2.base_url == "http://192.168.1.50:8000"

    # 3. Target with --port flag
    t3 = TargetInfo.parse("10.0.0.1 --port 9000")
    assert t3.host == "10.0.0.1"
    assert t3.port == 9000
    assert t3.base_url == "http://10.0.0.1:9000"

    # 4. HTTPS default port
    t4 = TargetInfo.parse("https://api.example.com")
    assert t4.scheme == "https"
    assert t4.port == 443
    assert t4.base_url == "https://api.example.com"


@pytest.mark.asyncio
async def test_synthesize_attack_chain_plan(tmp_path: Path) -> None:
    executor = HTTPXExecutor()
    registry = PentestToolRegistry(executor)
    orchestrator = AutonomousAttackOrchestrator(
        tool_registry=registry,
        executor=executor,
        output_dir=str(tmp_path / "attack_chains"),
    )

    plan = await orchestrator.synthesize_attack_chain_plan(
        target_str="http://127.0.0.1:8888",
        user_objective="Verify crAPI BOLA and Security Headers",
    )

    assert plan.target.port == 8888
    assert len(plan.nodes) >= 6
    assert plan.json_path.exists()
    assert plan.md_path.exists()
    assert len(plan.strategic_assessment) > 0

    plan_dict = plan.to_dict()
    assert plan_dict["chain_id"] == plan.chain_id
    assert plan_dict["total_nodes"] == len(plan.nodes)
    assert "strategic_assessment" in plan_dict

    md_text = plan.render_markdown()
    assert "# Attack Chain Plan" in md_text
    assert "STEP-01" in md_text
    assert "Autonomous Supervisor Strategic Assessment" in md_text


def test_target_tcp_reachability_and_fast_fail() -> None:
    # 1. Unreachable port (e.g. localhost on an unlikely closed port)
    target_dead = TargetInfo.parse("127.0.0.1:59999")
    is_reachable, reason = target_dead.check_tcp_reachability(timeout_seconds=0.3)
    assert not is_reachable
    assert "Connection refused" in reason or "timed out" in reason or "error" in reason.lower()


@pytest.mark.asyncio
async def test_execute_attack_chain(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    executor = HTTPXExecutor()
    registry = PentestToolRegistry(executor)

    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://127.0.0.1:8888/identity/api/v2/vehicle/v1/location",
        headers={"Authorization": "Bearer token_bob"},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"lat": 12.34}',
        latency_ms=25,
        body_sha256="sha256",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )

    # Mock tool executions to test harness lifecycle without live network
    for tool in registry.list_tools():
        if tool.metadata.name == "verify_bola":
            mock_finding = Finding(
                id="TEST-BOLA-01",
                category=VulnerabilityCategory.BOLA,
                severity=Severity.HIGH,
                title="BOLA on Vehicle Location",
                endpoint_url="http://127.0.0.1:8888/identity/api/v2/vehicle/v1/location",
                method=HTTPMethod.GET,
                target_object=TargetObject(
                    id="obj_1", type_name="vehicle", owner_principal_id="alice", value="v1"
                ),
                attacker_principal=Principal(
                    id="bob", name="Bob", role=Role.USER, jwt_token="token_bob"
                ),
                triplet=triplet,
                verification_proof="Differential response invariant violated.",
                created_at=now,
            )
            tool.execute = AsyncMock(return_value=mock_finding)  # type: ignore[method-assign]
        else:
            tool.execute = AsyncMock(return_value={"status": "ok"})  # type: ignore[method-assign]

    orchestrator = AutonomousAttackOrchestrator(
        tool_registry=registry,
        executor=executor,
        output_dir=str(tmp_path / "attack_chains"),
    )

    plan = await orchestrator.synthesize_attack_chain_plan(
        target_str="http://127.0.0.1:8888",
    )

    report = await orchestrator.execute_attack_chain(plan)

    assert report.total_steps == len(plan.nodes)
    assert report.completed_steps == len(plan.nodes)
    assert len(report.findings) >= 1
    assert any(f.id == "TEST-BOLA-01" for f in report.findings)
    assert len(report.poc_files) >= 1
    assert any("reproduce_test_bola_01.py" in str(p).lower() for p in report.poc_files)

    # Verify plan file on disk was updated with observations
    updated_text = plan.json_path.read_text(encoding="utf-8")
    assert "TEST-BOLA-01" in updated_text


@pytest.mark.asyncio
async def test_chat_run_autonomous_mission(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")
    # Redirect output directory to tmp_path
    session.autonomous_orchestrator.output_dir = tmp_path

    # Mock reachability check to simulate open port
    def _mock_reachability(self: TargetInfo, timeout_seconds: float = 1.5) -> tuple[bool, str]:
        return True, "Port open"

    monkeypatch.setattr(TargetInfo, "check_tcp_reachability", _mock_reachability)

    # Mock tool calls for fast execution
    for tool in session.tool_registry.list_tools():
        tool.execute = AsyncMock(return_value={"status": "ok"})  # type: ignore[method-assign]

    report = await session.run_autonomous_mission(
        target_input="http://127.0.0.1:8888",
        objective="Automated Test",
    )

    assert report is not None
    assert report.completed_steps == len(report.findings) + (
        report.total_steps - len(report.findings)
    )
    assert session.target_url == "http://127.0.0.1:8888"


@pytest.mark.asyncio
async def test_chat_run_autonomous_mission_unreachable_fast_fail() -> None:
    session = InteractiveChatSession()
    # Unreachable target returns None immediately without running tools
    report = await session.run_autonomous_mission(
        target_input="192.168.1.50:59999",
        objective="Fast fail test",
    )
    assert report is None
