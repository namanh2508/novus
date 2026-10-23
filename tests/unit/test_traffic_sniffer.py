"""Unit tests for PassiveTrafficSniffer."""

from __future__ import annotations

import base64
import json

from agentic_pentest.domain.entities import HTTPMethod, Role
from agentic_pentest.infrastructure.interception.traffic_sniffer import PassiveTrafficSniffer
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


def _generate_test_jwt(email: str, role: str) -> str:
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = (
        base64.urlsafe_b64encode(json.dumps({"sub": email, "role": role}).encode())
        .decode()
        .rstrip("=")
    )
    return f"{header}.{payload}.signature"


def test_sniffer_extracts_jwt_principal() -> None:
    graph = NetworkXEvidenceGraph()
    sniffer = PassiveTrafficSniffer(graph=graph)

    jwt = _generate_test_jwt("alice@example.com", "ADMIN")
    principal = sniffer._extract_jwt_principal(jwt)

    assert principal is not None
    assert principal.id == "alice@example.com"
    assert principal.name == "alice"
    assert principal.role == Role.ADMIN
    assert principal.jwt_token == jwt


def test_sniffer_extracts_path_target_object() -> None:
    graph = NetworkXEvidenceGraph()
    sniffer = PassiveTrafficSniffer(graph=graph)

    uuid_val = "f89b5f21-7829-45cb-a650-299a61090378"
    path = f"/identity/api/v2/vehicles/{uuid_val}/location"
    target_obj = sniffer._extract_path_target_object(path)

    assert target_obj is not None
    assert target_obj.type_name == "vehicle"
    assert target_obj.value == uuid_val


def test_sniffer_process_traffic_observation_injects_graph() -> None:
    graph = NetworkXEvidenceGraph()
    sniffer = PassiveTrafficSniffer(graph=graph)

    jwt = _generate_test_jwt("bob@example.com", "USER")
    headers = {"authorization": f"Bearer {jwt}", "content-type": "application/json"}
    uuid_val = "f89b5f21-7829-45cb-a650-299a61090378"

    sniffer._process_traffic_observation(
        method=HTTPMethod.GET,
        url=f"http://localhost:8888/identity/api/v2/vehicles/{uuid_val}/location",
        req_headers=headers,
        req_body=None,
        status_code=200,
        resp_headers={"content-type": "application/json"},
        resp_body='{"carId": "123"}',
        resp_hash="abc",
        latency_ms=12,
    )

    assert sniffer.stats.requests_intercepted == 1
    assert sniffer.stats.principals_discovered == 1
    assert sniffer.stats.objects_discovered == 1
    assert graph.node_count() >= 2
