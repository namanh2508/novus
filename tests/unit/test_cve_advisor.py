"""Unit tests for CVEAdvisoryIntelligence."""

from __future__ import annotations

from agentic_pentest.infrastructure.intelligence.cve_advisor import (
    CVEAdvisoryIntelligence,
)


def test_cve_advisor_matches_werkzeug_banner() -> None:
    advisor = CVEAdvisoryIntelligence()
    results = advisor.lookup_banner("Python/3.10 Werkzeug/2.0.1")

    assert len(results) >= 1
    cve_ids = [r.cve_id for r in results]
    assert "CVE-2022-29361" in cve_ids
    assert results[0].severity == "HIGH"


def test_cve_advisor_matches_nginx_banner() -> None:
    advisor = CVEAdvisoryIntelligence()
    results = advisor.lookup_banner("nginx/1.18.0 (Ubuntu)")

    assert len(results) >= 1
    assert any(r.component == "nginx" for r in results)


def test_cve_advisor_format_markdown_advisory() -> None:
    advisor = CVEAdvisoryIntelligence()
    results = advisor.lookup_banner("Werkzeug/2.0.1")
    md = advisor.format_markdown_advisory(results)

    assert "### 🛡️ Threat Intelligence & CVE Advisories" in md
    assert "CVE-2022-29361" in md
    assert "Upgrade werkzeug to >=" in md
