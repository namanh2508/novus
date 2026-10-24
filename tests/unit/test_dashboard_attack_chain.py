import pytest
from aiohttp.test_utils import AioHTTPTestCase

from agentic_pentest.infrastructure.proxy.interception_dashboard import (
    InterceptionProxyDashboard,
    get_live_attack_chain,
    update_live_attack_chain,
)


@pytest.mark.asyncio
async def test_live_attack_chain_getter_setter():
    sample_plan = {
        "chain_id": "test_chain_123",
        "user_objective": "Test IDOR Audit",
        "nodes": [
            {
                "node_id": "STEP-01",
                "phase": "RECON",
                "tool_name": "audit_headers",
                "status": "COMPLETED",
                "findings_count": 0,
            }
        ],
    }
    update_live_attack_chain(sample_plan)
    assert get_live_attack_chain() == sample_plan


class TestDashboardAttackChainAPI(AioHTTPTestCase):
    async def get_application(self):
        dashboard = InterceptionProxyDashboard(host="127.0.0.1", port=8091)
        return dashboard._app

    async def test_get_attack_chain_endpoint(self):
        update_live_attack_chain({"chain_id": "api_test", "total_nodes": 1})
        resp = await self.client.request("GET", "/api/attack_chain")
        assert resp.status == 200
        data = await resp.json()
        assert data.get("chain_id") == "api_test"

    async def test_post_attack_chain_endpoint(self):
        new_plan = {"chain_id": "posted_chain", "nodes": []}
        resp = await self.client.request("POST", "/api/attack_chain", json=new_plan)
        assert resp.status == 200
        data = await resp.json()
        assert data.get("status") == "updated"
        assert get_live_attack_chain() == new_plan
