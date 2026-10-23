"""Unit tests for RemediationPatchGenerator."""

from __future__ import annotations

from datetime import UTC, datetime

from agentic_pentest.application.use_cases.remediation_diff import RemediationPatchGenerator
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


def _create_dummy_finding(category: VulnerabilityCategory) -> Finding:
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/api/test",
        headers={},
        body=None,
    )
    resp = HTTPResponseObservation(
        status_code=200, headers={}, body='{"status": "ok"}', latency_ms=10, body_sha256="abc"
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    return Finding(
        id="VULN-TEST-1234",
        category=category,
        severity=Severity.HIGH,
        title=f"Test Vulnerability {category.value}",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/123/location",
        method=HTTPMethod.GET,
        target_object=TargetObject(
            id="obj_1", type_name="vehicle", owner_principal_id="user_alice", value="123"
        ),
        attacker_principal=Principal(id="user_bob", name="Bob", role=Role.USER),
        triplet=triplet,
        verification_proof="Proof of invariant breach",
        created_at=datetime.now(UTC),
    )


def test_remediation_diff_bola() -> None:
    finding = _create_dummy_finding(VulnerabilityCategory.BOLA)
    patch = RemediationPatchGenerator.generate_patch(finding)
    assert "--- a/controllers/vehicle_controller.py" in patch
    assert "+++ b/controllers/vehicle_controller.py" in patch
    assert "Explicit Object Ownership Invariant" in patch
    assert "obj.owner_id != request.current_user.id" in patch

    summary = RemediationPatchGenerator.get_remediation_summary(finding)
    assert "Enforce strict authorization checks" in summary


def test_remediation_diff_bfla() -> None:
    finding = _create_dummy_finding(VulnerabilityCategory.BFLA)
    patch = RemediationPatchGenerator.generate_patch(finding)
    assert "@require_role(Role.ADMIN)" in patch
    assert "ADMIN_CAPABILITY" in patch


def test_remediation_diff_bopla() -> None:
    finding = _create_dummy_finding(VulnerabilityCategory.BOPLA)
    patch = RemediationPatchGenerator.generate_patch(finding)
    assert "ALLOWED_MUTATION_KEYS" in patch
    assert "Strict Allowed-Key Whitelist" in patch
