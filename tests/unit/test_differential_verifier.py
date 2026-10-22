"""Unit tests for 3-Way Differential Invariant Oracle."""

import pytest
import respx
from agentic_pentest.application.use_cases.verify_differential import DifferentialVerifier
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor
from httpx import Response

from agentic_pentest.domain.entities import HTTPMethod, Principal, Role, TargetObject


@pytest.mark.asyncio
@respx.mock
async def test_differential_verifier_confirms_bola() -> None:
    # 1. Baseline: Alice accesses her car -> 200
    respx.get("http://localhost:8888/identity/api/v2/vehicle/v123/location").mock(
        return_value=Response(
            200,
            json={"vehicle_id": "v123", "lat": 10.1, "timestamp": "2026-10-22T00:00:00Z"},
        )
    )

    alice = Principal(id="u_alice", name="Alice", role=Role.USER, jwt_token="token_alice")
    bob = Principal(id="u_bob", name="Bob", role=Role.USER, jwt_token="token_bob")
    car = TargetObject(
        id="obj_car_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )

    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    verifier = DifferentialVerifier(executor=executor)

    # Bob attempts to access Alice's car
    finding = await verifier.verify_bola(
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/{vehicle_id}/location",
        method=HTTPMethod.GET,
        target_object=car,
        legitimate_owner=alice,
        attacker=bob,
    )

    assert finding is not None
    assert finding.category.value == "BOLA"
    assert finding.target_object.id == car.id
    assert finding.attacker_principal.id == bob.id
    assert "INV_OBJECT_ISOLATION" in finding.verification_proof
