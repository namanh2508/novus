import pytest

from agentic_pentest.domain.safety.rules_of_engagement import (
    LeakyBucketRateLimiter,
    RoEViolationError,
    RoEViolationType,
    RulesOfEngagement,
)


def test_roe_forbidden_path_enforcement() -> None:
    roe = RulesOfEngagement()

    # Allowed endpoint
    roe.validate_request_bounds("GET", "http://localhost:8888/identity/api/v2/user/profile")

    # Forbidden paths should raise RoEViolationError
    with pytest.raises(RoEViolationError) as exc_info:
        roe.validate_request_bounds("POST", "http://localhost:8888/identity/api/auth/logout")
    assert exc_info.value.violation_type == RoEViolationType.FORBIDDEN_PATH

    with pytest.raises(RoEViolationError) as exc_info_db:
        roe.validate_request_bounds("DELETE", "http://localhost:8888/admin/delete-db")
    assert exc_info_db.value.violation_type == RoEViolationType.FORBIDDEN_PATH


def test_roe_disallowed_method() -> None:
    roe = RulesOfEngagement(allowed_methods=("GET", "POST"))
    with pytest.raises(RoEViolationError) as exc_info:
        roe.validate_request_bounds("DELETE", "http://localhost:8888/identity/api/v2/user")
    assert exc_info.value.violation_type == RoEViolationType.DISALLOWED_METHOD


def test_leaky_bucket_rate_limiter() -> None:
    limiter = LeakyBucketRateLimiter(rate_per_second=5.0, burst=3)

    # First 3 burst requests should be allowed
    assert limiter.allow_request() is True
    assert limiter.allow_request() is True
    assert limiter.allow_request() is True

    # Immediate 4th request without delay should be blocked
    assert limiter.allow_request() is False

    # Reset allows burst again
    limiter.reset()
    assert limiter.allow_request() is True
