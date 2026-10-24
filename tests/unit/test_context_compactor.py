"""Unit tests for Phase 5: Lossless Context Compactor, SQLite WAL & autoDream."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from agentic_pentest.application.orchestration.background_dreamer import BackgroundDreamer
from agentic_pentest.application.orchestration.context_compactor import ContextCompactor
from agentic_pentest.domain.entities import (
    AgentTurn,
    Finding,
    HTTPMethod,
    Principal,
    Role,
    Severity,
    TargetObject,
    VulnerabilityCategory,
)
from agentic_pentest.infrastructure.storage.episodic_knowledge import EpisodicKnowledgeBase
from agentic_pentest.infrastructure.storage.sqlite_audit_store import SQLiteAuditStore
from agentic_pentest.infrastructure.storage.sqlite_session_store import SQLiteSessionStore


def test_compact_tool_output() -> None:
    compactor = ContextCompactor(max_body_preview_len=50)

    # Short string
    assert compactor.compact_tool_output("short output") == "short output"

    # Verbose JSON dict
    json_dict = json.dumps(
        {"user": "alice", "roles": ["admin"], "sensitive_data": "x" * 200, "status": "active"}
    )
    c_dict = compactor.compact_tool_output(json_dict)
    assert "[JSON dict keys=" in c_dict
    assert "sha256=" in c_dict

    # Verbose JSON list
    json_list = json.dumps([{"id": i, "name": f"item_{i}_with_long_details"} for i in range(10)])
    c_list = compactor.compact_tool_output(json_list)
    assert "[JSON list count=10" in c_list

    # HTML
    html_text = (
        "<html><head><title>Dashboard</title></head><body>Welcome Admin! "
        + "A" * 100
        + "</body></html>"
    )
    c_html = compactor.compact_tool_output(html_text)
    assert "[Raw text title='Dashboard'" in c_html


def test_compact_turns() -> None:
    compactor = ContextCompactor(max_uncompacted_turns=2)

    turns = [
        AgentTurn(
            turn_number=1,
            thought="Exploring http://target.local/api/v1/users",
            tool_name="crawl_endpoints",
            tool_arguments={},
            observation_summary='{"status": "ok", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-ID", "data": "huge '
            + "d" * 300
            + '"}',
            is_success=True,
        ),
        AgentTurn(
            turn_number=2,
            thought="Testing http://target.local/api/v1/orders",
            tool_name="verify_bola",
            tool_arguments={},
            observation_summary="Order details " + "o" * 200,
            is_success=True,
        ),
        AgentTurn(
            turn_number=3,
            thought="Active testing turn 3",
            tool_name="audit_headers",
            tool_arguments={},
            observation_summary="Headers ok",
            is_success=True,
        ),
    ]

    snapshot, retained = compactor.compact_turns(turns)
    assert snapshot.total_turns_processed == 3
    assert snapshot.compacted_turn_count == 1
    assert snapshot.retained_turn_count == 2
    assert len(retained) == 2
    assert retained[0].turn_number == 2
    assert retained[1].turn_number == 3
    assert any("http://target.local/api/v1/users" in ep for ep in snapshot.discovered_endpoints)
    assert len(snapshot.active_tokens) >= 1


def test_background_dreamer(tmp_path: Path) -> None:
    db_file = tmp_path / "dream.db"
    kb = EpisodicKnowledgeBase(db_path=str(db_file))
    dreamer = BackgroundDreamer(knowledge_base=kb)

    now = datetime.now(UTC)
    alice = Principal(id="u1", name="Alice", role=Role.USER)
    target_obj = TargetObject(id="o1", type_name="vehicle", owner_principal_id="u2", value="101")
    finding = Finding(
        id="FINDING-01",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA in vehicle tracking",
        endpoint_url="http://target.local/api/v2/vehicles/101",
        method=HTTPMethod.GET,
        target_object=target_obj,
        attacker_principal=alice,
        triplet=None,
        verification_proof="Cross-tenant access succeeded with 200 OK",
        created_at=now,
    )

    res = dreamer.dream(
        target_host="target.local",
        target_framework="Express",
        findings=[finding],
        observed_urls=["http://target.local/api/v2/vehicles/101"],
    )

    assert res["status"] == "completed"
    assert res["heuristics_consolidated"] == 1

    # Query back from KB
    learnings = kb.query_learnings(framework="Express")
    assert len(learnings) >= 1
    assert "vulnerable to BOLA" in learnings[0]["heuristic_insight"]


def test_sqlite_wal_mode_active(tmp_path: Path) -> None:
    db1 = tmp_path / "audit.db"
    audit_store = SQLiteAuditStore(db_path=str(db1))
    mode1 = audit_store._connection.execute("PRAGMA journal_mode;").fetchone()[0]
    assert str(mode1).lower() == "wal"

    db2 = tmp_path / "episodic.db"
    kb = EpisodicKnowledgeBase(db_path=str(db2))
    mode2 = kb._connection.execute("PRAGMA journal_mode;").fetchone()[0]
    assert str(mode2).lower() == "wal"

    db3 = tmp_path / "sessions.db"
    session_store = SQLiteSessionStore(db_path=str(db3))
    mode3 = session_store._connection.execute("PRAGMA journal_mode;").fetchone()[0]
    assert str(mode3).lower() == "wal"
