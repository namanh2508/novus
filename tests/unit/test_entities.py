"""Unit tests for domain entities and immutability invariants."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from agentic_pentest.domain.entities import (
    DifferentialTriplet,
    Finding,
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    OracleVerdict,
    Principal,
    Role,
    Severity,
    TargetObject,
    VulnerabilityCategory,
)


def test_principal_immutability() -> None:
    principal = Principal(
        id="user_alice_01",
        name="Alice",
        role=Role.USER,
        jwt_token="mock_jwt_token",
    )
    assert principal.name == "Alice"
    assert principal.role == Role.USER

    # Ensure immutability (frozen dataclass/model)
    with pytest.raises((FrozenInstanceError, TypeError)):
        principal.name = "Alice_Hacked"  # type: ignore[misc]


def test_differential_triplet_construction() -> None:
    now = datetime.now(UTC)
    req_legit = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={"Authorization": "Bearer token_alice"},
        body=None,
        timestamp=now,
    )
    resp_legit = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"lat": 37.77, "long": -122.41}',
        latency_ms=45,
        body_sha256="hash_legit",
        timestamp=now,
    )

    req_cross = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={"Authorization": "Bearer token_bob"},
        body=None,
        timestamp=now,
    )
    resp_cross = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"lat": 37.77, "long": -122.41}',
        latency_ms=42,
        body_sha256="hash_cross",
        timestamp=now,
    )

    req_anon = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={},
        body=None,
        timestamp=now,
    )
    resp_anon = HTTPResponseObservation(
        status_code=401,
        headers={"Content-Type": "application/json"},
        body='{"error": "unauthorized"}',
        latency_ms=10,
        body_sha256="hash_anon",
        timestamp=now,
    )

    triplet = DifferentialTriplet(
        baseline_legitimate=(req_legit, resp_legit),
        cross_principal_test=(req_cross, resp_cross),
        unauthenticated_control=(req_anon, resp_anon),
    )

    assert triplet.baseline_legitimate[1].status_code == 200
    assert triplet.cross_principal_test[1].status_code == 200
    assert triplet.unauthenticated_control[1].status_code == 401


def test_finding_creation() -> None:
    now = datetime.now(UTC)
    obj = TargetObject(
        id="v-1",
        type_name="vehicle_id",
        owner_principal_id="user_alice_01",
        value="uuid-car-123",
    )
    attacker = Principal(id="user_bob_02", name="Bob", role=Role.USER)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/api/test",
        headers={},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body="{}",
        latency_ms=10,
        body_sha256="sha",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    finding = Finding(
        id="FINDING-001",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA in vehicle location",
        endpoint_url="http://localhost:8888/api/test",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=attacker,
        triplet=triplet,
        verification_proof="Identical response body accessed cross-principal",
        created_at=now,
    )
    assert finding.category == VulnerabilityCategory.BOLA
    assert finding.severity == Severity.HIGH


def test_oracle_verdict_confidence_range() -> None:
    verdict = OracleVerdict(
        is_vulnerable=True,
        confidence_score=1.0,
        rationale="Cross-principal access succeeded with identical response body.",
        violated_invariants=["INV_OBJECT_ISOLATION"],
    )
    assert verdict.is_vulnerable is True
    assert 0.0 <= verdict.confidence_score <= 1.0
    assert len(verdict.violated_invariants) == 1
