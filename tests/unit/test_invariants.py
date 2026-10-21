"""Unit tests for domain invariant evaluation and noise masking."""

from agentic_pentest.domain.invariants import (
    SemanticDiffEngine,
    check_bfla_invariant,
    check_bola_invariant,
)


def test_semantic_diff_with_dynamic_noise() -> None:
    body_alice = """
    {
        "vehicle_id": "v-1234",
        "location": {"lat": 10.7626, "long": 106.6601},
        "timestamp": "2026-10-21T17:00:00Z",
        "trace_id": "tr-987123"
    }
    """
    body_bob_access = """
    {
        "trace_id": "tr-554411",
        "timestamp": "2026-10-21T17:00:05Z",
        "location": {"lat": 10.7626, "long": 106.6601},
        "vehicle_id": "v-1234"
    }
    """

    engine = SemanticDiffEngine(noise_keys={"timestamp", "trace_id"})
    similarity = engine.compute_similarity(body_alice, body_bob_access)
    assert similarity == 1.0  # Identical after masking noise keys


def test_bola_invariant_positive_vulnerability() -> None:
    # Baseline: Alice requests her vehicle -> 200 OK
    # Cross: Bob requests Alice's vehicle -> 200 OK with identical payload
    # Control: Unauthenticated requests -> 401 Unauthorized
    verdict = check_bola_invariant(
        baseline_status=200,
        cross_status=200,
        control_status=401,
        body_similarity=1.0,
    )
    assert verdict.is_vulnerable is True
    assert verdict.confidence_score >= 0.95
    assert "INV_OBJECT_ISOLATION" in verdict.violated_invariants


def test_bola_invariant_negative_properly_enforced() -> None:
    # Proper access control: Bob receives 403 Forbidden
    verdict = check_bola_invariant(
        baseline_status=200,
        cross_status=403,
        control_status=401,
        body_similarity=0.0,
    )
    assert verdict.is_vulnerable is False
    assert verdict.confidence_score == 1.0
    assert len(verdict.violated_invariants) == 0


def test_bfla_invariant_role_violation() -> None:
    # Low-privilege user accesses admin coupon endpoint successfully (200 OK)
    verdict = check_bfla_invariant(
        required_role="ADMIN",
        actual_role="USER",
        response_status=200,
    )
    assert verdict.is_vulnerable is True
    assert "INV_ROLE_HIERARCHY" in verdict.violated_invariants
