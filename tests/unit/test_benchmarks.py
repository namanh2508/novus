"""Unit tests for crAPI benchmark runner and metric evaluation."""

from datetime import UTC, datetime

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
from agentic_pentest.evaluation.crapi_runner import CrapiBenchmarkRunner
from agentic_pentest.evaluation.evaluate_metrics import format_academic_latex_table


def test_crapi_benchmark_runner_evaluation() -> None:
    runner = CrapiBenchmarkRunner(ground_truth_path="benchmarks/crapi/ground_truth.json")

    now = datetime.now(UTC)
    bob = Principal(id="u_bob", name="Bob", role=Role.USER)
    car = TargetObject(id="obj_1", type_name="vehicle_id", owner_principal_id="u_alice", value="v1")
    req = HTTPRequestObservation(
        method=HTTPMethod.GET,
        url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        headers={},
        body=None,
        timestamp=now,
    )
    resp = HTTPResponseObservation(
        status_code=200,
        headers={},
        body="{}",
        latency_ms=10,
        body_sha256="hash",
        timestamp=now,
    )
    triplet = DifferentialTriplet(
        baseline_legitimate=(req, resp),
        cross_principal_test=(req, resp),
        unauthenticated_control=(req, resp),
    )

    finding = Finding(
        id="FINDING-001",
        category=VulnerabilityCategory.BOLA,
        severity=Severity.HIGH,
        title="BOLA in vehicle location",
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/v1/location",
        method=HTTPMethod.GET,
        target_object=car,
        attacker_principal=bob,
        triplet=triplet,
        verification_proof="Cross-principal access succeeded",
        created_at=now,
    )

    result = runner.evaluate_findings(findings=[finding], elapsed_seconds=2.5, probes_count=6)

    assert result.precision == 1.0  # 1 TP, 0 FP
    assert len(result.true_positives) == 1
    assert "CRAPI-BOLA-01" in result.true_positives[0]
    assert len(result.false_positives) == 0


def test_latex_table_generation() -> None:
    data = [
        {
            "name": "Model X",
            "precision": 0.95,
            "recall": 0.80,
            "f1_score": 0.87,
            "false_positives": 1,
            "poc_repro": 0.90,
            "probes": 50,
        }
    ]
    latex = format_academic_latex_table(data)
    assert r"\begin{table*}" in latex
    assert "95.0\\%" in latex
    assert r"\bottomrule" in latex
