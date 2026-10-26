"""Unit tests for RollbackJournal and SafeRollbackManager (Safe Mode Mutation Protection)."""

from __future__ import annotations

import pytest

from agentic_pentest.application.interfaces.executor import IHTTPExecutor
from agentic_pentest.application.security.safe_rollback_manager import SafeRollbackManager
from agentic_pentest.application.use_cases.verify_differential import DifferentialVerifier
from agentic_pentest.domain.entities import (
    HTTPMethod,
    HTTPRequestObservation,
    HTTPResponseObservation,
    Principal,
    Role,
    TargetObject,
)
from agentic_pentest.domain.safety.rollback_journal import (
    CompensationType,
    RollbackJournal,
    RollbackRecipe,
    RollbackStatus,
)


class MockMutationExecutor(IHTTPExecutor):
    """Mock executor simulating live target entity state, mutation, and restoration."""

    def __init__(self) -> None:
        self.entities: dict[str, str] = {
            "http://localhost:8888/identity/api/v2/vehicle/v123": '{"id":"v123","owner":"Alice","color":"red"}'
        }
        self.request_history: list[tuple[str, str, str | None]] = []
        self.fail_revert: bool = False

    async def execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
        principal: Principal | None = None,
    ) -> tuple[HTTPRequestObservation, HTTPResponseObservation]:
        method_upper = method.upper()
        self.request_history.append((method_upper, url, body))

        req_obs = HTTPRequestObservation(
            method=HTTPMethod[method_upper]
            if method_upper in HTTPMethod.__members__
            else HTTPMethod.GET,
            url=url,
            headers=headers or {},
            body=body,
        )

        # Unauthenticated probe returns 401
        if principal is None:
            return req_obs, HTTPResponseObservation(
                status_code=401,
                headers={"content-type": "application/json"},
                body='{"error":"Unauthorized"}',
                latency_ms=8,
                body_sha256="err401",
            )

        if self.fail_revert and method_upper in {"POST", "PUT"}:
            return req_obs, HTTPResponseObservation(
                status_code=500,
                headers={"content-type": "application/json"},
                body='{"error":"Database error during restoration"}',
                latency_ms=15,
                body_sha256="err500",
            )

        if method_upper == "GET":
            if url in self.entities:
                return req_obs, HTTPResponseObservation(
                    status_code=200,
                    headers={"content-type": "application/json"},
                    body=self.entities[url],
                    latency_ms=10,
                    body_sha256="hash200",
                )
            return req_obs, HTTPResponseObservation(
                status_code=404,
                headers={"content-type": "application/json"},
                body='{"error":"Not Found"}',
                latency_ms=10,
                body_sha256="hash404",
            )

        elif method_upper == "DELETE":
            # Delete removes entity
            self.entities.pop(url, None)
            return req_obs, HTTPResponseObservation(
                status_code=200,
                headers={"content-type": "application/json"},
                body='{"message":"Entity deleted successfully"}',
                latency_ms=12,
                body_sha256="del200",
            )

        elif method_upper == "PUT":
            # Overwrite entity
            self.entities[url] = body or ""
            return req_obs, HTTPResponseObservation(
                status_code=200,
                headers={"content-type": "application/json"},
                body='{"message":"Entity updated successfully"}',
                latency_ms=14,
                body_sha256="put200",
            )

        elif method_upper == "POST":
            # Recreate entity
            # e.g. collection POST -> recreate /identity/api/v2/vehicle/v123
            created_url = f"{url}/v123"
            self.entities[created_url] = body or ""
            return req_obs, HTTPResponseObservation(
                status_code=201,
                headers={"content-type": "application/json"},
                body='{"message":"Entity recreated successfully"}',
                latency_ms=18,
                body_sha256="post201",
            )

        return req_obs, HTTPResponseObservation(
            status_code=200,
            headers={},
            body="{}",
            latency_ms=5,
            body_sha256="ok",
        )


def test_rollback_journal_domain_lifecycle() -> None:
    journal = RollbackJournal()
    assert journal.total_entries == 0
    assert journal.pending_count == 0

    recipe = RollbackRecipe(
        compensation_type=CompensationType.OVERWRITE_VIA_PUT,
        revert_method="PUT",
        revert_url="http://localhost:8888/api/item/1",
        revert_body='{"status":"original"}',
    )
    entry = journal.record_mutation(
        entry_id="rb-001",
        target_endpoint="http://localhost:8888/api/item/1",
        original_method="PUT",
        target_object_id="item-1",
        original_state_body='{"status":"original"}',
        recipe=recipe,
    )

    assert entry.status == RollbackStatus.RECORDED
    assert journal.total_entries == 1
    assert journal.pending_count == 1

    entry.mark_restored("HTTP 200 Overwrite verified")
    assert entry.status == RollbackStatus.VERIFIED_RESTORED
    assert journal.pending_count == 0

    summary = journal.create_audit_summary()
    assert summary["total_mutations_recorded"] == 1
    assert summary["successfully_restored"] == 1
    assert summary["pending_restorations"] == 0
    assert summary["failed_restorations"] == 0


@pytest.mark.asyncio
async def test_safe_rollback_manager_delete_and_compensate() -> None:
    executor = MockMutationExecutor()
    manager = SafeRollbackManager(executor)
    alice = Principal(id="u_alice", name="Alice", role=Role.USER, jwt_token="token_alice")

    target_url = "http://localhost:8888/identity/api/v2/vehicle/v123"

    # Pre-capture state before DELETE mutation using owner principal
    entry = await manager.pre_capture_and_record(
        endpoint_url=target_url,
        method="DELETE",
        target_object_id="v123",
        principal=alice,
    )

    assert entry.original_state_body is not None
    assert "Alice" in entry.original_state_body
    assert entry.recipe.compensation_type == CompensationType.RECREATE_VIA_POST
    assert entry.recipe.revert_method == "POST"

    # Simulate cross-principal DELETE occurring
    await executor.execute_request("DELETE", target_url, principal=alice)
    assert target_url not in executor.entities  # Entity is gone

    # Execute rollback compensation with owner principal
    success = await manager.execute_entry_rollback(entry, principal=alice)
    assert success is True
    assert entry.status == RollbackStatus.VERIFIED_RESTORED
    assert target_url in executor.entities  # Entity is restored!


@pytest.mark.asyncio
async def test_safe_rollback_manager_failure_handling() -> None:
    executor = MockMutationExecutor()
    executor.fail_revert = True  # Target database fails on restore
    manager = SafeRollbackManager(executor)
    alice = Principal(id="u_alice", name="Alice", role=Role.USER, jwt_token="token_alice")

    target_url = "http://localhost:8888/identity/api/v2/vehicle/v123"
    entry = await manager.pre_capture_and_record(
        endpoint_url=target_url,
        method="PUT",
        target_object_id="v123",
        principal=alice,
    )

    success = await manager.execute_entry_rollback(entry, principal=alice)
    assert success is False
    assert entry.status == RollbackStatus.COMPENSATION_FAILED
    assert "500" in entry.verification_notes


@pytest.mark.asyncio
async def test_differential_verifier_with_safe_rollback() -> None:
    executor = MockMutationExecutor()
    verifier = DifferentialVerifier(executor=executor, safe_mode=True)

    alice = Principal(id="u_alice", name="Alice", role=Role.USER, jwt_token="token_alice")
    bob = Principal(id="u_bob", name="Bob", role=Role.USER, jwt_token="token_bob")
    car = TargetObject(
        id="v123",
        type_name="vehicle_id",
        owner_principal_id="u_alice",
        value="v123",
    )

    # Bob attempts DELETE on Alice's car under safe mode
    finding = await verifier.verify_bola(
        endpoint_url="http://localhost:8888/identity/api/v2/vehicle/{vehicle_id}",
        method=HTTPMethod.DELETE,
        target_object=car,
        legitimate_owner=alice,
        attacker=bob,
    )

    assert finding is not None
    assert "Verified Rollback" in finding.verification_proof
    assert verifier.rollback_manager is not None
    assert verifier.rollback_manager.journal.total_entries >= 1
    # Check that car is restored in executor entities
    target_url = "http://localhost:8888/identity/api/v2/vehicle/v123"
    assert target_url in executor.entities
