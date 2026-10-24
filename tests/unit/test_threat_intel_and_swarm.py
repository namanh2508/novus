"""Unit tests for Phase 6: Threat Intel, OpenAPI Reconstructor, and Multi-Target Swarm."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentic_pentest.application.orchestration.swarm_orchestrator import (
    SwarmAuditResult,
    SwarmAuditTarget,
    SwarmOrchestrator,
)
from agentic_pentest.infrastructure.discovery.openapi_reconstructor import OpenAPIReconstructor
from agentic_pentest.infrastructure.discovery.threat_intel_bridge import ThreatIntelBridge
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


def test_openapi_reconstructor_generates_spec() -> None:
    reconstructor = OpenAPIReconstructor(title="Test Reconstructed crAPI", version="1.0.0")

    # Record GET with parameterized path
    reconstructor.record_interaction(
        method="GET",
        url="http://localhost:8888/identity/api/v2/vehicle/101/location",
        status_code=200,
        resp_body='{"lat": 37.77, "lng": -122.41, "active": true}',
    )

    # Record POST with body
    reconstructor.record_interaction(
        method="POST",
        url="http://localhost:8888/identity/api/v2/vehicle/101/reset",
        status_code=200,
        req_body='{"pin": 1234, "note": "mechanic reset"}',
        resp_body='{"status": "success"}',
    )

    spec_dict = reconstructor.to_dict()
    assert spec_dict["openapi"] == "3.0.3"
    assert spec_dict["info"]["title"] == "Test Reconstructed crAPI"

    # Verify path was parameterized
    assert "/identity/api/v2/vehicle/{id}/location" in spec_dict["paths"]
    loc_op = spec_dict["paths"]["/identity/api/v2/vehicle/{id}/location"]["get"]
    assert loc_op["parameters"][0]["name"] == "id"
    assert loc_op["parameters"][0]["in"] == "path"

    # Verify YAML serialization
    yaml_text = reconstructor.to_yaml()
    assert "openapi: 3.0.3" in yaml_text
    assert "/identity/api/v2/vehicle/{id}/location" in yaml_text


def test_threat_intel_bridge_mock_assets() -> None:
    bridge = ThreatIntelBridge()
    raw_data = [
        {
            "ip": "1.2.3.4",
            "port": 443,
            "protocol": "https",
            "domain": "api.example.com",
            "title": "Portal",
        },
        {
            "ip": "5.6.7.8",
            "port": 8080,
            "protocol": "http",
            "domain": "dev.example.com",
            "title": "Dev API",
        },
    ]
    assets = bridge.parse_mock_asset_data(raw_data, source="quake")
    assert len(assets) == 2
    assert assets[0].ip == "1.2.3.4"
    assert assets[0].port == 443
    assert assets[1].source == "quake"


@pytest.mark.asyncio
async def test_threat_intel_bridge_fofa_query() -> None:
    bridge = ThreatIntelBridge(fofa_email="test@sec.org", fofa_key="dummy_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            ["198.51.100.1", "443", "https", "crapi.target.org", "crAPI Home", "nginx", "US"]
        ]
    }

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        assets = await bridge.query_fofa('domain="crapi.target.org"')
        assert len(assets) == 1
        assert assets[0].ip == "198.51.100.1"
        assert assets[0].server_banner == "nginx"


@pytest.mark.asyncio
async def test_swarm_orchestrator_concurrent_ten_endpoints() -> None:
    graph = NetworkXEvidenceGraph()
    orchestrator = SwarmOrchestrator(evidence_graph=graph, max_concurrency=3)

    targets = [
        SwarmAuditTarget(endpoint_path=f"/api/v1/resource_{i}", method="GET") for i in range(10)
    ]

    active_concurrency = 0
    max_observed_concurrency = 0

    async def mock_audit(target: SwarmAuditTarget) -> SwarmAuditResult:
        nonlocal active_concurrency, max_observed_concurrency
        active_concurrency += 1
        if active_concurrency > max_observed_concurrency:
            max_observed_concurrency = active_concurrency

        await asyncio.sleep(0.01)

        active_concurrency -= 1
        return SwarmAuditResult(
            target=target,
            status="clean",
            is_vulnerable=False,
            details="Audit completed cleanly",
        )

    results = await orchestrator.run_swarm_campaign(targets, mock_audit)

    assert len(results) == 10
    assert all(r.status == "clean" for r in results)
    # Ensure concurrency was bounded by semaphore <= 3
    assert max_observed_concurrency <= 3

    # Ensure all 10 endpoints were recorded in the Evidence Graph without race conditions
    for i in range(10):
        node_id = f"endpoint:GET:/api/v1/resource_{i}"
        assert node_id in graph.graph
