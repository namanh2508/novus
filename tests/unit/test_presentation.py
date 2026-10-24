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
    assert session.compact_mode is False
    session.toggle_compact()
    assert session.compact_mode is True
    session.toggle_compact()
    assert session.compact_mode is False


def test_mascot_table_rendering() -> None:
    table_full = render_mascot_table(compact=False)
    assert table_full is not None
    assert len(table_full.rows) == 8

    table_compact = render_mascot_table(compact=True)
    assert table_compact is not None
    assert len(table_compact.rows) == 4

    # Test animation non-interactive / compact fallback execution
    test_console = Console(force_terminal=False)
    animate_mascot_banner(console=test_console, compact=True)
    animate_mascot_banner(console=test_console, compact=False)


def test_chat_session_bottom_toolbar() -> None:
    session = InteractiveChatSession(target_url="http://localhost:8888")
    toolbar = session._get_bottom_toolbar()
    assert "Navigate" in toolbar.value
    assert "Select" in toolbar.value
    assert "Complete" in toolbar.value
    assert "Cancel" in toolbar.value
    assert "Safe: ON" in toolbar.value


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
