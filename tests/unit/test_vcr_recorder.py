"""Unit tests for Offline VCR / HAR Cassette Recorder & Replay Executor."""

import tempfile
from pathlib import Path

import pytest

from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
)
from agentic_pentest.infrastructure.executors.vcr_recorder import (
    CassetteReplayExecutor,
    VCRHttpRecorder,
)


@pytest.mark.asyncio
async def test_vcr_record_and_replay_cycle() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        recorder = VCRHttpRecorder(cassette_dir=tmp_dir)

        req1 = HTTPRequestObservation(
            method=HTTPMethod.GET,
            url="http://target.lab:8888/identity/api/v2/vehicle/location",
            headers={"Accept": "application/json"},
            body=None,
        )
        resp1 = HTTPResponseObservation(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"latitude": 10.76, "longitude": 106.66}',
            latency_ms=18,
            body_sha256="hash1",
        )
        recorder.record(req1, resp1)

        cassette_path = recorder.save_cassette("test_crapi_cassette")
        assert Path(cassette_path).exists()

        # Replay offline via CassetteReplayExecutor
        replay_executor = CassetteReplayExecutor(cassette_path)
        req_out, resp_out = await replay_executor.execute_request(
            method="GET",
            url="http://any-offline-host:8888/identity/api/v2/vehicle/location",
        )

        assert resp_out.status_code == 200
        assert "10.76" in resp_out.body
        assert resp_out.latency_ms == 18
