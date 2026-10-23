"""Unit tests for HypothesisTreePlanner (Tree-of-Thoughts / MCTS pattern)."""

from __future__ import annotations

from agentic_pentest.application.use_cases.hypothesis_tree import (
    HypothesisTreePlanner,
    NodeStatus,
)
from agentic_pentest.domain.entities import VulnerabilityCategory


def test_hypothesis_tree_addition_and_priority_selection() -> None:
    planner = HypothesisTreePlanner()

    node1 = planner.add_hypothesis(
        category=VulnerabilityCategory.BOLA,
        endpoint="/api/v1/user/100",
        description="Test BOLA on user endpoint",
        estimated_priority=0.7,
    )

    node2 = planner.add_hypothesis(
        category=VulnerabilityCategory.BFLA,
        endpoint="/api/v1/admin/delete",
        description="Test BFLA on admin endpoint",
        estimated_priority=0.95,
    )

    node3 = planner.add_hypothesis(
        category=VulnerabilityCategory.BOPLA,
        endpoint="/api/v1/user/profile",
        description="Test Mass Assignment on profile",
        estimated_priority=0.85,
    )

    # First selection should pick node2 (priority 0.95)
    selected = planner.select_next_hypothesis()
    assert selected is not None
    assert selected.id == node2.id
    assert selected.status == NodeStatus.EXPLORING

    # Next selection should pick node3 (priority 0.85)
    selected2 = planner.select_next_hypothesis()
    assert selected2 is not None
    assert selected2.id == node3.id

    # Next selection should pick node1 (priority 0.7)
    selected3 = planner.select_next_hypothesis()
    assert selected3 is not None
    assert selected3.id == node1.id

    # When all are exploring, none pending
    assert planner.select_next_hypothesis() is None


def test_hypothesis_tree_branching_and_backtracking() -> None:
    planner = HypothesisTreePlanner()

    parent = planner.add_hypothesis(
        category=VulnerabilityCategory.BOLA,
        endpoint="/identity/api/v2/vehicle",
        description="Probe vehicle resource",
        estimated_priority=0.8,
    )

    # Add child hypothesis branching from parent
    child = planner.add_hypothesis(
        category=VulnerabilityCategory.BOLA,
        endpoint="/identity/api/v2/vehicle/location",
        description="Probe location sub-resource",
        estimated_priority=0.9,
        parent_id=parent.id,
    )
    assert child.depth == 1

    # Mark child as verified
    planner.mark_outcome(child.id, verified=True)
    assert child.status == NodeStatus.VERIFIED

    # Mark parent as exhausted
    planner.mark_outcome(parent.id, verified=False)
    assert parent.status == NodeStatus.EXHAUSTED

    verified_nodes = planner.get_verified_nodes()
    assert len(verified_nodes) == 1
    assert verified_nodes[0].id == child.id

    summary = planner.get_summary()
    assert summary[NodeStatus.VERIFIED.value] == 1
    assert summary[NodeStatus.EXHAUSTED.value] == 1
