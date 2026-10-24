from datetime import UTC, datetime

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
from agentic_pentest.domain.safety.threat_matrix import ThreatMatrixRegistry


def test_threat_matrix_registry_resolution() -> None:
    # 1. Test BOLA mapping
    bola_meta = ThreatMatrixRegistry.get_metadata(VulnerabilityCategory.BOLA)
    assert bola_meta.owasp_api_id == "API1:2023"
    assert "Broken Object Level Authorization" in bola_meta.owasp_title
    assert bola_meta.cwe_id == "CWE-639"
    assert bola_meta.mitre_technique_id == "T1078"

    # 2. Test SSRF mapping
    ssrf_meta = ThreatMatrixRegistry.get_metadata(VulnerabilityCategory.SSRF_CLOUD_METADATA)
    assert ssrf_meta.owasp_api_id == "API7:2023"
    assert ssrf_meta.cwe_id == "CWE-918"

    # 3. Test string fallback resolution
    meta_str = ThreatMatrixRegistry.get_metadata("bfla")
    assert meta_str.owasp_api_id == "API5:2023"
    assert meta_str.cwe_id == "CWE-285"


def test_enrich_finding_with_threat_taxonomies() -> None:
    now = datetime.now(UTC)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={},
        body=None,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body='{"lat": 37.77}',
        latency_ms=30,
        body_sha256="hash",
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    finding = Finding(
        id="FIND-TAXONOMY-01",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="Vehicle Location Unauthorized Exposure",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        method=HTTPMethod.GET,
        target_object=TargetObject(
            id="v1", type_name="vehicle", owner_principal_id="alice", value="v1"
        ),
        attacker_principal=Principal(id="bob", name="Bob", role=Role.USER),
        triplet=triplet,
        verification_proof="Cross-principal access succeeded",
        created_at=now,
    )

    enriched = ThreatMatrixRegistry.enrich_finding(finding)
    assert enriched["owasp_api"]["id"] == "API1:2023"
    assert enriched["cwe"]["id"] == "CWE-639"
    assert enriched["mitre_attack"]["id"] == "T1078"
    assert enriched["cvss"]["score"] == 8.5
