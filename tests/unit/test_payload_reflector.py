"""Unit tests for Multi-Turn Reflection and Parameter Self-Correction."""

import pytest
import respx
from httpx import Request, Response

from agentic_pentest.application.use_cases.reflect_and_retry import PayloadReflector
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor


@pytest.mark.asyncio
@respx.mock
async def test_reflector_recovers_from_missing_parameter_error() -> None:
    # First attempt without coupon_code returns 400 Bad Request
    # Second attempt with amended coupon_code returns 200 OK
    def mock_handler(request: Request) -> Response:
        body_text = request.read().decode("utf-8")
        if "coupon_code" in body_text:
            return Response(200, json={"status": "COUPON_CREATED", "discount": 100})
        return Response(400, json={"message": "coupon_code is required for creation"})

    respx.post("http://localhost:8888/community/api/v2/coupon/new-coupon").mock(
        side_effect=mock_handler
    )

    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    reflector = PayloadReflector(executor=executor)

    # Initial payload missing coupon_code
    initial_payload = {"amount": 100}
    req, resp = await reflector.execute_with_reflection(
        method="POST",
        url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        initial_payload=initial_payload,
        max_attempts=2,
    )

    # Should have reflected on the error, added coupon_code, and succeeded with HTTP 200
    assert resp.status_code == 200
    assert "COUPON_CREATED" in resp.body
