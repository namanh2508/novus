"""Unit tests for SAST-to-DAST Hybrid Reconciliation Engine."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_pentest.application.orchestration.sast_reconciliation import (
    SASTReconciliationEngine,
)


def test_sast_reconciliation_detects_unprotected_and_parameterized_routes() -> None:
    sample_code = """
from flask import Flask, request

app = Flask(__name__)

@app.route("/api/v1/user/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    return {"user": user_id}

@app.route("/api/v1/admin/promote", methods=["POST"])
def promote_user():
    return {"status": "promoted"}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "app.py"
        test_file.write_text(sample_code, encoding="utf-8")

        engine = SASTReconciliationEngine()
        routes = engine.analyze_source_tree(tmpdir)

        assert len(routes) >= 2
        paths = [r.path for r in routes]
        assert "/api/v1/user/<user_id>" in paths or any("user" in p for p in paths)
        assert "/api/v1/admin/promote" in paths

        nodes = engine.generate_reconciled_nodes(routes, "http://test.local", start_step_idx=10)
        assert len(nodes) >= 2
        assert any(n["tool_name"] == "verify_bfla" for n in nodes)
        assert any("TARGETED CODE-AWARE EXPLOITATION" in n["phase"] for n in nodes)
