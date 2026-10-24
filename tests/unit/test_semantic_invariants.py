from agentic_pentest.domain.invariants import (
    check_bfla_invariant,
    check_bola_invariant,
    check_jwt_key_confusion_invariant,
    check_race_condition_toctou_invariant,
    check_ssrf_metadata_invariant,
    is_semantic_error_response,
)


def test_is_semantic_error_response_json() -> None:
    # 200 OK with explicit error in JSON
    body1 = '{"status": "error", "message": "unauthorized access to object"}'
    assert is_semantic_error_response(200, body1) is True

    # 200 OK with success: false
    body2 = '{"success": false, "error": "Permission denied"}'
    assert is_semantic_error_response(200, body2) is True

    # 200 OK with genuine data
    body3 = '{"id": "v1", "owner": "alice", "latitude": 10.0}'
    assert is_semantic_error_response(200, body3) is False


def test_is_semantic_error_response_html() -> None:
    body_html = "<html><head><title>Access Denied</title></head><body>Forbidden</body></html>"
    assert is_semantic_error_response(200, body_html) is True


def test_check_bola_invariant_rejects_fake_200_ok() -> None:
    # Cross status is 200, but body contains semantic error
    cross_body_error = '{"status": "error", "message": "Access denied"}'
    legit_body = '{"id": "v1", "location": "secret_spot"}'

    verdict = check_bola_invariant(
        baseline_status=200,
        cross_status=200,
        control_status=401,
        body_similarity=0.9,
        baseline_body=legit_body,
        cross_body=cross_body_error,
        control_body="",
    )
    assert verdict.is_vulnerable is False
    assert "semantic denial" in verdict.rationale.lower() or "blocked" in verdict.rationale.lower()


def test_check_bfla_invariant_rejects_semantic_error() -> None:
    error_body = '{"code": 403, "error": "forbidden action"}'
    verdict = check_bfla_invariant(
        required_role="ADMIN",
        actual_role="USER",
        response_status=200,
        response_body=error_body,
    )
    assert verdict.is_vulnerable is False


def test_check_ssrf_metadata_invariant() -> None:
    # AWS metadata response
    aws_body = '{"ami-id": "ami-12345678", "instance-id": "i-0abcdef1234567890"}'
    v_aws = check_ssrf_metadata_invariant(200, aws_body)
    assert v_aws.is_vulnerable is True
    assert "INV_SSRF_NETWORK_ISOLATION" in v_aws.violated_invariants

    # Non-metadata safe response
    safe_body = '{"status": "ok", "message": "image converted successfully"}'
    v_safe = check_ssrf_metadata_invariant(200, safe_body)
    assert v_safe.is_vulnerable is False

    # Blocked 403
    v_blocked = check_ssrf_metadata_invariant(403, "Forbidden")
    assert v_blocked.is_vulnerable is False


def test_check_race_condition_toctou_invariant() -> None:
    # 5 concurrent requests: 3 succeeded (should fail invariant if max=1)
    statuses_vuln = [200, 200, 200, 400, 400]
    v_race = check_race_condition_toctou_invariant(statuses_vuln, max_allowed_success=1)
    assert v_race.is_vulnerable is True
    assert "INV_ATOMIC_STATE_TRANSITION" in v_race.violated_invariants

    # Only 1 succeeded -> invariant held
    statuses_safe = [200, 400, 400, 400, 400]
    v_safe = check_race_condition_toctou_invariant(statuses_safe, max_allowed_success=1)
    assert v_safe.is_vulnerable is False


def test_check_jwt_key_confusion_invariant() -> None:
    # Alg: none accepted
    v_none = check_jwt_key_confusion_invariant(200, '{"data": "secret"}', attack_type="alg_none")
    assert v_none.is_vulnerable is True
    assert "INV_CRYPTOGRAPHIC_INTEGRITY" in v_none.violated_invariants

    # Tampered rejected with 401
    v_rej = check_jwt_key_confusion_invariant(401, '{"error": "invalid signature"}')
    assert v_rej.is_vulnerable is False
