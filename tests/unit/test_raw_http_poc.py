from datetime import UTC, datetime

from agentic_pentest.application.use_cases.generate_poc import PoCGenerator
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


def test_raw_http_poc_generation() -> None:
    req_obs = HTTPRequestObservation(
        method=HTTPMethod.POST,
        url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        headers={"Content-Type": "application/json"},
        body='{"coupon_code": "DISCOUNT50"}',
    )
    resp_obs = HTTPResponseObservation(
        status_code=200,
        headers={},
        body='{"status": "ok"}',
        latency_ms=45,
        body_sha256="abc",
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req_obs, resp_obs),
        cross_principal_test=(req_obs, resp_obs),
        unauthenticated_control=(req_obs, resp_obs),
    )
    finding = Finding(
        id="FIND-TEST-01",
        category=VulnerabilityCategory.BFLA,
        severity=Severity.HIGH,
        title="Admin Coupon Function Exposed",
        endpoint_url="http://localhost:8888/community/api/v2/coupon/new-coupon",
        method=HTTPMethod.POST,
        target_object=TargetObject(
            id="coupon_1", type_name="coupon", owner_principal_id="admin_1", value="DISCOUNT50"
        ),
        attacker_principal=Principal(
            id="bob", name="Bob", role=Role.USER, jwt_token="token_bob_sample"
        ),
        triplet=triplet,
        verification_proof="Role hierarchy invariant broken",
        created_at=datetime.now(UTC),
    )

    gen = PoCGenerator()
    raw_http = gen.generate_raw_http_poc(finding)

    assert "POST /community/api/v2/coupon/new-coupon HTTP/1.1" in raw_http
    assert "Host: localhost:8888" in raw_http
    assert "Authorization: Bearer token_bob_sample" in raw_http
    assert "Content-Length: " in raw_http
    assert '{"coupon_code": "DISCOUNT50"}' in raw_http

    all_pocs = gen.generate_all_pocs(finding)
    assert "raw_http" in all_pocs
    assert "python" in all_pocs
    assert "curl" in all_pocs
