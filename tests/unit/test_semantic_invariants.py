from agentic_pentest.domain.invariants import (
    check_bfla_invariant,
    check_bola_invariant,
    is_semantic_error_response,
)


def test_is_semantic_error_response_json():
    # 200 OK with explicit error in JSON
    body1 = '{"status": "error", "message": "unauthorized access to object"}'
    assert is_semantic_error_response(200, body1) is True

    # 200 OK with success: false
    body2 = '{"success": false, "error": "Permission denied"}'
    assert is_semantic_error_response(200, body2) is True

    # 200 OK with genuine data
    body3 = '{"id": "v1", "owner": "alice", "latitude": 10.0}'
    assert is_semantic_error_response(200, body3) is False


def test_is_semantic_error_response_html():
    body_html = "<html><head><title>Access Denied</title></head><body>Forbidden</body></html>"
    assert is_semantic_error_response(200, body_html) is True


def test_check_bola_invariant_rejects_fake_200_ok():
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


def test_check_bfla_invariant_rejects_semantic_error():
    error_body = '{"code": 403, "error": "forbidden action"}'
    verdict = check_bfla_invariant(
        required_role="ADMIN",
        actual_role="USER",
        response_status=200,
        response_body=error_body,
    )
    assert verdict.is_vulnerable is False
