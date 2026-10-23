"""Unit tests for BFLAVerifier (Broken Function Level Authorization)."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.verify_bfla import BFLAVerifier
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
    VulnerabilityCategory,
)


class MockPrivilegedExecutor(IHTTPExecutor):
    def __init__(self, allow_privileged: bool = True) -> None:
        self.allow_privileged = allow_privileged

    async def execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Principal | None = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        req_obs = HTTPRequestObservation(
            method=HTTPMethod[method.upper()]
            if method.upper() in HTTPMethod.__members__
            else HTTPMethod.GET,
            url=url,
            headers=headers or {},
            body=body,
        )

        # If unauthenticated -> 401
        if principal is None:
            resp_obs = HTTPResponseObservation(
                status_code=401,
                headers={"content-type": "application/json"},
                body='{"error": "Unauthorized"}',
                latency_ms=10,
                body_sha256="anon_401",
            )
            return req_obs, resp_obs

        # If caller is regular user:
        if self.allow_privileged:
            # Vulnerable application returns 200 to regular user
            resp_obs = HTTPResponseObservation(
                status_code=200,
                headers={"content-type": "application/json"},
                body='{"status": "Coupon created in database"}',
                latency_ms=15,
                body_sha256="vuln_200",
            )
        else:
            # Secure application rejects regular user with 403 Forbidden
            resp_obs = HTTPResponseObservation(
                status_code=403,
                headers={"content-type": "application/json"},
                body='{"error": "Forbidden: Requires ADMIN role"}',
                latency_ms=12,
                body_sha256="secure_403",
            )

        return req_obs, resp_obs


@pytest.mark.asyncio
async def test_bfla_verifier_detects_vulnerability_on_unauthorized_success() -> None:
    executor = MockPrivilegedExecutor(allow_privileged=True)
    verifier = BFLAVerifier(executor)

    caller = Principal(id="user_bob", name="Bob", role=Role.USER, jwt_token="bob_token")
    finding = await verifier.verify_bfla(
        endpoint_url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        method=HTTPMethod.POST,
        unprivileged_caller=caller,
        privileged_role_required=Role.ADMIN,
        payload={"coupon_code": "FORGED", "amount": "100"},
    )

    assert finding is not None
    assert finding.category == VulnerabilityCategory.BFLA
    assert "BFLA INVARIANT VIOLATION CONFIRMED" in finding.verification_proof
    assert finding.attacker_principal.name == "Bob"


@pytest.mark.asyncio
async def test_bfla_verifier_returns_none_when_server_properly_enforces_403() -> None:
    executor = MockPrivilegedExecutor(allow_privileged=False)
    verifier = BFLAVerifier(executor)

    caller = Principal(id="user_bob", name="Bob", role=Role.USER, jwt_token="bob_token")
    finding = await verifier.verify_bfla(
        endpoint_url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        method=HTTPMethod.POST,
        unprivileged_caller=caller,
        privileged_role_required=Role.ADMIN,
    )

    assert finding is None
