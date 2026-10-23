"""Unit tests for EpisodicKnowledgeBase SQLite storage."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_pentest.infrastructure.storage.episodic_knowledge import EpisodicKnowledgeBase


def test_episodic_knowledge_record_and_query() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_knowledge.db")
        kb = EpisodicKnowledgeBase(db_path)

        kb.record_learning(
            framework="crapi",
            category="BOLA",
            heuristic_insight="Vehicle location endpoint leaks GPS if object UUID is forged",
            conviction_score=0.9,
        )

        kb.record_learning(
            framework="crapi",
            category="BFLA",
            heuristic_insight="Coupon creation endpoint lacks administrative role check",
            conviction_score=0.95,
        )

        # Re-record to verify increment
        kb.record_learning(
            framework="crapi",
            category="BOLA",
            heuristic_insight="Vehicle location endpoint leaks GPS if object UUID is forged",
            conviction_score=0.9,
        )

        learnings = kb.query_learnings("crapi")
        assert len(learnings) == 2

        bola_learning = next(item for item in learnings if item["category"] == "BOLA")
        assert bola_learning["successful_verifications"] == 2
        assert bola_learning["conviction_score"] >= 0.95

        bfla_learning = next(item for item in learnings if item["category"] == "BFLA")
        assert bfla_learning["successful_verifications"] == 1

        kb.close()
