"""Unit tests for AuthenticatedDynamicHarvester."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from agentic_pentest.application.orchestration.dynamic_harvester import (
    AuthenticatedDynamicHarvester,
)
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
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
async def test_authenticated_dynamic_harvester_extracts_endpoints_and_ids() -> None:
    executor = AsyncMock()

    async def mock_execute(
        method: str, url: str, **kwargs: Any
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        if "/dashboard" in url:
            data = {
                "user_id": "99",
                "current_vehicle": "11111111-2222-3333-4444-555555555555",
                "orders": [{"id": 501, "code": "ORD-501"}],
            }
            return _make_pair(
                200,
                json.dumps(data),
                headers={"content-type": "application/json"},
            )
        if "/profile" in url:
            return _make_pair(
                200,
                '<a href="/api/v1/orders?id=501">View Order</a>',
                headers={"content-type": "text/html"},
            )
        return _make_pair(404)

    executor.execute_request.side_effect = mock_execute

    harvester = AuthenticatedDynamicHarvester(executor, "http://target.local")
    principal = Principal(id="alice", name="Alice", role=Role.USER, jwt_token="token_alice")
    result = await harvester.harvest(principal=principal)

    assert len(result.visited_pages) >= 2
    assert "11111111-2222-3333-4444-555555555555" in result.harvested_identifiers["uuid"]
    assert (
        "99" in result.harvested_identifiers["integer_id"]
        or "501" in result.harvested_identifiers["integer_id"]
    )
    assert any(ep.path == "/dashboard" for ep in result.endpoints)
