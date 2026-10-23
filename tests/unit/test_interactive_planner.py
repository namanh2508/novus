"""Unit tests for InteractivePentestPlanner."""

from __future__ import annotations

from agentic_pentest.application.use_cases.interactive_planner import (
    InteractivePentestPlanner,
    PlanStepStatus,
)


def test_planner_generates_standard_plan() -> None:
    planner = InteractivePentestPlanner()
    steps = planner.generate_standard_plan("http://localhost:8888")

    assert len(steps) >= 6
    assert steps[0].id == "STEP-01"
    assert "Headers" in steps[0].title
    assert steps[0].owasp_api_category == "API8:2023 Security Misconfiguration"

    step_categories = [s.owasp_api_category for s in steps]
    assert any("API1:2023" in c for c in step_categories)
    assert any("API5:2023" in c for c in step_categories)
    assert any("API3:2023" in c for c in step_categories)


def test_planner_step_progression_and_coverage() -> None:
    planner = InteractivePentestPlanner()
    planner.generate_standard_plan("http://localhost:8888")

    assert planner.calculate_coverage() == 0.0

    step1 = planner.get_next_step()
    assert step1 is not None
    assert step1.id == "STEP-01"

    planner.mark_step_in_progress("STEP-01")
    assert step1.status == PlanStepStatus.IN_PROGRESS

    planner.mark_step_completed("STEP-01", summary="Headers verified", findings_count=0)
    assert step1.status == PlanStepStatus.COMPLETED

    coverage_1 = planner.calculate_coverage()
    assert coverage_1 > 0.0

    step2 = planner.get_next_step()
    assert step2 is not None
    assert step2.id == "STEP-02"

    planner.mark_step_skipped("STEP-02", reason="Not required by operator")
    assert step2.status == PlanStepStatus.SKIPPED

    coverage_2 = planner.calculate_coverage()
    assert coverage_2 > coverage_1
