"""Unit tests for ToolErrorDiagnostician & Self-Healing recovery engine."""

from __future__ import annotations

from agentic_pentest.application.use_cases.tool_diagnostician import (
    RecoveryAction,
    ToolErrorDiagnostician,
)


def test_diagnostician_handles_rate_limiting() -> None:
    diag = ToolErrorDiagnostician()
    res = diag.diagnose(
        tool_name="verify_bola",
        error_message="HTTP 429 Too Many Requests: Rate limit exceeded",
        status_code=429,
    )
    assert res.action == RecoveryAction.RETRY_WITH_BACKOFF
    assert res.can_auto_retry is True
    assert res.delay_seconds >= 5.0
    assert "rate-limiting" in res.reason


def test_diagnostician_handles_expired_jwt() -> None:
    diag = ToolErrorDiagnostician()
    res = diag.diagnose(
        tool_name="verify_bfla",
        error_message="Token expired signature verification failed",
        status_code=401,
    )
    assert res.action == RecoveryAction.RE_AUTHENTICATE
    assert res.can_auto_retry is True
    assert res.suggested_params.get("refresh_credentials") is True


def test_diagnostician_handles_ssl_errors() -> None:
    diag = ToolErrorDiagnostician()
    res = diag.diagnose(
        tool_name="audit_security_headers",
        error_message="SSL: CERTIFICATE_VERIFY_FAILED: self-signed certificate",
    )
    assert res.action == RecoveryAction.ADD_INSECURE_FLAG
    assert res.suggested_params.get("verify_ssl") is False


def test_diagnostician_handles_connection_refused() -> None:
    diag = ToolErrorDiagnostician()
    res = diag.diagnose(
        tool_name="seed_crapi",
        error_message="ConnectEx: target machine actively refused it",
    )
    assert res.action == RecoveryAction.ESCALATE_TO_OPERATOR
    assert res.can_auto_retry is False
    assert "Check Docker" in res.reason
