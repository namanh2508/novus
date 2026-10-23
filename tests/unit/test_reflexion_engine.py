"""Unit tests for Self-Improving Closed-Loop Reflexion Engine."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from agentic_pentest.application.use_cases.memory_manager import MemoryManager
from agentic_pentest.application.use_cases.reflexion_engine import SelfImprovingReflexionEngine
from agentic_pentest.domain.entities import (
    DifferentialTriplet,
    Finding,
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
    Severity,
    TargetObject,
    VulnerabilityCategory,
)
from agentic_pentest.infrastructure.storage.episodic_knowledge import EpisodicKnowledgeBase


def test_reflexion_engine_closed_loop(tmp_path: os.PathLike[str]) -> None:
    mem_file = os.path.join(tmp_path, "MEMORY.md")
    db_file = os.path.join(tmp_path, "test_episodic.db")

    mem_mgr = MemoryManager(target_url="http://test.local", memory_file=mem_file)
    kb = EpisodicKnowledgeBase(db_path=db_file)
    engine = SelfImprovingReflexionEngine(memory_manager=mem_mgr, episodic_kb=kb)

    obj = TargetObject(id="v1", type_name="vehicle", owner_principal_id="alice", value="v1")
    attacker = Principal(id="bob", name="Bob", role=Role.USER)
    now = datetime.now(UTC)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://test.local/api/v2/vehicle/{id}/location",
        headers={},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200, headers={}, body="{}", latency_ms=10, body_sha256="sha", timestamp=now
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )

    finding = Finding(
        id="FIND-1",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA on vehicle location",
        endpoint_url="http://test.local/api/v2/vehicle/{id}/location",
        method=HTTPMethod.GET,
        target_object=obj,
        attacker_principal=attacker,
        triplet=triplet,
        verification_proof="Cross-tenant vehicle object accessed without authorization",
        created_at=now,
    )

    rule = engine.reflect_on_finding(finding, framework="crapi")
    assert "BOLA Invariant" in rule
    assert "/api/v2/vehicle/{id}/location" in rule

    # Verify physical file written
    assert os.path.exists(mem_file)
    with open(mem_file, encoding="utf-8") as f:
        content = f.read()
    assert "Learned Offensive Invariants" in content
    assert "BOLA Invariant" in content

    # Verify SQLite Episodic KB
    learnings = engine.retrieve_prior_intuitions("crapi")
    assert len(learnings) == 1
    assert learnings[0]["category"] == "BOLA"

    # Test defense bypass reflection
    bypass_rule = engine.reflect_on_mitigation_bypass(
        endpoint="/api/orders",
        blocked_mutation="standard payload",
        bypassing_mutation="unicode normalization",
        framework="crapi",
    )
    assert "unicode normalization" in bypass_rule
    kb.close()
