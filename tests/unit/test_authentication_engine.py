"""Unit tests for Dynamic Authentication Engine and JWT claim parsing."""

import pytest
import respx
from httpx import Response

from agentic_pentest.application.use_cases.authenticate_principals import AuthenticationEngine
from agentic_pentest.domain.entities import Role
from agentic_pentest.infrastructure.executors.httpx_executor import HTTPXExecutor
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


@pytest.mark.asyncio
@respx.mock
async def test_authenticate_and_ingest_into_graph() -> None:
    # Sample unverified JWT: header.payload.signature
    # Payload: {"sub": "u_alice_99", "email": "alice@crapi.local", "role": "ROLE_USER"}
    jwt_payload_b64 = "eyJzdWIiOiAidV9hbGljZV85OSIsICJlbWFpbCI6ICJhbGljZUBjcmFwaS5sb2NhbCIsICJyb2xlIjogIlJPTEVfVVNFUiJ9"
    mock_jwt = f"eyJhbGciOiJIUzI1NiJ9.{jwt_payload_b64}.mock_signature"

    respx.post("http://localhost:8888/identity/api/auth/v1/login").mock(
        return_value=Response(200, json={"token": mock_jwt})
    )

    executor = HTTPXExecutor(allowed_hosts=["localhost:8888"])
    graph = NetworkXEvidenceGraph()
    auth_engine = AuthenticationEngine(executor=executor, graph=graph)

    principal = await auth_engine.authenticate_user(
        login_url="http://localhost:8888/identity/api/auth/v1/login",
        email="alice@crapi.local",
        password="Password123!",
        principal_id="alice_fallback",
        role=Role.USER,
    )

    assert principal.id == "u_alice_99"
    assert principal.name == "Alice"
    assert principal.jwt_token == mock_jwt
    assert len(graph.to_dict()["nodes"]) >= 1
