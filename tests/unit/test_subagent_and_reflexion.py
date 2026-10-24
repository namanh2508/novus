"""Unit tests for SubagentDelegator and ReflexionAntiLoopEngine."""

from datetime import UTC, datetime

import pytest

from agentic_pentest.application.orchestration.anti_loop_reflexion import (
    LoopSeverity,
    ReflexionState,
)
from agentic_pentest.application.orchestration.subagent_delegator import (
    BudgetExceededError,
    SubagentDelegator,
    SubagentRole,
)
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


def _make_dummy_finding(finding_id: str = "FIND-01") -> Finding:
    now = datetime.now(UTC)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER, jwt_token="token_bob")
    obj = TargetObject(
        id="obj_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v123/location",
        headers={"Authorization": "Bearer token_bob"},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"vehicle_id": "v123"}',
        latency_ms=25,
        body_sha256="hash123",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    return Finding(
        id=finding_id,
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA on Vehicle",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v123/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=bob,
        triplet=triplet,
        verification_proof="Cross-principal access succeeded",
        created_at=now,
    )


def test_reflexion_detects_consecutive_failures() -> None:
    state = ReflexionState(max_consecutive_failures=3)
    # Fail 1
    sev1 = state.record_trace("VERIFY_BOLA", "/api/v2/user", 403, "Forbidden", success=False)
    assert sev1 == LoopSeverity.NONE

    # Fail 2 -> Warning
    sev2 = state.record_trace("VERIFY_BOLA", "/api/v2/user", 403, "Forbidden", success=False)
    assert sev2 == LoopSeverity.WARNING

    # Fail 3 -> STUCK (Trigger pivot)
    sev3 = state.record_trace("VERIFY_BOLA", "/api/v2/user", 403, "Forbidden", success=False)
    assert sev3 == LoopSeverity.STUCK
    assert len(state.backtrack_reasons) == 1

    pivot = state.suggest_pivot("VERIFY_BOLA", "/api/v2/user")
    assert "BFLA" in pivot


def test_reflexion_detects_ping_pong_loop() -> None:
    state = ReflexionState()
    # A -> B -> A -> B loop pattern
    state.record_trace("GET_TOKEN", "/auth/login", 200, "ok", success=False)
    state.record_trace("GET_VEHICLE", "/vehicle/1", 401, "unauth", success=False)
    state.record_trace("GET_TOKEN", "/auth/login", 200, "ok", success=False)
    sev = state.record_trace("GET_VEHICLE", "/vehicle/1", 401, "unauth", success=False)

    assert sev == LoopSeverity.STUCK
    assert any("ping-pong" in r for r in state.backtrack_reasons)


def test_subagent_delegator_budget_exceeded() -> None:
    delegator = SubagentDelegator()
    budget = delegator.create_subagent_budget(SubagentRole.RECON)
    assert budget.max_turns == 4

    # Consume turns up to limit
    budget.consume_turn(100)
    budget.consume_turn(100)
    budget.consume_turn(100)
    budget.consume_turn(100)

    # 5th turn should raise BudgetExceededError
    with pytest.raises(BudgetExceededError):
        budget.consume_turn(100)


def test_subagent_delegator_report_consolidation() -> None:
    delegator = SubagentDelegator()
    f1 = _make_dummy_finding("FIND-01")
    rep = delegator.record_subagent_result(
        role=SubagentRole.AUTH_AUDIT,
        objective="Audit vehicle endpoints",
        turns=2,
        findings=[f1],
        summary="Found 1 BOLA vulnerability",
    )
    assert rep.role == SubagentRole.AUTH_AUDIT
    consolidated = delegator.get_consolidated_findings()
    assert len(consolidated) == 1
    assert consolidated[0].id == "FIND-01"
