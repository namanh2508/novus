"""Unit tests for Zero-Dependency PoC Generator."""

from datetime import UTC, datetime

from agentic_pentest.application.use_cases.generate_poc import PoCGenerator
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


def test_generate_standalone_poc_script() -> None:
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
        body='{"vehicle_id": "v123", "lat": 10.1}',
        latency_ms=30,
        body_sha256="sha256",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    finding = Finding(
        id="FINDING-CRAPI-01",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA in crAPI vehicle location",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v123/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=bob,
        triplet=triplet,
        verification_proof="Cross-principal access succeeded with invariant violation INV_OBJECT_ISOLATION",
        created_at=now,
    )

    generator = PoCGenerator()
    script = generator.generate_python_poc(finding)

    assert "import requests" in script or "import urllib.request" in script
    assert "token_bob" in script
    assert "http://localhost:8888/identity/api/v2/vehicle/v123/location" in script
    assert "Zero-Dependency PoC" in script
