"""Unit tests for Two-Tier MemoryManager."""

from __future__ import annotations

from agentic_pentest.application.use_cases.memory_manager import MemoryManager
from agentic_pentest.domain.entities import Principal, Role


def test_memory_manager_working_index_rendering() -> None:
    mgr = MemoryManager(target_url="http://localhost:8888")
    mgr.record_principal(Principal(id="user_alice", name="Alice", role=Role.USER))
    mgr.record_identifier("vehicle_id", "f89b5f21-7829-45cb-a650-299a61090378")
    mgr.record_tested_endpoint("/identity/api/v2/vehicle/location")
    mgr.record_hypothesis("Test BOLA access", "VERIFIED")

    md = mgr.render_working_memory_md()

    assert "http://localhost:8888" in md
    assert "user_alice" in md
    assert "f89b5f21-7829-45cb-a650-299a61090378" in md
    assert "/identity/api/v2/vehicle/location" in md
    assert "[VERIFIED] Test BOLA access" in md

    # Ensure Tier 1 memory remains concise (under ~500 tokens / 2000 chars)
    assert len(md) < 2000


def test_memory_manager_serialization_roundtrip() -> None:
    mgr = MemoryManager(target_url="http://localhost:8888")
    mgr.record_principal(
        Principal(id="user_alice", name="Alice", role=Role.USER, jwt_token="token_abc")
    )
    mgr.record_identifier("vehicle_id", "v-12345")
    mgr.record_tested_endpoint("/api/test")
    mgr.record_hypothesis("Hypothesis A", "SUCCESS")

    data = mgr.to_dict()
    reconstructed = MemoryManager.from_dict(data)

    assert reconstructed.target_url == mgr.target_url
    assert "user_alice" in reconstructed.principals
    assert reconstructed.principals["user_alice"].jwt_token == "token_abc"
    assert "v-12345" in reconstructed.identifiers["vehicle_id"]
    assert "/api/test" in reconstructed.tested_endpoints
