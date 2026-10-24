from agentic_pentest.application.orchestration.anti_loop_reflexion import (
    LoopSeverity,
    ReflexionState,
)


def test_reflexion_detects_consecutive_failures() -> None:
    state = ReflexionState(max_consecutive_failures=3)
    # 1st failure
    sev1 = state.record_trace("verify_bola", "/api/v1/user", 403, "Forbidden", False)
    assert sev1 == LoopSeverity.NONE

    # 2nd failure
    sev2 = state.record_trace("verify_bola", "/api/v1/user", 403, "Forbidden", False)
    assert sev2 == LoopSeverity.WARNING

    # 3rd failure
    sev3 = state.record_trace("verify_bola", "/api/v1/user", 403, "Forbidden", False)
    assert sev3 == LoopSeverity.STUCK
    assert len(state.backtrack_reasons) > 0


def test_reflexion_detects_ping_pong_oscillation() -> None:
    state = ReflexionState()
    # Ping-pong between tool A and tool B
    state.record_trace("tool_A", "/api/v1", 400, "err", False)
    state.record_trace("tool_B", "/api/v2", 400, "err", False)
    state.record_trace("tool_A", "/api/v1", 400, "err", False)
    sev = state.record_trace("tool_B", "/api/v2", 400, "err", False)
    assert sev == LoopSeverity.STUCK
    assert any("ping-pong" in r.lower() for r in state.backtrack_reasons)


def test_reflexion_suggest_pivot() -> None:
    state = ReflexionState()
    pivot_bola = state.suggest_pivot("verify_bola", "/api/v1/user")
    assert "BFLA" in pivot_bola or "Mass Assignment" in pivot_bola

    pivot_jwt = state.suggest_pivot("audit_jwt", "/api/v1/auth")
    assert "JKU" in pivot_jwt or "Header" in pivot_jwt
