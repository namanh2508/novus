"""Unit tests for SOTA agentic extensions: Tool Call Repair, Net Policy, and Semantic Grepper."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_pentest.domain.safety.net_policy import NetworkScopePolicy
from agentic_pentest.infrastructure.discovery.semantic_grepper import SemanticCodeGrepper
from agentic_pentest.infrastructure.reasoning.tool_call_repair import (
    ToolCallRepairEngine,
)


def test_tool_call_repair_markdown_and_trailing_commas() -> None:
    # 1. Markdown code fence with trailing commas and Python constants
    raw_markdown = """```json
    {
        'target_url': 'http://localhost:8888',
        'safe_mode': True,
        'retry_count': 3,
    }
    ```"""
    parsed = ToolCallRepairEngine.repair_and_parse(raw_markdown)
    assert parsed["target_url"] == "http://localhost:8888"
    assert parsed["safe_mode"] is True
    assert parsed["retry_count"] == 3


def test_tool_call_repair_truncated_braces() -> None:
    # 2. Truncated output missing closing brace
    raw_truncated = '{"action": "scan", "options": {"depth": 2'
    parsed = ToolCallRepairEngine.repair_and_parse(raw_truncated)
    assert parsed["action"] == "scan"
    assert parsed["options"]["depth"] == 2


def test_net_policy_scope_and_cloud_metadata() -> None:
    policy = NetworkScopePolicy(
        allowed_hosts_or_cidrs=["target.org", "192.168.1.0/24"],
        block_cloud_metadata=True,
    )

    # Allowed target
    assert policy.is_target_in_scope("https://target.org/api/v1") is True
    assert policy.is_target_in_scope("http://sub.target.org:8080/path") is True
    assert policy.is_target_in_scope("http://192.168.1.50:8000") is True

    # Out of scope target
    assert policy.is_target_in_scope("https://evil.attacker.org") is False
    assert policy.is_target_in_scope("http://10.0.0.1") is False

    # Cloud metadata tripwire
    assert policy.is_cloud_metadata("169.254.169.254") is True
    assert policy.is_cloud_metadata("metadata.google.internal") is True
    assert policy.is_target_in_scope("http://169.254.169.254/latest/meta-data/") is False


def test_net_policy_url_redaction() -> None:
    url_sensitive = (
        "https://admin:superSecretPass@api.target.com/v1/users?token=eyJhbGciOiJIUzI1NiJ9&page=1"
    )
    redacted = NetworkScopePolicy.redact_sensitive_url(url_sensitive)
    assert "superSecretPass" not in redacted
    assert "admin:***@" in redacted
    assert "token=***" in redacted
    assert "page=1" in redacted


def test_semantic_code_grepper() -> None:
    grepper = SemanticCodeGrepper()

    with tempfile.TemporaryDirectory() as tmp_dir:
        sample_file = Path(tmp_dir) / "routes.py"
        sample_file.write_text(
            """
@app.post("/identity/api/v2/vehicle/location")
def get_location():
    vehicle_id = params['vehicle_id']
    jwt_secret = "super_hardcoded_jwt_secret_123"
    db.execute(f"SELECT * FROM vehicles WHERE id = '{vehicle_id}'")
            """,
            encoding="utf-8",
        )

        findings = grepper.scan_directory(tmp_dir)
        rule_ids = {f.rule_id for f in findings}

        assert "UNAUTHENTICATED_MUTATING_ROUTE" in rule_ids
        assert "POTENTIAL_IDOR_PARAM_BINDING" in rule_ids
        assert "HARDCODED_SECRET_OR_JWT_KEY" in rule_ids
        assert "SQL_STRING_FORMATTING_TAINT" in rule_ids
