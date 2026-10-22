"""Unit tests for SQLite immutable audit store."""

from datetime import UTC, datetime

from agentic_pentest.infrastructure.storage.sqlite_audit_store import SQLiteAuditStore

from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
)


def test_record_and_retrieve_audit_trail(tmp_path: object) -> None:
    db_file = str(tmp_path) + "/audit.db"
    store = SQLiteAuditStore(db_path=db_file)

    now = datetime.now(UTC)
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={"Authorization": "Bearer token"},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"lat": 10.1}',
        latency_ms=25,
        body_sha256="sha256_mock_hash",
        timestamp=now,
    )

    row_id = store.record_observation(session_id="sess_001", request=req, response=resp)
    assert row_id >= 1

    records = store.get_session_observations("sess_001")
    assert len(records) == 1
    retrieved_req, retrieved_resp = records[0]
    assert retrieved_req.url == req.url
    assert retrieved_resp.status_code == 200
    assert retrieved_resp.body_sha256 == "sha256_mock_hash"
