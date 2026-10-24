"""Unit tests for Multi-Agent Consensus Voting Engine."""

from datetime import UTC, datetime

import pytest

from agentic_pentest.application.orchestration.consensus_verifier import (
    ConsensusVerifier,
    VoteDecision,
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


def _build_test_finding(
    category: VulnerabilityCategory = VulnerabilityCategory.BOLA,
    attacker_id: str = "user_bob",
    owner_id: str = "user_alice",
    proof: str = "Oracle verified invariant INV_OBJECT_ISOLATION breached",
) -> Finding:
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={},
        body=None,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body='{"latitude": 37.77}',
        latency_ms=12,
        body_sha256="hash123",
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    return Finding(
        id="FINDING-TEST-001",
        category=category,
        severity=Severity.HIGH,
        title="BOLA on Vehicle Location",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        method=HTTPMethod.GET,
        target_object=TargetObject(
            id="v1", type_name="vehicle", owner_principal_id=owner_id, value="v1"
        ),
        attacker_principal=Principal(id=attacker_id, name="Attacker", role=Role.USER),
        triplet=triplet,
        verification_proof=proof,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_consensus_supermajority_confirm() -> None:
    verifier = ConsensusVerifier(required_threshold=0.66)
    finding = _build_test_finding()

    report = await verifier.evaluate_finding(finding)

    assert report.is_confirmed is True
    assert report.status_verdict == "CONFIRMED"
    assert report.confidence_score >= 0.85
    assert len(report.votes) == 3
    assert all(v.decision == VoteDecision.CONFIRM for v in report.votes)


@pytest.mark.asyncio
async def test_consensus_reject_false_positive_same_owner() -> None:
    # If attacker is actually the legitimate owner -> False positive
    verifier = ConsensusVerifier(required_threshold=0.66)
    finding = _build_test_finding(attacker_id="user_alice", owner_id="user_alice")

    report = await verifier.evaluate_finding(finding)

    # AuthSpecialist should reject
    auth_votes = [v for v in report.votes if v.specialist_name == "AuthSpecialist"]
    assert auth_votes[0].decision == VoteDecision.REJECT
    assert report.is_confirmed is False
