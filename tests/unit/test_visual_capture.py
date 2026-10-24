from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentic_pentest.application.orchestration.autonomous_orchestrator import (
    AutonomousAttackOrchestrator,
)
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
from agentic_pentest.infrastructure.discovery.playwright_crawler import PlaywrightDynamicCrawler


@pytest.fixture
def dummy_finding() -> Finding:
    obs_req = HTTPRequestObservation(
        url="http://127.0.0.1:8888/identity/api/v2/vehicle/v1/location",
        method=HTTPMethod.GET,
        headers={"Authorization": "Bearer bob_token"},
        body=None,
    )
    obs_resp = HTTPResponseObservation(
        status_code=200,
        headers={"content-type": "application/json"},
        body='{"latitude": 10.0, "longitude": 20.0}',
        latency_ms=15,
        body_sha256="abc123sha",
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(obs_req, obs_resp),
        cross_principal_test=(obs_req, obs_resp),
        unauthenticated_control=(obs_req, obs_resp),
    )
    return Finding(
        id="FINDING-TEST-BOLA",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA Location Leak",
        endpoint_url="http://127.0.0.1:8888/identity/api/v2/vehicle/v1/location",
        method=HTTPMethod.GET,
        target_object=TargetObject(
            id="obj_v1",
            type_name="vehicle",
            owner_principal_id="alice",
            value="v1",
        ),
        attacker_principal=Principal(id="bob", name="Bob", role=Role.USER, jwt_token="bob_jwt"),
        triplet=triplet,
        verification_proof="Cross-tenant access verified without authorization check.",
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_playwright_capture_screenshot_fallback():
    crawler = PlaywrightDynamicCrawler()
    # If URL is invalid or playwright cannot launch in sandboxed mock, should return False gracefully
    res = await crawler.capture_screenshot(
        "invalid-url", "reports/pocs/test_dummy.png", timeout_ms=500
    )
    assert res is False


@pytest.mark.asyncio
async def test_orchestrator_try_capture_visual_proof_success(dummy_finding, tmp_path):
    mock_crawler = MagicMock()

    async def mock_capture(target_url, output_path, headers=None, timeout_ms=15000):
        # Create the file to simulate successful screenshot
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x89PNG\r\n\x1a\nfake_image_bytes")
        return True

    mock_crawler.capture_screenshot = AsyncMock(side_effect=mock_capture)

    mock_registry = MagicMock()
    mock_executor = MagicMock()
    orchestrator = AutonomousAttackOrchestrator(
        tool_registry=mock_registry,
        executor=mock_executor,
        visual_crawler=mock_crawler,
    )

    shot = await orchestrator._try_capture_visual_proof(dummy_finding)
    assert shot is not None
    assert shot.exists()
    assert shot.name == "evidence_finding_test_bola.png"
    mock_crawler.capture_screenshot.assert_called_once()
    assert (
        mock_crawler.capture_screenshot.call_args[1]["headers"]["Authorization"] == "Bearer bob_jwt"
    )

    # Clean up test file
    if shot.exists():
        shot.unlink()
