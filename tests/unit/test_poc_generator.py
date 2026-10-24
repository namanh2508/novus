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


def test_generate_multi_language_pocs() -> None:
    now = datetime.now(UTC)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER, jwt_token="token_bob")
    obj = TargetObject(
        id="obj_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )
    req = HTTPRequestObservation(
        method=HTTPMethod.POST,
        url="http://localhost:8888/identity/api/v2/vehicle/v123/reset",
        headers={"Authorization": "Bearer token_bob", "Content-Type": "application/json"},
        body='{"pin": "1234"}',
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"status": "ok"}',
        latency_ms=25,
        body_sha256="sha256",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    finding = Finding(
        id="FINDING-CRAPI-02",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA test",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v123/reset",
        method=HTTPMethod.POST,
        target_object=obj,
        attacker_principal=bob,
        triplet=triplet,
        verification_proof="BOLA confirmed",
        created_at=now,
    )
    generator = PoCGenerator()

    # 1. cURL PoC
    curl_sh = generator.generate_curl_poc(finding)
    assert "curl -i -s -X POST" in curl_sh
    assert "Authorization: Bearer token_bob" in curl_sh
    assert '--data \'{"pin": "1234"}\'' in curl_sh

    # 2. Go PoC
    go_code = generator.generate_go_poc(finding)
    assert "package main" in go_code
    assert "http.NewRequest" in go_code
    assert "Authorization" in go_code
    assert "net/http" in go_code

    # 3. Node.js PoC
    node_code = generator.generate_node_poc(finding)
    assert "async function testVulnerability()" in node_code
    assert "fetch(targetUrl," in node_code
    assert "token_bob" in node_code

    # 4. generate_all_pocs
    all_pocs = generator.generate_all_pocs(finding)
    assert set(all_pocs.keys()) == {"python", "urllib", "curl", "go", "node", "raw_http"}
    assert "requests.request" in all_pocs["python"]
    assert "urllib.request" in all_pocs["urllib"]
    assert "POST /identity/api/v2/vehicle/v123/reset HTTP/1.1" in all_pocs["raw_http"]

    # 5. Pure stdlib urllib PoC direct
    urllib_code = generator.generate_urllib_poc(finding)
    assert "import urllib.request" in urllib_code
    assert "token_bob" in urllib_code
    assert "test_vulnerability()" in urllib_code
