"""Unit tests for OSINT attack surface and cloud asset leakage scanner."""

from __future__ import annotations

import pytest

from agentic_pentest.application.use_cases.tool_registry import OSINTAttackSurfaceTool
from agentic_pentest.infrastructure.discovery.osint_scanner import OSINTAttackSurfaceScanner


def test_extract_apex_domain() -> None:
    scanner = OSINTAttackSurfaceScanner()
    assert scanner.extract_apex_domain("http://api.staging.target.com:8888/v1") == "target.com"
    assert scanner.extract_apex_domain("https://sub.portal.domain.org") == "domain.org"
    assert scanner.extract_apex_domain("localhost") == "localhost"


def test_scan_cloud_assets_leakage() -> None:
    scanner = OSINTAttackSurfaceScanner()
    html_sample = """
    <html>
      <script src="https://assets-corp.s3.amazonaws.com/bundle.js"></script>
      <img src="https://storage.googleapis.com/public-photos-bucket/avatar.png" />
      <a href="https://corpstorage.blob.core.windows.net/invoices/inv.pdf">Invoice</a>
      <script>var fb = "https://corp-auth.firebaseio.com";</script>
    </html>
    """
    findings = scanner.scan_cloud_assets(html_sample, "https://target.com/app")
    assert len(findings) == 4

    providers = {f.provider for f in findings}
    assert "AWS_S3" in providers
    assert "GCP_GCS" in providers
    assert "AZURE_BLOB" in providers
    assert "FIREBASE" in providers

    s3_finding = next(f for f in findings if f.provider == "AWS_S3")
    assert s3_finding.resource_identifier == "assets-corp"
    assert s3_finding.risk_level == "HIGH"


def test_check_subdomain_takeover() -> None:
    scanner = OSINTAttackSurfaceScanner()
    # Dangling GitHub Pages
    is_takeover, svc = scanner.check_subdomain_takeover("blog.target.com", "targetblog.github.io")
    assert is_takeover is True
    assert svc == "GitHub Pages Dangling CNAME"

    # Dangling S3 bucket
    is_takeover, svc = scanner.check_subdomain_takeover(
        "static.target.com", "static-bucket.s3.amazonaws.com"
    )
    assert is_takeover is True
    assert svc == "AWS S3 Bucket Takeover"

    # Safe CNAME
    is_takeover, svc = scanner.check_subdomain_takeover("api.target.com", "elb-12345.awsglobal.com")
    assert is_takeover is False
    assert svc is None


@pytest.mark.asyncio
async def test_osint_attack_surface_tool() -> None:
    tool = OSINTAttackSurfaceTool()
    sample_content = (
        "Leaked cloud database backup: https://storage.googleapis.com/secret-backup-crapi/crapi.sql"
    )
    result = await tool.execute(
        target_url="http://127.0.0.1:8888",
        page_content=sample_content,
    )
    assert "target_domain" in result
    assert result["total_subdomains"] >= 1
    assert len(result["cloud_assets"]) == 1
    assert result["cloud_assets"][0]["provider"] == "GCP_GCS"
    assert result["cloud_assets"][0]["resource"] == "secret-backup-crapi"
