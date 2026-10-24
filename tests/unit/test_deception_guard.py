from agentic_pentest.domain.deception_guard import DeceptionGuard


def test_deception_guard_detects_canary_domain():
    guard = DeceptionGuard()
    res = guard.analyze_target("http://test.canarytokens.org/auth/token")
    assert res.is_deception is True
    assert res.risk_level == "HONEYPOT_TRAP"
    assert any("canarytokens.org" in ind for ind in res.detected_indicators)


def test_deception_guard_detects_honeypot_path():
    guard = DeceptionGuard()
    res = guard.analyze_target("http://127.0.0.1:8888/honey/login")
    assert res.is_deception is True
    assert any("Honeypot URI Pattern" in ind for ind in res.detected_indicators)


def test_deception_guard_detects_canary_headers():
    guard = DeceptionGuard()
    res = guard.analyze_target(
        "http://127.0.0.1:8888/api/v1/user",
        headers={"X-Canary-Token": "secret123"},
    )
    assert res.is_deception is True
    assert any("Canary Tripwire Header" in ind for ind in res.detected_indicators)


def test_deception_guard_allows_safe_targets():
    guard = DeceptionGuard()
    res = guard.analyze_target("http://127.0.0.1:8888/identity/api/v2/vehicle")
    assert res.is_deception is False
    assert res.risk_level == "SAFE"


def test_deception_guard_filters_endpoints():
    guard = DeceptionGuard()
    endpoints = [
        "http://127.0.0.1:8888/api/v1/user",
        "http://127.0.0.1:8888/honeypot/admin",
        "http://canarytokens.com/test",
        "http://127.0.0.1:8888/api/v1/order",
    ]
    safe = guard.filter_safe_endpoints(endpoints)
    assert len(safe) == 2
    assert "http://127.0.0.1:8888/api/v1/user" in safe
    assert "http://127.0.0.1:8888/api/v1/order" in safe
