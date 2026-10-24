"""Unit tests for SSRF & Cloud Metadata posture auditor (SSRFCapabilityAuditor)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.audit_ssrf import SSRFCapabilityAuditor
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Severity,
    VulnerabilityCategory,
)


class MockExecutor(IHTTPExecutor):
    """Configurable mock executor for simulating SSRF responses."""

    def __init__(self, response_map: dict[str, HTTPResponseObservation] | None = None) -> None:
        self.response_map = response_map or {}
        self.executed_requests: list[dict[str, object]] = []

    async def execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Principal | None = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        now = datetime.now(UTC)
        req = HTTPRequestObservation(
            method=HTTPMethod.POST if method == "POST" else HTTPMethod.GET,
            url=url,
            headers=headers or {},
            body=body,
            timestamp=now,
        )
        self.executed_requests.append({"method": method, "url": url, "body": body})
        payload_key = ""
        if body:
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    payload_key = str(data.get("webhook_url", ""))
            except Exception:
                pass

        resp = self.response_map.get(
            payload_key,
            HTTPResponseObservation(
                status_code=200,
                headers={},
                body='{"status": "ok"}',
                latency_ms=10.0,
                body_sha256="dummy",
                timestamp=now,
            ),
        )
        return req, resp


@pytest.mark.asyncio
async def test_ssrf_auditor_detects_aws_imds() -> None:
    now = datetime.now(UTC)
    aws_resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "text/plain"},
        body="ami-id\ninstance-id\niam/security-credentials",
        latency_ms=15.0,
        body_sha256="dummy_sha",
        timestamp=now,
    )
    executor = MockExecutor(response_map={"http://169.254.169.254/latest/meta-data/": aws_resp})
    auditor = SSRFCapabilityAuditor(executor)

    res = await auditor.audit_endpoint(
        base_url="http://target.local",
        candidate_path="/api/coupon",
        auth_token="jwt_alice",
    )

    assert res.is_vulnerable_ssrf is True
    assert res.is_cloud_metadata_exposed is True
    assert res.exposed_provider == "AWS_IMDSv1"
    assert len(res.findings) == 1
    finding = res.findings[0]
    assert finding.category == VulnerabilityCategory.SSRF_CLOUD_METADATA
    assert finding.severity == Severity.CRITICAL
    assert "Verified SSRF" in finding.verification_proof


@pytest.mark.asyncio
async def test_ssrf_auditor_detects_gcp_metadata() -> None:
    now = datetime.now(UTC)
    gcp_resp = HTTPResponseObservation(
        status_code=200,
        headers={"Metadata-Flavor": "Google"},
        body="10293847561029384",
        latency_ms=12.0,
        body_sha256="dummy_sha",
        timestamp=now,
    )
    executor = MockExecutor(
        response_map={"http://metadata.google.internal/computeMetadata/v1/instance/id": gcp_resp}
    )
    auditor = SSRFCapabilityAuditor(executor)

    res = await auditor.audit_endpoint(
        base_url="http://target.local",
        candidate_path="/api/webhook",
    )

    assert res.is_vulnerable_ssrf is True
    assert res.is_cloud_metadata_exposed is True
    assert res.exposed_provider == "GCP_METADATA"


@pytest.mark.asyncio
async def test_ssrf_auditor_safe_endpoint() -> None:
    # All SSRF probes return safe non-matching response
    executor = MockExecutor()
    auditor = SSRFCapabilityAuditor(executor)

    res = await auditor.audit_endpoint(
        base_url="http://target.local",
        candidate_path="/api/safe",
    )

    assert res.is_vulnerable_ssrf is False
    assert res.is_cloud_metadata_exposed is False
    assert res.exposed_provider is None
    assert len(res.findings) == 0
    assert "SECURE" in res.details
