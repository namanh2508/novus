"""Unit tests for DynamicAuthManager."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from agentic_pentest.application.orchestration.dynamic_auth import (
    AuthMechanism,
    DynamicAuthManager,
)
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
)


def _make_pair(
    status: int, body: str = "", headers: dict[str, str] | None = None
) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888",
        headers={},
        body=None,
        timestamp=datetime.now(UTC),
    )
    resp = HTTPResponseObservation(
        status_code=status,
        headers=headers or {},
        body=body,
        latency_ms=10,
        body_sha256="abc",
        timestamp=datetime.now(UTC),
    )
    return req, resp


@pytest.mark.asyncio
async def test_detect_auth_surface_finds_login_form() -> None:
    executor = AsyncMock()

    async def mock_execute(
        method: str, url: str, **kwargs: Any
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        if "/login" in url:
            html = '<form action="/login"><input name="username"><input type="password" name="password"><input name="_csrf" value="tok123"></form>'
            return _make_pair(200, html)
        if "/register" in url:
            return _make_pair(200, '<form action="/register"></form>')
        return _make_pair(404, "Not Found")

    executor.execute_request.side_effect = mock_execute

    mgr = DynamicAuthManager(executor, "http://target.local")
    surface = await mgr.detect_auth_surface()

    assert surface.requires_auth is True
    assert surface.login_url == "http://target.local/login"
    assert surface.register_url == "http://target.local/register"
    assert "username" in surface.form_fields
    assert "password" in surface.form_fields
    assert surface.csrf_token == "tok123"


@pytest.mark.asyncio
async def test_provision_with_user_supplied_token_and_cookie() -> None:
    executor = AsyncMock()
    mgr = DynamicAuthManager(executor, "http://target.local")

    res_token = await mgr.provision(token="jwt.token.val")
    assert res_token.success is True
    assert res_token.mechanism == AuthMechanism.JWT_BEARER
    assert res_token.principal_alice is not None
    assert res_token.principal_alice.jwt_token == "jwt.token.val"

    res_cookie = await mgr.provision(cookie="sessionid=xyz123")
    assert res_cookie.success is True
    assert res_cookie.mechanism == AuthMechanism.SESSION_COOKIE
    assert res_cookie.principal_alice is not None
    assert res_cookie.principal_alice.session_headers["Cookie"] == "sessionid=xyz123"


@pytest.mark.asyncio
async def test_provision_via_auto_registration() -> None:
    executor = AsyncMock()

    async def mock_execute(
        method: str, url: str, **kwargs: Any
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        if method == "GET" and "/login" in url:
            return _make_pair(200, '<input type="password">')
        if method == "GET" and "/signup" in url:
            return _make_pair(200, "signup page")
        if method == "POST" and "/signup" in url:
            return _make_pair(201, '{"status": "created"}')
        if method == "POST" and "/login" in url:
            return _make_pair(200, '{"token": "auth_token_999"}')
        return _make_pair(404)

    executor.execute_request.side_effect = mock_execute

    mgr = DynamicAuthManager(executor, "http://target.local")
    res = await mgr.provision()

    assert res.success is True
    assert res.mechanism == AuthMechanism.JWT_BEARER
    assert res.principal_alice is not None
    assert res.principal_bob is not None
    assert res.principal_alice.jwt_token == "auth_token_999"


@pytest.mark.asyncio
async def test_provision_fallback_requires_user_input() -> None:
    executor = AsyncMock()

    async def mock_execute(
        method: str, url: str, **kwargs: Any
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        if method == "GET" and "/login" in url:
            return _make_pair(200, '<input type="password">')
        if method == "POST" and "/login" in url:
            return _make_pair(401, '{"error": "Unauthorized"}')
        return _make_pair(404)

    executor.execute_request.side_effect = mock_execute

    mgr = DynamicAuthManager(executor, "http://target.local")
    res = await mgr.provision()

    assert res.success is False
    assert res.requires_user_input is True
    assert "Please provide --auth" in res.details
