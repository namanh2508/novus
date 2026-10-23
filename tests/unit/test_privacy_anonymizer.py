"""Unit tests for TwoWayAnonymizer (Anonproxy/Dark-Moon pattern)."""

from __future__ import annotations

from agentic_pentest.domain.privacy import TwoWayAnonymizer


def test_anonymizer_replaces_and_restores_sensitive_tokens() -> None:
    anonymizer = TwoWayAnonymizer()

    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHclp"
    email = "alice@example.com"
    uuid_str = "f89b5f21-7829-45cb-a650-299a61090378"
    host = "localhost:8888"

    raw_text = (
        f"Request target: http://{host}/api/v2/vehicle/{uuid_str}/location "
        f"with user {email} and token Bearer {jwt}"
    )

    anonymized = anonymizer.anonymize(raw_text)

    # Invariants: No sensitive value should be present in anonymized text
    assert jwt not in anonymized
    assert email not in anonymized
    assert uuid_str not in anonymized
    assert host not in anonymized

    # Surrogates should be present
    assert "SURROGATE_JWT_1" in anonymized
    assert "USER_1@anonymized.test" in anonymized
    assert "SURROGATE_UUID_1" in anonymized
    assert "target-cluster-1.local" in anonymized

    # Two-way restoration invariant: Restoring should yield exact original text
    restored = anonymizer.restore(anonymized)
    assert restored == raw_text


def test_anonymizer_preserves_consistency_across_multiple_occurrences() -> None:
    anonymizer = TwoWayAnonymizer()

    email = "bob@attacker.corp"
    text1 = f"User {email} logged in."
    text2 = f"User {email} attempted BOLA access."

    anon1 = anonymizer.anonymize(text1)
    anon2 = anonymizer.anonymize(text2)

    assert "USER_1@anonymized.test" in anon1
    assert "USER_1@anonymized.test" in anon2
    assert anonymizer.total_vault_entries == 1

    assert anonymizer.restore(anon1) == text1
    assert anonymizer.restore(anon2) == text2


def test_anonymizer_clear() -> None:
    anonymizer = TwoWayAnonymizer()
    anonymizer.anonymize("contact user@test.com on 127.0.0.1:8080")
    assert anonymizer.total_vault_entries >= 2

    anonymizer.clear()
    assert anonymizer.total_vault_entries == 0
