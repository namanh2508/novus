# EPIC-02: Execution Engine, 3-Way Differential Verifier & Zero-Dep PoC (Batch Tasks T-007 to T-010)

> **Objective**: Implement the core execution harness, the 3-Way Differential Invariant Oracle for zero false-positive BOLA verification, and the zero-dependency PoC generator.

---

## 📦 Scope of Deliverables

| Task | Target File | Role & Layer | Reference Test |
| :--- | :--- | :--- | :--- |
| **T-007** | `src/agentic_pentest/infrastructure/executors/httpx_executor.py` | `IHTTPExecutor` + Scope Guard (Infrastructure) | `tests/unit/test_httpx_executor.py` |
| **T-008** | `src/agentic_pentest/infrastructure/executors/shadow_cloner.py` | Mutation Isolation Guard (Infrastructure) | Spec compliant |
| **T-009** | `src/agentic_pentest/application/use_cases/verify_differential.py` | 3-Way Differential Invariant Oracle (Application) | `tests/unit/test_differential_verifier.py` |
| **T-010** | `src/agentic_pentest/application/use_cases/generate_poc.py` | Zero-Dependency PoC Generator (Application) | `tests/unit/test_poc_generator.py` |

---

## 🛠️ Detailed Specifications

### 1. `HTTPXExecutor` (`src/agentic_pentest/infrastructure/executors/httpx_executor.py`)
- Implements `IHTTPExecutor` from `agentic_pentest.application.interfaces.executor`.
- Accepts `allowed_hosts: list[str]`.
- Enforces Scope Guard: Parses host from URL using `urllib.parse.urlparse`. If host not in `allowed_hosts`, raises `ScopeViolationError`.
- Executes async request using `httpx.AsyncClient`.
- Injects auth headers if `principal` is provided:
  * If `principal.jwt_token`: `headers["Authorization"] = f"Bearer {principal.jwt_token}"`
  * Merges `principal.session_headers`.
- Returns `(HTTPRequestObservation, HTTPResponseObservation)` tuple.

### 2. `ShadowObjectCloner` (`src/agentic_pentest/infrastructure/executors/shadow_cloner.py`)
- Provides `clone_object(original_obj: TargetObject, clone_endpoint: str) -> TargetObject` to ensure destructive mutations (`PUT`, `DELETE`) never execute on unseeded or root entities.

### 3. `DifferentialVerifier` (`src/agentic_pentest/application/use_cases/verify_differential.py`)
- Takes `executor: IHTTPExecutor` and optional `diff_engine: SemanticDiffEngine`.
- Implements `async def verify_bola(endpoint_url: str, method: HTTPMethod, target_object: TargetObject, legitimate_owner: Principal, attacker: Principal) -> Finding | None`:
  1. Interpolates `target_object.value` into path (e.g. `{vehicle_id}` $\to$ `v123`).
  2. Runs **Baseline Request** with `legitimate_owner`.
  3. Runs **Cross-Principal Test** with `attacker`.
  4. Runs **Control Request** with `None` (unauthenticated).
  5. Computes body similarity via `SemanticDiffEngine(noise_keys={"timestamp", "trace_id", "nonce"}).compute_similarity(...)`.
  6. Evaluates `check_bola_invariant(baseline_status, cross_status, control_status, similarity)`.
  7. If `verdict.is_vulnerable`: constructs and returns a `Finding` with `triplet=DifferentialTriplet(...)`, `category=VulnerabilityCategory.BOLA`, `severity=Severity.HIGH`. Else returns `None`.

### 4. `PoCGenerator` (`src/agentic_pentest/application/use_cases/generate_poc.py`)
- Implements `def generate_python_poc(self, finding: Finding) -> str`:
- Generates a standalone Python script with:
  * Explanatory banner comment with Finding ID, category, and OWASP API rating.
  * Standalone execution using `import requests`.
  * Configured target URL, method, and attacker auth header.
  * Assertions checking for vulnerability confirmation.
  * Zero agent framework dependencies.

---

## 📋 Master Prompt for Copilot (Agent Mode / Copilot Edits)
```text
Please implement the 4 core execution, verifier, and PoC modules specified in `tasks/EPIC-02-execution-oracle-poc.md`:

1. `src/agentic_pentest/infrastructure/executors/httpx_executor.py` (implements IHTTPExecutor in `application/interfaces/executor.py` with Scope Guard)
2. `src/agentic_pentest/infrastructure/executors/shadow_cloner.py` (mutation isolation cloner)
3. `src/agentic_pentest/application/use_cases/verify_differential.py` (3-Way Differential Invariant Oracle for BOLA)
4. `src/agentic_pentest/application/use_cases/generate_poc.py` (Zero-dependency standalone Python PoC generator)

Requirements:
- Ensure all unit tests pass with 0 errors:
  * tests/unit/test_httpx_executor.py
  * tests/unit/test_differential_verifier.py
  * tests/unit/test_poc_generator.py
  * And all 13 prior tests (pytest tests/unit/)
- Strict typing (mypy --strict compliant) and Clean Architecture decoupling.
- Commit your changes in git:
  git add src/
  git commit -m "feat(core): implement EPIC-02 execution harness, differential verifier and PoC generator"
```
