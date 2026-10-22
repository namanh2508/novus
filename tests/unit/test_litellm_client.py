"""Unit tests for LiteLLM reasoning client and JSON extraction."""

import pytest

from agentic_pentest.infrastructure.reasoning.litellm_client import LiteLLMClient


@pytest.mark.asyncio
async def test_offline_fallback_plan() -> None:
    client = LiteLLMClient(fallback_offline=True)
    plan = await client.generate_structured_plan(
        system_prompt="System instructions",
        user_prompt="Target objects",
    )
    assert "actions" in plan
    assert len(plan["actions"]) >= 1
    assert plan["actions"][0]["action_type"] == "VERIFY_BOLA"


def test_extract_json_from_markdown_fences() -> None:
    client = LiteLLMClient()
    raw = """
    Here is your testing plan:
    ```json
    {
        "status": "READY",
        "actions": [{"id": 1, "type": "PROBE"}]
    }
    ```
    Good luck!
    """
    extracted = client._extract_json_from_text(raw)
    assert extracted["status"] == "READY"
    assert len(extracted["actions"]) == 1
