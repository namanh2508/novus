"""Unit tests for SASTBridgeRouteExtractor."""

from __future__ import annotations

import tempfile
from pathlib import Path

from agentic_pentest.domain.entities import HTTPMethod
from agentic_pentest.infrastructure.discovery.sast_bridge import (
    SASTBridgeRouteExtractor,
)
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


def test_sast_bridge_extracts_routes_and_flags_missing_auth() -> None:
    sample_code = """
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/public/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok"})

@app.route('/identity/api/v2/vehicle/<id>/location', methods=['GET'])
def get_vehicle_location(id):
    # Missing @login_required or auth check!
    return jsonify({"carId": id, "lat": 10.0})

@app.route('/community/api/v2/coupon/new-coupon', methods=['POST'])
@login_required
def create_coupon():
    return jsonify({"coupon": "DISCOUNT"})
"""

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(sample_code)
        f_path = f.name

    try:
        extractor = SASTBridgeRouteExtractor()
        findings = extractor.scan_file(f_path)

        assert len(findings) == 3

        # Check unprotected sensitive vehicle endpoint
        vehicle_finding = next(f for f in findings if "vehicle" in f.path)
        assert vehicle_finding.is_protected is False
        assert vehicle_finding.potential_risk == "HIGH_BFLA_BOLA_CANDIDATE"
        assert HTTPMethod.GET in vehicle_finding.methods

        # Check protected coupon endpoint
        coupon_finding = next(f for f in findings if "coupon" in f.path)
        assert coupon_finding.is_protected is True
        assert HTTPMethod.POST in coupon_finding.methods

        # Test populating graph
        graph = NetworkXEvidenceGraph()
        count = extractor.populate_evidence_graph(graph, findings)
        assert count == 3
        assert graph.node_count() >= 3
    finally:
        Path(f_path).unlink(missing_ok=True)
