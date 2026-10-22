"""Unit tests for Dynamic Object Harvester."""

import pytest
import respx
from httpx import Response

from agentic_pentest.application.use_cases.harvest_objects import ObjectHarvester
from agentic_pentest.domain.entities import Principal, Role
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


@pytest.mark.asyncio
@respx.mock
async def test_harvest_objects_from_api_response() -> None:
    respx.get("http://localhost:8888/identity/api/v2/vehicle/vehicles").mock(
        return_value=Response(
            200,
            json=[
                {"id": 1, "vin": "VIN-123456", "vehicle_id": "uuid-car-01", "model": "Tesla"},
                {"id": 2, "vin": "VIN-987654", "vehicle_id": "uuid-car-02", "model": "Ford"},
            ],
        )
    )

    alice = Principal(id="u_alice", name="Alice", role=Role.USER, jwt_token="token_alice")
    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    graph = NetworkXEvidenceGraph()
    graph.add_principal(alice)

    harvester = ObjectHarvester(executor=executor, graph=graph)
    harvested = await harvester.harvest_from_endpoint(
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/vehicles",
        principal=alice,
        expected_type="vehicle",
    )

    assert len(harvested) >= 2
    types = {h.type_name for h in harvested}
    assert "vehicle_id" in types or "vin" in types

    # Graph should have established ownership
    alice_objects = graph.get_principal_objects("u_alice")
    assert len(alice_objects) >= 2
