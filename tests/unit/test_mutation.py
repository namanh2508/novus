"""Unit tests for PolymorphicMutator pure domain logic."""

from __future__ import annotations

from agentic_pentest.domain.mutation import (
    MutationStrategy,
    PolymorphicMutator,
)


def test_mutator_identifier_mutations() -> None:
    mutator = PolymorphicMutator()
    target_id = "test-uuid-1234-abcd"

    mutations = mutator.mutate_identifier(target_id)
    assert len(mutations) >= 5

    strategies = [m.strategy for m in mutations]
    assert MutationStrategy.UUID_TAMPERING in strategies
    assert MutationStrategy.TYPE_JUGGLING in strategies
    assert MutationStrategy.BOUNDARY_VALUE in strategies
    assert MutationStrategy.PATH_TRAVERSAL in strategies
    assert MutationStrategy.NOSQL_INJECTION in strategies

    # Check Nil UUID
    nil_mut = next(m for m in mutations if m.strategy == MutationStrategy.UUID_TAMPERING)
    assert nil_mut.mutated_value == PolymorphicMutator.NIL_UUID

    # Check NoSQL injection
    nosql_mut = next(m for m in mutations if m.strategy == MutationStrategy.NOSQL_INJECTION)
    assert nosql_mut.mutated_value == {"$ne": None}


def test_mutator_mass_assignment_payloads() -> None:
    mutator = PolymorphicMutator()
    base_payload = {"email": "alice@example.com", "name": "Alice"}

    payloads = mutator.generate_mass_assignment_payloads(base_payload)
    assert len(payloads) >= 5

    # Check that privileged keys were injected
    injected_keys = set()
    for p in payloads:
        assert p["email"] == "alice@example.com"
        assert p["name"] == "Alice"
        for k in p:
            if k not in base_payload:
                injected_keys.add(k)

    assert "role" in injected_keys
    assert "is_admin" in injected_keys
    assert "verified" in injected_keys
    assert "credit" in injected_keys
