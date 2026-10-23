"""Unit tests for AdvancedFuzzyDenoiser."""

from __future__ import annotations

from agentic_pentest.domain.denoiser import AdvancedFuzzyDenoiser


def test_denoiser_uuid_and_jwt() -> None:
    denoiser = AdvancedFuzzyDenoiser()
    raw = (
        '{"id": "c138f6d2-8b74-4b53-9ec1-3fcf7f80db61", '
        '"token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgN_p_token", '
        '"status": "active"}'
    )
    result = denoiser.denoise(raw)
    assert "__NORM_UUID__" in result.denoised_text
    assert "__NORM_JWT__" in result.denoised_text
    assert result.stripped_tokens_count >= 2
    assert "UUID" in result.detected_patterns
    assert "JWT_TOKEN" in result.detected_patterns


def test_denoiser_iso_timestamp_and_epoch() -> None:
    denoiser = AdvancedFuzzyDenoiser()
    raw = '{"created_at": "2026-10-23T10:15:30.123Z", "ts": 1729678530}'
    result = denoiser.denoise(raw)
    assert "__NORM_TIMESTAMP__" in result.denoised_text
    assert "__NORM_EPOCH__" in result.denoised_text


def test_denoiser_semantic_similarity_with_dynamic_noise() -> None:
    denoiser = AdvancedFuzzyDenoiser()
    body_alice = (
        '{"carId": "f89b5f21-7829-45cb-a650-299a61090378", '
        '"time": "2026-10-23T10:00:00Z", "location": {"lat": 10.51234, "lon": 106.71234}}'
    )
    # Same object returned to attacker, but with different server timestamp and precision
    body_bob = (
        '{"carId": "f89b5f21-7829-45cb-a650-299a61090378", '
        '"time": "2026-10-23T10:00:05Z", "location": {"lat": 10.51239, "lon": 106.71239}}'
    )
    similarity = denoiser.calculate_semantic_similarity(body_alice, body_bob)
    assert similarity >= 0.95
