"""Unit tests for presentation layer, CLI, chat session, and demo server."""

from __future__ import annotations

import json
import urllib.request

from typer.testing import CliRunner

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
