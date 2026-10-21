# TASK-002: Domain Invariants & Semantic Diff Engine

## Objective
Implement mathematical invariant rules and the JSON AST semantic diff engine for BOLA/BFLA verification.

## Target File
`src/agentic_pentest/domain/invariants.py`

## Architecture Invariants
- **Clean Architecture Inward Rule**: Pure domain logic. No HTTP or database imports.
- Pure Python standard library (`json`, `re`, `typing`, `dataclasses`).

## Required Classes & Functions
1. `class SemanticDiffEngine`:
   - `__init__(self, noise_keys: set[str] | None = None)`
   - `mask_noise(self, data: Any) -> Any`: Recursively walks JSON structures (dicts, lists) and strips keys matching `noise_keys` (case-insensitive, e.g. `timestamp`, `nonce`, `trace_id`, `created_at`, `updated_at`).
   - `compute_similarity(self, json_str_a: str, json_str_b: str) -> float`: Returns Jaccard / AST token similarity between 0.0 and 1.0. Returns 1.0 if identical after normalization and noise masking.
2. `def check_bola_invariant(baseline_status: int, cross_status: int, control_status: int, body_similarity: float) -> OracleVerdict`:
   - Evaluates the 3-Way Differential Invariant:
     * If `baseline_status == 200` AND `cross_status == 200` AND `control_status in (401, 403)` AND `body_similarity >= 0.8`: Returns `OracleVerdict(is_vulnerable=True, confidence_score=0.98, violated_invariants=["INV_OBJECT_ISOLATION"])`.
     * If `cross_status in (401, 403, 404)`: Returns `OracleVerdict(is_vulnerable=False, confidence_score=1.0)`.
3. `def check_bfla_invariant(required_role: str, actual_role: str, response_status: int) -> OracleVerdict`:
   - If `actual_role != required_role` and `response_status == 200`: Returns `OracleVerdict(is_vulnerable=True, violated_invariants=["INV_ROLE_HIERARCHY"])`.
   - Else returns `OracleVerdict(is_vulnerable=False)`.

## Definition of Done (DoD)
1. File exists at `src/agentic_pentest/domain/invariants.py`.
2. Passes all tests in `tests/unit/test_invariants.py`.
3. Passes `ruff check .` with 0 warnings.
4. Passes `mypy --strict src/agentic_pentest/domain/invariants.py` with 0 errors.

---

## 📋 Copilot Prompt (Copy & Paste to Copilot Edits / Agent Mode)
```text
Please implement the invariant checking and semantic diff engine in `src/agentic_pentest/domain/invariants.py` strictly following `tasks/TASK-002-domain-invariants.md`.
Requirements:
1. Import `OracleVerdict` from `agentic_pentest.domain.entities`.
2. Ensure strict type annotations.
3. Handle invalid JSON gracefully without raising unhandled exceptions.
4. Ensure tests/unit/test_invariants.py passes completely.
```
