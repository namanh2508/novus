"""Unit tests for Evidence-Guided Adaptive Planner."""

import pytest

from agentic_pentest.application.use_cases.plan_next_action import AdaptivePlanner
from agentic_pentest.domain.entities import Principal, Role, TargetObject
from agentic_pentest.infrastructure.playbooks.registry import PlaybookRegistry
from agentic_pentest.infrastructure.reasoning.litellm_client import LiteLLMClient
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


@pytest.mark.asyncio
async def test_adaptive_planner_schedules_cross_principal_targets() -> None:
    graph = NetworkXEvidenceGraph()
    alice = Principal(id="u_alice", name="Alice", role=Role.USER)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER)
    car_alice = TargetObject(
        id="obj_car_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )
    graph.add_principal(alice)
    graph.add_principal(bob)
    graph.add_object(car_alice)
    graph.add_access_edge("u_alice", "obj_car_1", relation="OWNS")

    registry = PlaybookRegistry()
    registry.load_playbooks("src/agentic_pentest/infrastructure/playbooks/data")
    llm = LiteLLMClient(fallback_offline=True)

    planner = AdaptivePlanner(graph=graph, playbook_registry=registry, llm_client=llm)
    actions = await planner.plan_next_actions(attacker_id="u_bob", max_actions=3)

    assert len(actions) >= 1
    assert any(a.action_type == "VERIFY_BOLA" for a in actions)
