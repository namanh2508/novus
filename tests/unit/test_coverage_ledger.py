from agentic_pentest.domain.coverage_ledger import CoverageLedger, CoverageState
from agentic_pentest.domain.entities import VulnerabilityCategory


def test_coverage_ledger_registration_and_metrics() -> None:
    ledger = CoverageLedger()

    # Register endpoints
    ledger.register_endpoint("GET", "/identity/api/v2/user/profile")
    ledger.register_endpoint("GET", "/identity/api/v2/vehicle/{id}/location")
    ledger.register_endpoint("POST", "/community/api/v2/coupon/new-coupon")

    metrics_initial = ledger.get_metrics()
    assert metrics_initial["total_endpoints"] == 3
    assert metrics_initial["tested_endpoints"] == 0
    assert metrics_initial["coverage_percentage"] == 0.0

    # Record probes
    ledger.record_probe(
        "GET",
        "/identity/api/v2/user/profile",
        VulnerabilityCategory.BOLA,
        CoverageState.VERIFIED_SECURE,
    )
    ledger.record_probe(
        "GET",
        "/identity/api/v2/vehicle/{id}/location",
        VulnerabilityCategory.BOLA,
        CoverageState.VULNERABLE,
    )

    metrics_updated = ledger.get_metrics()
    assert metrics_updated["tested_endpoints"] == 2
    assert metrics_updated["vulnerable_endpoints"] == 1
    assert metrics_updated["coverage_percentage"] == 66.67

    # Markdown export check
    md = ledger.to_markdown_table()
    assert "Attack Surface Coverage Ledger" in md
    assert "🔴 VULNERABLE" in md
    assert "🟢 SECURE" in md

    # Dictionary export check
    data = ledger.to_dict()
    assert len(data["endpoints"]) == 3
