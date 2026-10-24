"""Unit tests for SOTA research upgrades: AttackPathDAG, ProducerConsumerInferer, and WAFEvasionMutator."""

from __future__ import annotations

from agentic_pentest.application.orchestration.attack_path_dag import (
    AttackPathDAG,
    NodeExecutionStatus,
)
from agentic_pentest.application.orchestration.subagent_delegator import SubagentRole
from agentic_pentest.application.use_cases.waf_evasion_mutator import (
    WAFEvasionMutator,
)
from agentic_pentest.infrastructure.discovery.producer_consumer_inferer import (
    DynamicProducerConsumerInferer,
)


def test_attack_path_dag_execution_and_artifact_propagation() -> None:
    dag = AttackPathDAG()
    dag.set_seed_artifact("target_url", "http://localhost:8888")

    # Hop 1: Recon produces vehicle_id
    n1 = dag.add_node(
        node_id="hop-01",
        title="Recon & Object Discovery",
        role=SubagentRole.RECON,
        target_endpoint="/identity/api/v2/vehicle",
        prerequisite_keys=["target_url"],
    )

    # Hop 2: Auth Audit requires vehicle_id and produces bola_finding_id
    dag.add_node(
        node_id="hop-02",
        title="BOLA Cross-User Audit",
        role=SubagentRole.AUTH_AUDIT,
        target_endpoint="/identity/api/v2/vehicle/{vehicle_id}/location",
        prerequisite_keys=["vehicle_id"],
    )
    dag.add_edge("hop-01", "hop-02")

    # Hop 3: Remediation requires bola_finding_id
    dag.add_node(
        node_id="hop-03",
        title="Generate Patch",
        role=SubagentRole.REMEDIATION,
        target_endpoint="/identity/api/v2/vehicle",
        prerequisite_keys=["bola_finding_id"],
    )
    dag.add_edge("hop-02", "hop-03")

    # Initially, only hop-01 is ready
    ready_init = dag.get_ready_nodes()
    assert len(ready_init) == 1
    assert ready_init[0].id == "hop-01"

    # Complete hop-01 and produce vehicle_id
    dag.mark_completed("hop-01", new_artifacts={"vehicle_id": "v-12345"}, latency_ms=45.2)
    assert n1.status == NodeExecutionStatus.COMPLETED

    # Now hop-02 becomes ready
    ready_step2 = dag.get_ready_nodes()
    assert len(ready_step2) == 1
    assert ready_step2[0].id == "hop-02"

    # Complete hop-02 and produce bola_finding_id
    dag.mark_completed(
        "hop-02", new_artifacts={"bola_finding_id": "FINDING-BOLA-01"}, latency_ms=120.0
    )

    # Now hop-03 becomes ready
    ready_step3 = dag.get_ready_nodes()
    assert len(ready_step3) == 1
    assert ready_step3[0].id == "hop-03"

    dag.mark_completed("hop-03", latency_ms=15.0)

    summary = dag.generate_attack_chain_summary()
    assert summary["total_hops"] == 3
    assert summary["completed_hops"] == 3
    assert summary["is_fully_compromised"] is True
    assert "vehicle_id" in summary["harvested_artifact_keys"]


def test_attack_path_dag_cascade_failure() -> None:
    dag = AttackPathDAG()
    dag.set_seed_artifact("target_url", "http://localhost:8888")

    dag.add_node(
        "n1", "Initial Hop", SubagentRole.RECON, "/api/start", prerequisite_keys=["target_url"]
    )
    dag.add_node(
        "n2", "Dependent Hop", SubagentRole.AUTH_AUDIT, "/api/next", prerequisite_keys=["token"]
    )
    dag.add_edge("n1", "n2")

    dag.mark_failed("n1", error="Connection refused")
    summary = dag.generate_attack_chain_summary()

    assert summary["failed_hops"] == 1
    assert summary["skipped_hops"] == 1
    assert summary["is_fully_compromised"] is False
    assert dag.nodes["n2"].status == NodeExecutionStatus.SKIPPED


def test_dynamic_producer_consumer_inferer() -> None:
    inferer = DynamicProducerConsumerInferer()

    # Response produced by POST /api/orders
    mock_order_response = {
        "status": "success",
        "order": {
            "order_id": "ord-998877",
            "items": [{"item_id": 101, "name": "Brake Rotor"}],
        },
        "session_id": "sess-abc",
    }

    produced = inferer.extract_produced_fields(
        endpoint="/api/orders",
        method="POST",
        response_data=mock_order_response,
    )
    assert "order.order_id" in produced
    assert produced["order.order_id"] == "ord-998877"

    # Consumer endpoint candidates
    consumer_candidates = [
        ("GET", "/api/orders/{order_id}"),
        ("DELETE", "/api/orders/{order_id}"),
        ("GET", "/api/catalog/items"),
    ]

    relations = inferer.infer_relations(consumer_candidates)
    assert len(relations) >= 2  # Matches GET and DELETE /api/orders/{order_id}

    rel = next(r for r in relations if r.consumer_method == "GET")
    assert rel.parameter_name == "order_id"
    assert rel.confidence >= 0.90

    # Resolve concrete URL
    concrete_url = inferer.resolve_concrete_consumer_url(rel, "ord-998877")
    assert concrete_url == "/api/orders/ord-998877"


def test_waf_evasion_mutator_detection_and_payloads() -> None:
    mutator = WAFEvasionMutator()

    # 1. Cloudflare detection
    cf_res = mutator.detect_waf(
        status_code=403,
        headers={"cf-ray": "848123abc-SJC", "server": "cloudflare"},
        body="<html>Attention Required! Cloudflare</html>",
    )
    assert cf_res.is_waf_detected is True
    assert cf_res.waf_vendor == "Cloudflare"

    # 2. ModSecurity detection
    mod_res = mutator.detect_waf(
        status_code=403,
        headers={"server": "nginx"},
        body="Access denied with code 403 [OWASP_CRS/3.3.0]",
    )
    assert mod_res.is_waf_detected is True
    assert mod_res.waf_vendor == "ModSecurity"

    # 3. Clean 200 response
    clean_res = mutator.detect_waf(status_code=200, headers={"server": "nginx"})
    assert clean_res.is_waf_detected is False

    # 4. SQL comment chunking mutation
    sql = "1' UNION SELECT username, password FROM users--"
    chunked = mutator.mutate_sql_payload(sql, strategy="comments")
    assert "/**/" in chunked
    assert "UN/**/ION" in chunked

    # 5. Full jitter backoff delay within bounds
    delay = mutator.calculate_backoff_delay(attempt=3, base_delay=1.0, max_delay=10.0)
    assert 0.5 <= delay <= 10.0
