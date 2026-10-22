"""Unit tests for SARIF 2.1.0 report exporter."""

import json
from datetime import UTC, datetime

from agentic_pentest.application.use_cases.export_sarif import SARIFExporter
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


def test_sarif_export_format() -> None:
    now = datetime.now(UTC)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER)
    obj = TargetObject(
        id="obj_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v123/location",
        headers={},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body="{}",
        latency_ms=10,
        body_sha256="hash",
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
        title="BOLA in crAPI",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v123/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=bob,
        triplet=triplet,
        verification_proof="Cross-principal access succeeded",
        created_at=now,
    )

    exporter = SARIFExporter()
    sarif_str = exporter.export([finding])
    sarif_data = json.loads(sarif_str)

    assert sarif_data["version"] == "2.1.0"
    assert len(sarif_data["runs"]) == 1
    assert len(sarif_data["runs"][0]["results"]) == 1
    assert sarif_data["runs"][0]["results"][0]["ruleId"] == "SEC-BOLA-001"
