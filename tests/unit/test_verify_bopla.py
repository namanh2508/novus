"""Unit tests for BOPLAVerifier (Broken Object Property Level Authorization)."""

from __future__ import annotations

import json

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.verify_bopla import BOPLAVerifier
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
    VulnerabilityCategory,
)


class MockBOPLAExecutor(IHTTPExecutor):
    def __init__(self, vulnerable: bool = True) -> None:
        self.vulnerable = vulnerable

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
            else HTTPMethod.POST,
            url=url,
            headers=headers or {},
            body=body,
        )

        resp_headers = {"content-type": "application/json"}
        parsed_body = json.loads(body) if body else {}

        if self.vulnerable:
            # Server naively accepts and reflects injected privileged property
            resp_obs = HTTPResponseObservation(
                status_code=200,
                headers=resp_headers,
                body=json.dumps(parsed_body),
                latency_ms=15,
                body_sha256="vuln_bopla_sha",
            )
        else:
            # Server strips privileged keys or rejects them
            clean_body = {
                k: v
                for k, v in parsed_body.items()
                if k not in ["role", "is_admin", "admin", "verified", "credit"]
            }
            resp_obs = HTTPResponseObservation(
                status_code=200,
                headers=resp_headers,
                body=json.dumps(clean_body),
                latency_ms=10,
                body_sha256="safe_bopla_sha",
            )

        return req_obs, resp_obs


@pytest.mark.asyncio
async def test_bopla_verifier_detects_mass_assignment() -> None:
    executor = MockBOPLAExecutor(vulnerable=True)
    verifier = BOPLAVerifier(executor)

    caller = Principal(
        id="user_bob",
        name="Bob",
        role=Role.USER,
        jwt_token="valid_token_bob",
    )

    finding = await verifier.verify_mass_assignment(
        endpoint_url="http://localhost:8888/identity/api/v2/user/profile",
        method=HTTPMethod.PUT,
        caller=caller,
        base_payload={"name": "Bob", "bio": "Pentester"},
        probe_keys=["role"],
    )

    assert finding is not None
    assert finding.category == VulnerabilityCategory.BOPLA
    assert "role" in finding.title
    assert "BOPLA / MASS ASSIGNMENT INVARIANT VIOLATION" in finding.verification_proof
    assert finding.attacker_principal.name == "Bob"


@pytest.mark.asyncio
async def test_bopla_verifier_passes_secure_endpoint() -> None:
    executor = MockBOPLAExecutor(vulnerable=False)
    verifier = BOPLAVerifier(executor)

    caller = Principal(
        id="user_bob",
        name="Bob",
        role=Role.USER,
        jwt_token="valid_token_bob",
    )

    finding = await verifier.verify_mass_assignment(
        endpoint_url="http://localhost:8888/identity/api/v2/user/profile",
        method=HTTPMethod.PUT,
        caller=caller,
        base_payload={"name": "Bob", "bio": "Pentester"},
        probe_keys=["role"],
    )

    assert finding is None
