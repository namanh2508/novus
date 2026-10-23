"""Unit tests for extended security auditors (UC-12 to UC-15 and AI Code Guard)."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.use_cases.ai_code_guard import AICodeSecurityAuditor
from agentic_pentest.application.use_cases.audit_graphql import GraphQLSecurityAuditor
from agentic_pentest.application.use_cases.audit_jwt import JWTSecurityAuditor
from agentic_pentest.application.use_cases.audit_race_condition import RaceConditionAuditor
from agentic_pentest.application.use_cases.audit_secret_leak import SecretMemoryLeakAuditor
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    VulnerabilityCategory,
)


class MockExtendedExecutor(IHTTPExecutor):
    def __init__(self) -> None:
        self.call_count = 0

    async def execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Principal | None = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        self.call_count += 1
        req = HTTPRequestObservation(
            method=HTTPMethod[method.upper()]
            if method.upper() in HTTPMethod.__members__
            else HTTPMethod.GET,
            url=url,
            headers=headers or {},
            body=body,
        )

        resp_headers = {"content-type": "application/json"}
        resp_body = "{}"
        status_code = 200

        # GraphQL mock responses
        if "graphql" in url:
            if body and "IntrospectionProbe" in body:
                resp_body = (
                    '{"data": {"__schema": {"types": [{"name": "User"}, {"name": "Admin"}]}}}'
                )
            elif body and body.strip().startswith("["):
                resp_body = '[{"data": {"__typename": "Query"}}, {"data": {"__typename": "Query"}}]'
            else:
                resp_body = '{"data": {}}'

        # Secret leak mock responses
        elif ".env" in url:
            resp_body = "DB_PASSWORD=SuperSecretPass123\nAWS_SECRET_KEY=abcd1234efgh"
        elif ".git" in url:
            resp_body = "[core]\nrepositoryformatversion = 0"
        elif "heapdump" in url:
            resp_body = "JAVA PROFILE 1.0.2 \x00\x00 sensitive memory buffer" * 1000

        # JWT mock responses
        elif headers and "Authorization" in headers:
            auth_val = headers["Authorization"]
            if "none" in auth_val or auth_val.endswith("."):
                status_code = 200
                resp_body = '{"authenticated": true, "user": "admin"}'

        resp = HTTPResponseObservation(
            status_code=status_code,
            headers=resp_headers,
            body=resp_body,
            latency_ms=10,
            body_sha256="mock_hash",
        )
        return req, resp


def test_ai_code_guard_detects_dangerous_sinks() -> None:
    auditor = AICodeSecurityAuditor()
    vulnerable_code = """
import os
import pickle

def handle_user_input(payload):
    # Vulnerable sinks without guards
    os.system(payload)
    data = pickle.loads(payload)
    eval(payload)
"""
    report = auditor.audit_source_code(vulnerable_code)
    assert report.unprotected_sink_count >= 3
    assert report.risk_score_index > 50.0
    assert report.tree_guard_coverage_pct == 0.0
    assert len(report.alerts) >= 3


def test_ai_code_guard_detects_leaked_secrets() -> None:
    auditor = AICodeSecurityAuditor()
    code_with_secret = """
API_KEY = "sk-proj-1234567890abcdef1234567890"
AWS_KEY = "AKIA1234567890ABCDEF"
"""
    report = auditor.audit_source_code(code_with_secret)
    assert any(a.category == VulnerabilityCategory.SECRET_LEAK for a in report.alerts)


@pytest.mark.asyncio
async def test_race_condition_auditor() -> None:
    executor = MockExtendedExecutor()
    auditor = RaceConditionAuditor(executor)
    res = await auditor.audit_race_condition(
        endpoint_url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        concurrency_burst=5,
        expected_success_limit=1,
    )
    assert res.concurrent_requests_sent == 5
    assert res.successful_responses == 5
    assert res.is_vulnerable_to_race is True
    assert res.finding is not None
    assert res.finding.category == VulnerabilityCategory.RACE_CONDITION


@pytest.mark.asyncio
async def test_graphql_auditor() -> None:
    executor = MockExtendedExecutor()
    auditor = GraphQLSecurityAuditor(executor)
    res = await auditor.audit_endpoint("http://localhost:8888")
    assert res.is_graphql_detected is True
    assert res.introspection_enabled is True
    assert res.batching_attack_supported is True
    assert len(res.findings) >= 2


@pytest.mark.asyncio
async def test_jwt_auditor() -> None:
    executor = MockExtendedExecutor()
    auditor = JWTSecurityAuditor(executor)
    # Header: {"alg":"HS256","typ":"JWT"}, Payload: {"sub":"user"}, Sig: dummy
    valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.test_sig"
    res = await auditor.audit_token("http://localhost:8888/identity/api/v2/vehicle", valid_token)
    assert res.is_alg_none_vulnerable is True
    assert len(res.findings) >= 1
    assert any(f.category == VulnerabilityCategory.JWT_FLAW for f in res.findings)


@pytest.mark.asyncio
async def test_secret_leak_auditor() -> None:
    executor = MockExtendedExecutor()
    auditor = SecretMemoryLeakAuditor(executor)
    res = await auditor.audit_secrets("http://localhost:8888")
    assert len(res.exposed_paths) >= 2
    assert len(res.findings) >= 2
    assert any(f.category == VulnerabilityCategory.SECRET_LEAK for f in res.findings)
