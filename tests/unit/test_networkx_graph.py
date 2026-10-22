"""Unit tests for NetworkX Evidence Graph adapter."""

from agentic_pentest.domain.entities import Principal, Role, TargetObject
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


def test_evidence_graph_principals_and_objects() -> None:
    graph = NetworkXEvidenceGraph()

    alice = Principal(id="u_alice", name="Alice", role=Role.USER)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER)
    car_alice = TargetObject(
        id="obj_car_1",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="uuid-car-alice",
    )
    car_bob = TargetObject(
        id="obj_car_2",
        type_name="vehicle_id",
        owner_principal_id="u_bob",
        value="uuid-car-bob",
    )

    graph.add_principal(alice)
    graph.add_principal(bob)
    graph.add_object(car_alice)
    graph.add_object(car_bob)

    # Establish ownership edges
    graph.add_access_edge("u_alice", "obj_car_1", relation="OWNS")
    graph.add_access_edge("u_bob", "obj_car_2", relation="OWNS")

    # Alice's objects
    alice_objs = graph.get_principal_objects("u_alice")
    assert len(alice_objs) == 1
    assert alice_objs[0].id == "obj_car_1"

    # Cross-principal targets for Bob (all objects not owned by Bob)
    cross_targets = graph.get_cross_principal_targets("u_bob")
    assert len(cross_targets) == 1
    assert cross_targets[0].id == "obj_car_1"
    assert cross_targets[0].owner_principal_id == "u_alice"
