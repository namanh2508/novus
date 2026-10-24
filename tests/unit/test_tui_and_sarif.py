"""Unit tests for Phase 7: Terminal Canvas TUI and SARIF 2.1.0 Exporter with CVSS v3.1."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from agentic_pentest.domain.entities import (
    Finding,
    HTTPMethod,
    Principal,
    Role,
    Severity,
    TargetObject,
    VulnerabilityCategory,
)
from agentic_pentest.presentation.sarif_exporter import SARIFExporter
from agentic_pentest.presentation.tui.terminal_canvas import TerminalCanvas


def test_terminal_canvas_rendering() -> None:
    canvas = TerminalCanvas()
    canvas.update_metrics(
        target_url="http://target.local:8888",
        agent_state="EXECUTING",
        proxy_status="socks5://127.0.0.1:9050",
        total_requests=42,
        findings_count={"HIGH": 2, "CRITICAL": 1},
        latest_traffic_preview="GET /api/v2/orders HTTP/1.1 -> 200 OK",
    )

    canvas.add_or_update_endpoint("/api/v2/orders", "GET", "EXECUTING", "Testing IDOR")
    canvas.add_or_update_endpoint("/api/v2/vehicle/location", "GET", "VERIFIED", "BOLA confirmed")
    canvas.add_or_update_endpoint("/api/v2/auth/login", "POST", "CLEAN", "Rate limit active")

    rendered = canvas.render_to_string()
    assert "AGENTIC PENTEST OS" in rendered
    assert "http://target.local:8888" in rendered
    assert "socks5://127.0.0.1:9050" in rendered
    assert "/api/v2/orders" in rendered
    assert "VERIFIED" in rendered
    assert "CLEAN" in rendered


def test_sarif_exporter_with_cvss_v31() -> None:
    now = datetime.now(UTC)
    alice = Principal(id="u1", name="Alice", role=Role.USER)
    obj = TargetObject(id="o1", type_name="vehicle", owner_principal_id="u2", value="v100")

    finding_bola = Finding(
        id="FINDING-BOLA-01",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA in vehicle tracking",
        endpoint_url="http://target.local/api/v2/vehicle/v100/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=alice,
        triplet=None,
        verification_proof="Cross-tenant access succeeded",
        created_at=now,
    )

    finding_bfla = Finding(
        id="FINDING-BFLA-01",
        category=VulnerabilityCategory.BFLA,
        severity=Severity.CRITICAL,
        title="BFLA in admin reset",
        endpoint_url="http://target.local/api/v2/admin/reset",
        method=HTTPMethod.POST,
        target_object=obj,
        attacker_principal=alice,
        triplet=None,
        verification_proof="User invoked admin function",
        created_at=now,
    )

    exporter = SARIFExporter()
    sarif_str = exporter.export([finding_bola, finding_bfla])

    sarif_json = json.loads(sarif_str)
    assert sarif_json["version"] == "2.1.0"
    assert sarif_json["$schema"] == SARIFExporter.SCHEMA_URI

    runs = sarif_json["runs"]
    assert len(runs) == 1
    results = runs[0]["results"]
    assert len(results) == 2

    # Check BOLA CVSS
    bola_props = results[0]["properties"]
    assert "CVSS:3.1" in bola_props["cvssV3_vector"]
    assert bola_props["cvssV3_baseScore"] == 8.1
    assert bola_props["security-severity"] == "8.1"

    # Check BFLA CVSS
    bfla_props = results[1]["properties"]
    assert "CVSS:3.1" in bfla_props["cvssV3_vector"]
    assert bfla_props["cvssV3_baseScore"] == 8.8
