"""Unit tests for ContextEngineer and selective compaction."""

from __future__ import annotations

from agentic_pentest.application.use_cases.context_manager import ContextEngineer
from agentic_pentest.domain.entities import AgentGoal, AgentTurn


def test_context_engineer_summarize_observation() -> None:
    engineer = ContextEngineer()

    short_text = "HTTP 200 OK: Content-Type: application/json"
    assert engineer.summarize_observation(short_text, max_length=100) == short_text

    long_text = "A" * 1000
    summary = engineer.summarize_observation(long_text, max_length=200)
    assert len(summary) < 300
    assert "truncated" in summary


def test_context_engineer_compact_turns() -> None:
    engineer = ContextEngineer()

    turns = [
        AgentTurn(
            turn_number=i,
            thought=f"Thought {i}",
            tool_name=f"tool_{i}",
            tool_arguments={},
            observation_summary=f"Obs {i}",
            is_success=True,
        )
        for i in range(10)
    ]

    compacted = engineer.compact_turns(turns, max_turns_to_keep=4)
    assert len(compacted) == 4
    assert compacted[0].turn_number == 6
    assert compacted[-1].turn_number == 9


def test_context_engineer_build_loop_prompt() -> None:
    engineer = ContextEngineer()
    goal = AgentGoal(target_url="http://localhost:8888", max_turns=5)

    prompt = engineer.build_loop_prompt(
        goal=goal,
        memory_summary="- Target: http://localhost:8888\n- Active Principals: Alice",
        recent_turns=[],
        findings=[],
        anti_loop_warning="Warning: Loop detected",
    )

    assert "=== AGENT MISSION ===" in prompt
    assert "http://localhost:8888" in prompt
    assert "=== WORKING MEMORY ===" in prompt
    assert "Warning: Loop detected" in prompt
    assert "=== NEXT ACTION REQUIRED ===" in prompt
