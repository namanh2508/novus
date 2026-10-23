"""Unit tests for UC-1 to UC-5 (K1-K8) tools and NaturalLanguageIntentRouter."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from agentic_pentest.application.use_cases.audit_cookies import CookieSecurityAuditor
from agentic_pentest.application.use_cases.audit_cors import CorsSecurityAuditor
from agentic_pentest.application.use_cases.audit_login import LoginSecurityAuditor
from agentic_pentest.application.use_cases.audit_security_headers import SecurityHeaderAuditor
from agentic_pentest.application.use_cases.intent_router import (
    NaturalLanguageIntentRouter,
    PentestIntent,
)
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor


@pytest.mark.asyncio
@respx.mock
async def test_uc1_security_headers_auditor() -> None:
    respx.get("http://localhost:8888/test").mock(
        return_value=Response(
            200,
            headers={
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-Content-Type-Options": "nosniff",
            },
        )
    )
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    auditor = SecurityHeaderAuditor(executor)
    result = await auditor.audit("http://localhost:8888/test")

    assert "strict-transport-security" in result.present_headers
    assert "content-security-policy" in result.missing_headers
    assert result.score > 0
    assert len(result.findings) >= 1


@pytest.mark.asyncio
@respx.mock
async def test_uc2_cookie_security_auditor() -> None:
    respx.get("http://localhost:8888/cookie").mock(
        return_value=Response(
            200,
            headers={
                "Set-Cookie": "session_id=abc12345; Path=/",
            },
        )
    )
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    auditor = CookieSecurityAuditor(executor)
    result = await auditor.audit("http://localhost:8888/cookie")

    assert result.total_cookies == 1
    assert len(result.vulnerable_cookies) == 1
    vuln = result.vulnerable_cookies[0]
    assert vuln["cookie_name"] == "session_id"
    assert any("HttpOnly" in f for f in vuln["missing_flags"])
    assert any("Secure" in f for f in vuln["missing_flags"])


@pytest.mark.asyncio
@respx.mock
async def test_uc3_cors_auditor() -> None:
    respx.get("http://localhost:8888/cors").mock(
        return_value=Response(
            200,
            headers={
                "Access-Control-Allow-Origin": "https://evil-attacker.com",
                "Access-Control-Allow-Credentials": "true",
            },
        )
    )
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    auditor = CorsSecurityAuditor(executor)
    result = await auditor.audit("http://localhost:8888/cors")

    assert result.is_vulnerable is True
    assert result.severity == "CRITICAL" or result.severity == "HIGH"
    assert result.allows_credentials is True


@pytest.mark.asyncio
@respx.mock
async def test_uc4_login_security_auditor() -> None:
    respx.get("http://localhost:8888/login").mock(
        return_value=Response(
            200,
            headers={
                "Content-Type": "text/html",
            },
        )
    )
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    auditor = LoginSecurityAuditor(executor)
    result = await auditor.audit("http://localhost:8888/login")

    assert result.has_rate_limit is False
    assert len(result.weaknesses) >= 1


def test_natural_language_intent_router() -> None:
    router = NaturalLanguageIntentRouter()

    # UC-1 Header prompt (from Teacher's feedback)
    r1 = router.route("Kiểm tra các HTTP security header của website trong scope được cấp.")
    assert r1.intent == PentestIntent.AUDIT_HEADERS
    assert r1.recommended_tool == "SecurityHeaderAuditor"

    # UC-2 Cookie prompt (from Teacher's feedback)
    r2 = router.route("Kiểm tra cookie có cấu hình thiếu Secure, HttpOnly hoặc SameSite không.")
    assert r2.intent == PentestIntent.AUDIT_COOKIES
    assert r2.recommended_tool == "CookieSecurityAuditor"

    # UC-3 CORS prompt (from Teacher's feedback)
    r3 = router.route("Đánh giá các endpoint có dấu hiệu cấu hình CORS không an toàn.")
    assert r3.intent == PentestIntent.AUDIT_CORS
    assert r3.recommended_tool == "CorsSecurityAuditor"

    # UC-4 Login prompt (from Teacher's feedback)
    r4 = router.route(
        "Kiểm tra các trang đăng nhập có dấu hiệu cấu hình bảo mật yếu không, ưu tiên phép kiểm tra ít tác động."
    )
    assert r4.intent == PentestIntent.AUDIT_LOGIN
    assert r4.recommended_tool == "LoginSecurityAuditor"

    # UC-5 BOLA / IDOR prompt
    r5 = router.route("Kiểm tra kiểm soát truy cập đối tượng BOLA/IDOR trên API.")
    assert r5.intent == PentestIntent.VERIFY_BOLA
    assert r5.recommended_tool == "DifferentialVerifier"

    # Remediation prompt
    r6 = router.route("Hướng dẫn khắc phục và vá lỗi header.")
    assert r6.intent == PentestIntent.REMEDIATION

    # Seeder prompt
    r7 = router.route("Seed tài khoản crAPI thật")
    assert r7.intent == PentestIntent.SEED_CRAPI

    # Dynamic URL extraction
    r8 = router.route("Kiểm tra header của http://127.0.0.1:8888/identity")
    assert r8.intent == PentestIntent.AUDIT_HEADERS
    assert r8.extracted_url == "http://127.0.0.1:8888/identity"


@pytest.mark.asyncio
@respx.mock
async def test_crapi_benchmark_seeder() -> None:
    from agentic_pentest.application.use_cases.seed_crapi import CrapiBenchmarkSeeder

    respx.post("http://localhost:8888/identity/api/auth/signup").mock(
        return_value=Response(200, json={"status": 200, "message": "User registered"})
    )
    respx.post("http://localhost:8888/identity/api/auth/login").mock(
        return_value=Response(200, json={"token": "mock_jwt_token_12345"})
    )
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    seeder = CrapiBenchmarkSeeder(executor)
    res = await seeder.seed("http://localhost:8888")

    assert res.status == "SUCCESS"
    assert res.alice.jwt_token == "mock_jwt_token_12345"
    assert res.bob.jwt_token == "mock_jwt_token_12345"
    assert res.target_vehicle.value == CrapiBenchmarkSeeder.DEFAULT_CRAPI_VEHICLE_UUID
