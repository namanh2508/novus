import pytest

from agentic_pentest.application.orchestration.attack_chain import (
    AttackChainOrchestrator,
    AttackChainStage,
    StageTransitionError,
)


def test_attack_chain_happy_path() -> None:
    orchestrator = AttackChainOrchestrator(target_url="http://localhost:8888")
    assert orchestrator.current_stage == AttackChainStage.RECONNAISSANCE

    # Advance through stages
    r1 = orchestrator.transition_to(AttackChainStage.SURFACE_MAPPING, {"endpoints_found": 15})
    assert r1.to_stage == AttackChainStage.SURFACE_MAPPING
    assert orchestrator.current_stage == AttackChainStage.SURFACE_MAPPING

    r2 = orchestrator.transition_to(AttackChainStage.HYPOTHESIS_EXPLORATION)
    assert r2.to_stage == AttackChainStage.HYPOTHESIS_EXPLORATION

    r3 = orchestrator.transition_to(AttackChainStage.DIFFERENTIAL_VERIFICATION)
    assert r3.to_stage == AttackChainStage.DIFFERENTIAL_VERIFICATION

    r4 = orchestrator.transition_to(AttackChainStage.CONSENSUS_ADJUDICATION)
    assert r4.to_stage == AttackChainStage.CONSENSUS_ADJUDICATION

    r5 = orchestrator.transition_to(AttackChainStage.REMEDIATION_AND_ROLLBACK)
    assert r5.to_stage == AttackChainStage.REMEDIATION_AND_ROLLBACK

    r6 = orchestrator.transition_to(AttackChainStage.COMPLETED)
    assert r6.to_stage == AttackChainStage.COMPLETED
    assert orchestrator.is_completed() is True

    summary = orchestrator.get_lifecycle_summary()
    assert summary["total_transitions"] == 6
    assert summary["is_completed"] is True


def test_attack_chain_illegal_transition_rejection() -> None:
    orchestrator = AttackChainOrchestrator(target_url="http://localhost:8888")

    # Cannot skip directly from RECONNAISSANCE to REMEDIATION_AND_ROLLBACK
    with pytest.raises(StageTransitionError):
        orchestrator.transition_to(AttackChainStage.REMEDIATION_AND_ROLLBACK)

    # Valid transition to SURFACE_MAPPING
    orchestrator.transition_to(AttackChainStage.SURFACE_MAPPING)

    # Cannot skip to COMPLETED
    with pytest.raises(StageTransitionError):
        orchestrator.transition_to(AttackChainStage.COMPLETED)
