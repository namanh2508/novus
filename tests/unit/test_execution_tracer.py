from agentic_pentest.domain.telemetry.tracer import (
    CostEstimator,
    ExecutionTracer,
    SpanStatus,
    SpanType,
)


def test_cost_estimator() -> None:
    # Claude 3.5 Sonnet: $3 / 1M prompt, $15 / 1M completion
    cost = CostEstimator.estimate(
        "claude-3-5-sonnet", prompt_tokens=10_000, completion_tokens=2_000
    )
    # 0.03 + 0.03 = 0.06
    assert cost == 0.06

    # Ollama is free ($0.0)
    cost_local = CostEstimator.estimate(
        "ollama/llama3", prompt_tokens=50_000, completion_tokens=10_000
    )
    assert cost_local == 0.0


def test_execution_tracer_lifecycle_and_budget() -> None:
    tracer = ExecutionTracer(max_cost_budget_usd=0.10)

    span = tracer.start_span(
        "planning_step_1", SpanType.PLANNING, attributes={"agent": "JevPlanner"}
    )
    assert span.span_id.startswith("span_")
    assert span.status == SpanStatus.OK

    finished = tracer.finish_span(
        span.span_id,
        status=SpanStatus.OK,
        prompt_tokens=5_000,
        completion_tokens=1_000,
        model_name="claude-3-5-sonnet",
    )
    assert finished is not None
    assert finished.duration_ms >= 0.0
    assert finished.estimated_cost_usd > 0.0

    assert tracer.get_total_tokens() == 6_000
    assert tracer.is_budget_exceeded() is False

    traces = tracer.export_traces()
    assert len(traces) == 1
    assert traces[0]["name"] == "planning_step_1"
    assert traces[0]["type"] == "PLANNING"
