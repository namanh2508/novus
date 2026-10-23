"""Unit tests for ObsidianVaultExporter."""

from __future__ import annotations

import tempfile
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
from agentic_pentest.infrastructure.reporting.obsidian_vault_exporter import (
    ObsidianVaultExporter,
)


def _sample_finding() -> Finding:
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/123/location",
        headers={},
        body=None,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body='{"carId": "123", "lat": 10.5}',
        latency_ms=10,
        body_sha256="abc",
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    return Finding(
        id="VULN-BOLA-9988",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA on Vehicle Location Telemetry",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/123/location",
        method=HTTPMethod.GET,
        target_object=TargetObject(
            id="car_1", type_name="vehicle", owner_principal_id="user_alice", value="123"
        ),
        attacker_principal=Principal(
            id="user_bob", name="Bob", role=Role.USER, jwt_token="token_bob"
        ),
        triplet=triplet,
        verification_proof="Cross-principal request succeeded with HTTP 200",
        created_at=datetime.now(UTC),
    )


def test_obsidian_vault_exporter() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = ObsidianVaultExporter(output_dir=tmpdir)
        finding = _sample_finding()

        vault_path = exporter.export(
            target_url="http://localhost:8888",
            findings=[finding],
            telemetry_logs=["Test log 1", "Evidence hash verified"],
        )

        assert vault_path.exists()

        # Check index note
        index_file = vault_path / "00_Index.md"
        assert index_file.exists()
        index_text = index_file.read_text(encoding="utf-8")
        assert "Penetration Testing Engagement Index" in index_text
        assert "VULN-BOLA-9988" in index_text
        assert "Zero False-Positive Guarantee" in index_text

        # Check findings note
        finding_file = vault_path / "findings" / "VULN-BOLA-9988.md"
        assert finding_file.exists()
        finding_text = finding_file.read_text(encoding="utf-8")
        assert "id: VULN-BOLA-9988" in finding_text
        assert "sequenceDiagram" in finding_text
        assert "reproduce_vuln-bola-9988.py" in finding_text
        assert "Explicit Object Ownership Invariant" in finding_text

        # Check attack surface note
        surface_file = vault_path / "01_Target_Attack_Surface.md"
        assert surface_file.exists()

        # Check telemetry note
        telemetry_file = vault_path / "02_Audit_Telemetry.md"
        assert telemetry_file.exists()
        assert "Evidence hash verified" in telemetry_file.read_text(encoding="utf-8")
