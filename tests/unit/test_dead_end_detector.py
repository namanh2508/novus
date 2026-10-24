from agentic_pentest.application.orchestration.dead_end_detector import DeadEndDetector


def test_dead_end_detector_prunes_after_threshold() -> None:
    detector = DeadEndDetector(failure_threshold=3)

    url = "http://localhost:8888/identity/api/v2/nonexistent"
    method = "GET"

    assert detector.is_dead_end(method, url) is False

    # Failures 1 and 2
    pruned_1 = detector.record_outcome(
        method, url, 404, is_success=False, failure_reason="Not Found"
    )
    assert pruned_1 is False
    assert detector.is_dead_end(method, url) is False

    pruned_2 = detector.record_outcome(
        method, url, 404, is_success=False, failure_reason="Not Found"
    )
    assert pruned_2 is False
    assert detector.is_dead_end(method, url) is False

    # 3rd failure triggers pruning
    pruned_3 = detector.record_outcome(
        method, url, 404, is_success=False, failure_reason="Not Found"
    )
    assert pruned_3 is True
    assert detector.is_dead_end(method, url) is True

    # Filter candidate actions
    candidates = [("GET", url), ("GET", "http://localhost:8888/identity/api/v2/vehicle/1")]
    viable = detector.filter_viable_candidates(candidates)
    assert len(viable) == 1
    assert viable[0][1] == "http://localhost:8888/identity/api/v2/vehicle/1"


def test_success_resets_consecutive_failures() -> None:
    detector = DeadEndDetector(failure_threshold=3)
    url = "http://localhost:8888/identity/api/v2/vehicle/1"
    method = "GET"

    detector.record_outcome(method, url, 500, is_success=False)
    detector.record_outcome(method, url, 500, is_success=False)

    # Success resets consecutive failure count
    detector.record_outcome(method, url, 200, is_success=True)

    # Next failure should be count 1, not 3
    pruned = detector.record_outcome(method, url, 500, is_success=False)
    assert pruned is False
    assert detector.is_dead_end(method, url) is False
