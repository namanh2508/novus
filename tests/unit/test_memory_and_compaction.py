"""Unit tests for Two-Tier Memory, SelectiveCompactor, and LoopDetector."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_pentest.application.use_cases.memory_manager import (
    LoopDetector,
    MemoryManager,
    SelectiveCompactor,
)


def test_two_tier_topic_notes_and_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_file = Path(tmpdir) / "MEMORY.md"
        topics_dir = Path(tmpdir) / "topics"

        mgr = MemoryManager(
            target_url="http://test.local",
            memory_file=str(mem_file),
            topics_dir=str(topics_dir),
        )

        # Record active notes
        mgr.record_topic_note("auth", "Session cookie JSESSIONID=123 active")
        mgr.record_topic_note("auth", "Temporary bearer token issued")

        # Mark obsolete note as superseded
        mgr.supersede_topic_note("auth", "JSESSIONID")

        assert mem_file.exists()
        auth_topic_file = topics_dir / "auth.md"
        assert auth_topic_file.exists()

        content = auth_topic_file.read_text(encoding="utf-8")
        assert "## Active Knowledge" in content
        assert "Temporary bearer token issued" in content
        assert "## Superseded / Deprecated Knowledge" in content
        assert "JSESSIONID=123" in content


def test_selective_compactor_preserves_invariants_and_prunes_bloat() -> None:
    compactor = SelectiveCompactor(max_body_chars=60)

    short_text = "Status: 200 OK - Token verified"
    assert compactor.compact_observation(short_text) == short_text

    long_html = "<html>" + ("<div>lots of content</div>" * 20) + "</html>"
    compacted = compactor.compact_observation(long_html)
    assert len(compacted) < len(long_html)
    assert "[compacted" in compacted

    # Compact JSON arrays
    big_json = [{"id": i, "data": f"item_{i}"} for i in range(100)]
    compact_json = compactor.compact_json_data(big_json, max_items=2)
    assert compact_json["__type__"] == "compacted_array"
    assert compact_json["total_items"] == 100
    assert len(compact_json["sample"]) == 2


def test_loop_detector_triggers_on_repeats_and_pingpong() -> None:
    detector = LoopDetector(max_repeats=3)

    # 1. Repeated calls
    is_loop, advice = detector.record_call("verify_bola", {"url": "http://test", "id": "1"})
    assert is_loop is False

    is_loop, advice = detector.record_call("verify_bola", {"url": "http://test", "id": "1"})
    assert is_loop is False

    is_loop, advice = detector.record_call("verify_bola", {"url": "http://test", "id": "1"})
    assert is_loop is True
    assert advice is not None
    assert "Loop Warning" in advice

    # 2. Alternating ping-pong calls (A -> B -> A -> B)
    detector2 = LoopDetector(max_repeats=5)
    detector2.record_call("tool_a", {"step": 1})
    detector2.record_call("tool_b", {"step": 1})
    detector2.record_call("tool_a", {"step": 1})
    is_loop, advice = detector2.record_call("tool_b", {"step": 1})
    assert is_loop is True
    assert "Oscillating Loop Warning" in (advice or "")
