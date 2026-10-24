"""Unit tests for Dynamic Proxy Rotator and IP Reputation Checker (Phase 3)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentic_pentest.application.use_cases.tool_registry import ProxyRotatorTool
from agentic_pentest.infrastructure.proxy.ip_reputation import IPReputationChecker
from agentic_pentest.infrastructure.proxy.proxy_rotator import (
    ProxyNode,
    ProxyRotator,
    ProxyStrategy,
)


def test_proxy_node_defaults() -> None:
    node = ProxyNode(url="http://10.0.0.1:8080")
    assert node.health_score == 1.0
    assert node.is_active is True
    assert node.consecutive_failures == 0


def test_proxy_rotator_add_and_strategies() -> None:
    rotator = ProxyRotator(initial_proxies=["http://proxy1:8080", "socks5://proxy2:1080"])
    active = rotator.get_active_nodes()
    assert len(active) == 2
    assert active[1].protocol == "socks5"

    # Test round robin
    node_a = rotator.select_proxy(ProxyStrategy.ROUND_ROBIN)
    node_b = rotator.select_proxy(ProxyStrategy.ROUND_ROBIN)
    assert node_a is not None and node_b is not None
    assert node_a.url != node_b.url

    # Test fastest
    node_a.latency_ms = 10.0
    node_b.latency_ms = 100.0
    fastest = rotator.select_proxy(ProxyStrategy.FASTEST)
    assert fastest is not None
    assert fastest.url == node_a.url

    # Test health weighted
    node_a.health_score = 0.9
    node_b.health_score = 0.1
    chosen = rotator.select_proxy(ProxyStrategy.HEALTH_WEIGHTED)
    assert chosen is not None


def test_proxy_rotator_health_degradation_and_quarantine() -> None:
    rotator = ProxyRotator(initial_proxies=["http://fragile:8080"], max_consecutive_failures=2)
    node = rotator.get_active_nodes()[0]
    assert node.is_active is True

    # 1st failure
    rotator.record_outcome("http://fragile:8080", success=False)
    assert node.consecutive_failures == 1
    assert node.health_score == 0.75
    assert node.is_active is True

    # 2nd failure -> exceeds max_consecutive_failures -> deactivated
    rotator.record_outcome("http://fragile:8080", success=False)
    assert node.consecutive_failures == 2
    assert node.health_score == 0.5
    assert node.is_active is False
    assert len(rotator.get_active_nodes()) == 0

    # Pool status
    status = rotator.get_pool_status()
    assert status["total_nodes"] == 1
    assert status["active_nodes"] == 0
    assert status["healthy_ratio"] == 0.0


def test_proxy_rotator_success_recovery() -> None:
    rotator = ProxyRotator(initial_proxies=["http://recover:8080"])
    rotator.record_outcome("http://recover:8080", success=False)
    # Recover
    rotator.record_outcome("http://recover:8080", success=True, latency_ms=45.0)
    node = rotator.get_active_nodes()[0]
    assert node.consecutive_failures == 0
    assert node.health_score > 0.75


@pytest.mark.asyncio
async def test_ip_reputation_checker_mock() -> None:
    checker = IPReputationChecker()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ip": "198.51.100.5"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        res = await checker.check_egress_ip(
            proxy_url="http://198.51.100.5:8080",
            expected_different_from="203.0.113.1",
        )
        assert res["status"] == "success"
        assert res["egress_ip"] == "198.51.100.5"
        assert res["is_anonymized"] is True
        assert res["leak_detected"] is False

        # Test origin leak detection
        res_leaked = await checker.check_egress_ip(
            proxy_url="http://198.51.100.5:8080",
            expected_different_from="198.51.100.5",
        )
        assert res_leaked["is_anonymized"] is False
        assert res_leaked["leak_detected"] is True


@pytest.mark.asyncio
async def test_proxy_rotator_tool_execution() -> None:
    tool = ProxyRotatorTool()
    assert tool.metadata.name == "rotate_proxy_node"

    # Add proxy
    add_res = await tool.execute(action="add", proxy_url="socks5://127.0.0.1:9050")
    assert add_res["status"] == "added"
    assert add_res["protocol"] == "socks5"

    # Select proxy
    sel_res = await tool.execute(action="select", strategy="round_robin")
    assert sel_res["status"] == "selected"
    assert sel_res["proxy_url"] == "socks5://127.0.0.1:9050"

    # Record outcome
    rec_res = await tool.execute(
        action="record_outcome",
        proxy_url="socks5://127.0.0.1:9050",
        success=True,
        latency_ms=25.0,
    )
    assert rec_res["status"] == "updated"

    # Status
    status_res = await tool.execute(action="status")
    assert status_res["total_nodes"] >= 1
