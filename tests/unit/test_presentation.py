"""Unit tests for presentation layer, CLI, chat session, and demo server."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest
from rich.console import Console
from typer.testing import CliRunner

from agentic_pentest.presentation.banner_art import animate_mascot_banner, render_mascot_table
from agentic_pentest.presentation.chat import InteractiveChatSession
from agentic_pentest.presentation.cli import app
from agentic_pentest.presentation.demo_server import start_live_demo_server

runner = CliRunner()


def test_cli_doctor() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Environment Diagnostics" in result.stdout


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.stdout
    assert "run" in result.stdout
    assert "chat" in result.stdout
    assert "demo-server" in result.stdout


def test_live_demo_server_endpoints() -> None:
    server = start_live_demo_server(host="127.0.0.1", port=8999)
    try:
        # 1. Healthcheck
        req = urllib.request.Request("http://127.0.0.1:8999/identity/api/auth/v1/health")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            assert data["status"] == "HEALTHY"

        # 2. Login
        login_data = json.dumps({"email": "alice@crapi.local", "password": "Password123!"}).encode()
        req_login = urllib.request.Request(
            "http://127.0.0.1:8999/identity/api/auth/v1/login",
            data=login_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_login) as resp:
            data = json.loads(resp.read().decode())
            assert "token" in data
            assert data["user"]["name"] == "Alice"
    finally:
        server.shutdown()


def test_chat_session_commands() -> None:
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")
    # Status and help should execute without error
    session.print_status()
    session.print_help()
    session.show_graph()
    session.show_findings()
    session.show_poc()
    session.show_banner()
    assert not session.compact_mode
    session.toggle_compact()
    assert session.compact_mode
    session.toggle_compact()
    assert not session.compact_mode
    assert not session.pixel_mode
    session.toggle_pixel()
    assert session.pixel_mode
    session.toggle_pixel()
    assert not session.pixel_mode
    assert session.show_toolbar
    tb_active = session._get_bottom_toolbar()
    assert "navigate" in tb_active.value
    session.toggle_toolbar()
    assert not session.show_toolbar
    tb_disabled = session._get_bottom_toolbar()
    assert tb_disabled.value == ""
    session.toggle_toolbar()
    assert session.show_toolbar


@pytest.mark.asyncio
async def test_chat_session_model_and_ssrf() -> None:
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")
    # 1. Model check executes and renders diagnostic table
    await session.check_model()

    # 2. SSRF audit runs against mock endpoint without unhandled exceptions
    await session.audit_ssrf("/community/api/v2/coupon/new-coupon")

    # 3. Add dummy finding and test multi-format PoCs
    from datetime import UTC, datetime

    from agentic_pentest.domain.entities import (
        DifferentialTriplet,
        Finding,
        HTTPMethod,
        HTTPRequestObservation,
        HTTPResponseObservation,
        Severity,
        TargetObject,
        VulnerabilityCategory,
    )

    now = datetime.now(UTC)
    obj = TargetObject(id="o1", type_name="vehicle", owner_principal_id="alice", value="v123")
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://127.0.0.1:8888/identity/api/v2/vehicle/v123/location",
        headers={"Authorization": "Bearer token_bob"},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"vehicle_id": "v123"}',
        latency_ms=20,
        body_sha256="sha",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )
    f = Finding(
        id="FINDING-PRES-01",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="Test BOLA",
        endpoint_url="http://127.0.0.1:8888/identity/api/v2/vehicle/v123/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=session.bob,
        triplet=triplet,
        verification_proof="Verified invariant breach",
        created_at=now,
    )
    session.findings.append(f)

    # Test each language generator
    session.show_poc("curl")
    session.show_poc("go")
    session.show_poc("node")
    session.show_poc("all")
    session.show_poc("python")

    # 4. Test fuzzing and exploit guides
    await session.audit_fuzz()
    session.show_exploit_guide()
    session.show_exploit_guide("memory")
    session.show_exploit_guide("mitigations")
    session.show_exploit_guide("tools")


def test_mascot_table_rendering() -> None:
    table_sleek = render_mascot_table(compact=False)
    assert table_sleek is not None
    assert len(table_sleek.rows) == 4

    table_compact = render_mascot_table(compact=True)
    assert table_compact is not None
    assert len(table_compact.rows) == 3

    table_pixel = render_mascot_table(pixel_mode=True)
    assert table_pixel is not None
    assert len(table_pixel.rows) == 10

    test_console = Console(force_terminal=False)
    animate_mascot_banner(console=test_console, compact=True)
    animate_mascot_banner(console=test_console, compact=False)
    animate_mascot_banner(console=test_console, pixel_mode=True)


def test_live_demo_server_bola_token_enforcement() -> None:
    server = start_live_demo_server(host="127.0.0.1", port=8998)
    try:
        # 1. Anonymous request should be rejected (401)
        req_anon = urllib.request.Request(
            "http://127.0.0.1:8998/identity/api/v2/vehicle/v-alice-101/location"
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req_anon)
        assert exc_info.value.code == 401

        # 2. Garbage token request should be rejected (401)
        req_garbage = urllib.request.Request(
            "http://127.0.0.1:8998/identity/api/v2/vehicle/v-alice-101/location",
            headers={"Authorization": "Bearer invalid_garbage_token"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req_garbage)
        assert exc_info.value.code == 401

        # 3. Authenticated request from Bob succeeds (200 - BOLA verified)
        req_bob = urllib.request.Request(
            "http://127.0.0.1:8998/identity/api/v2/vehicle/v-alice-101/location",
            headers={"Authorization": "Bearer token_bob"},
        )
        with urllib.request.urlopen(req_bob) as resp:
            data = json.loads(resp.read().decode())
            assert resp.status == 200
            assert data["vehicle_id"] == "v-alice-101"
            assert "location" in data
    finally:
        server.shutdown()


def test_checkpoint_save_and_resume() -> None:
    session = InteractiveChatSession(target_url="http://test.local:8888")
    session.permission_mode = "strict"
    cp_path = session.save_checkpoint("test_unit_checkpoint")
    assert cp_path.exists()

    session_resumed = InteractiveChatSession(target_url="http://other.url")
    ok = session_resumed.resume_checkpoint("test_unit_checkpoint")
    assert ok is True
    assert session_resumed.target_url == "http://test.local:8888"
    assert session_resumed.permission_mode == "strict"

    # Cleanup test checkpoint
    if cp_path.exists():
        cp_path.unlink()


def test_cli_auto_command_help() -> None:
    result = runner.invoke(app, ["auto", "--help"])
    assert result.exit_code == 0
    assert "autonomous" in result.stdout.lower()
    assert "--sarif" in result.stdout
    assert "--safe-mode" in result.stdout


@pytest.mark.asyncio
async def test_chat_rollback_and_mission() -> None:
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")
    # 1. Rollback status executes without error on empty journal
    await session.show_rollback_status()

    # 2. Record a mutation and check rollback status
    from agentic_pentest.domain.safety.rollback_journal import CompensationType, RollbackRecipe

    session.rollback_manager.journal.record_mutation(
        entry_id="rb-test-01",
        target_endpoint="http://127.0.0.1:8888/identity/api/v2/vehicle/v-1",
        original_method="DELETE",
        target_object_id="v-1",
        recipe=RollbackRecipe(
            revert_method="POST",
            revert_url="http://127.0.0.1:8888/identity/api/v2/vehicle",
            compensation_type=CompensationType.RECREATE_VIA_POST,
            revert_body='{"id": "v-1"}',
        ),
        original_state_body='{"id": "v-1"}',
    )
    assert session.rollback_manager.journal.pending_count == 1

    from datetime import UTC, datetime
    from unittest.mock import AsyncMock

    from agentic_pentest.domain.entities import HTTPRequestObservation, HTTPResponseObservation

    mock_resp = HTTPResponseObservation(
        status_code=201,
        headers={},
        body='{"status": "restored"}',
        body_sha256="abc123hash",
        latency_ms=1.0,
        timestamp=datetime.now(UTC),
    )
    mock_req = HTTPRequestObservation(
        method="POST",
        url="http://127.0.0.1:8888/identity/api/v2/vehicle",
        headers={},
        body='{"id": "v-1"}',
        timestamp=datetime.now(UTC),
    )
    session.executor.execute_request = AsyncMock(return_value=(mock_req, mock_resp))
    await session.show_rollback_status()
    assert session.rollback_manager.journal.restored_count == 1
