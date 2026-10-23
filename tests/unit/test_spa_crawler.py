"""Unit tests for SPADynamicCrawler."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
)
from agentic_pentest.infrastructure.discovery.spa_crawler import SPADynamicCrawler
from agentic_pentest.infrastructure.storage.networkx_graph import NetworkXEvidenceGraph


@pytest.mark.asyncio
async def test_spa_crawler_extracts_endpoints_from_html_and_js() -> None:
    executor = AsyncMock()

    html_payload = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SPA Dashboard</title>
        <script src="/static/js/main.chunk.js"></script>
    </head>
    <body>
        <script>
            fetch('/identity/api/v2/user/dashboard');
        </script>
    </body>
    </html>
    """

    js_chunk = """
    function getVehicle(carId) {
        return axios.get('/identity/api/v2/vehicle/' + carId + '/location');
    }
    function deleteOrder(orderId) {
        return fetch('/workshop/api/merchant/order/' + orderId, { method: 'DELETE' });
    }
    """

    def mock_execute_request(
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Any = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        req = HTTPRequestObservation(
            method=HTTPMethod.GET, url=url, headers=headers or {}, body=None
        )
        if url == "http://localhost:8888":
            resp = HTTPResponseObservation(
                status_code=200, headers={}, body=html_payload, latency_ms=10, body_sha256="h1"
            )
        elif "/static/js/main.chunk.js" in url:
            resp = HTTPResponseObservation(
                status_code=200, headers={}, body=js_chunk, latency_ms=10, body_sha256="h2"
            )
        else:
            resp = HTTPResponseObservation(
                status_code=404, headers={}, body="", latency_ms=5, body_sha256="h3"
            )
        return req, resp

    executor.execute_request.side_effect = mock_execute_request

    crawler = SPADynamicCrawler(executor)
    endpoints = await crawler.crawl("http://localhost:8888")

    assert len(endpoints) >= 2
    paths = [ep.path for ep in endpoints]
    assert any("identity/api/v2/user/dashboard" in p for p in paths)
    assert any("identity/api/v2/vehicle/" in p for p in paths)

    # Test populating Evidence Graph
    graph = NetworkXEvidenceGraph()
    count = crawler.populate_evidence_graph(graph, endpoints)
    assert count >= 2
    assert graph.node_count() >= 2
