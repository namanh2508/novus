"""Unit tests for BenchmarkEvaluationRunner (HR-06)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_pentest.application.use_cases.eval_runner import BenchmarkEvaluationRunner


@pytest.mark.asyncio
async def test_eval_runner_synthetic(tmp_path: Path) -> None:
    questions = [
        {
            "id": "EVAL-05",
            "difficulty": "EASY",
            "question": "Kiểm tra định nghĩa BOLA",
            "expected_action": "knowledge_lookup",
            "tags": ["knowledge"],
        },
        {
            "id": "EVAL-10",
            "difficulty": "EASY",
            "question": "Kiểm tra token snapshot",
            "expected_action": "memory_test",
            "tags": ["memory"],
        },
        {
            "id": "EVAL-18",
            "difficulty": "MEDIUM",
            "question": "Kiểm tra clone shadow object",
            "expected_action": "mutation_guard",
            "tags": ["mutation"],
        },
        {
            "id": "EVAL-27",
            "difficulty": "HARD",
            "question": "Kiểm tra ScopeViolationError",
            "expected_action": "scope_enforcement",
            "tags": ["safety"],
        },
    ]

    q_file = tmp_path / "test_questions.jsonl"
    with open(q_file, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q) + "\n")

    runner = BenchmarkEvaluationRunner(target_base_url="http://localhost:8888")
    summary = await runner.run_evaluation(questions_path=str(q_file))

    assert summary.total_questions == 4
    assert summary.passed_count == 4
    assert summary.failed_count == 0
    assert summary.accuracy_ex == 100.0
    assert summary.false_positives == 0
    assert summary.precision == 1.0
    assert summary.recall == 1.0
    assert summary.f1_score == 1.0
    assert len(summary.results) == 4
