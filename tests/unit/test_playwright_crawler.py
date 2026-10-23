"""Unit tests for PlaywrightDynamicCrawler."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
)
from agentic_pentest.infrastructure.discovery.playwright_crawler import (
    PlaywrightDynamicCrawler,
)


@pytest.mark.asyncio
async def test_playwright_crawler_fallback_without_browser() -> None:
    """Test graceful fallback to SPADynamicCrawler when Playwright browser is unavailable."""
    mock_executor = AsyncMock(spec=IHTTPExecutor)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://test-app.local",
        headers={},
        body="",
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"content-type": "text/html"},
        body="<html><script src='/bundle.js'></script></html>",
        latency_ms=10,
        body_sha256="abc",
    )
    mock_executor.execute_request.return_value = (req, resp)

    crawler = PlaywrightDynamicCrawler(fallback_executor=mock_executor)
    res = await crawler.crawl_deep("http://test-app.local")

    assert res.target_url == "http://test-app.local"
    assert isinstance(res.discovered_endpoints, list)
