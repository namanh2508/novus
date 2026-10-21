# TASK-001: Pure Domain Entities Implementation

## Objective
Implement pure domain entities and value objects for the pentesting agent according to Clean Architecture rules.

## Target File
`src/agentic_pentest/domain/entities.py`

## Architecture Invariants
- **Clean Architecture Inward Rule**: MUST NOT import `httpx`, `litellm`, `sqlite3`, `pydantic_settings`, or any framework driver.
- Use Python standard library (`dataclasses`, `enum`, `datetime`, `typing`, `uuid`) or pure `pydantic.BaseModel` with `frozen=True`.
- All domain models must be immutable (read-only after construction).

## Required Entities & Enums
1. `HTTPMethod(str, Enum)`: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`, `HEAD`.
2. `Role(str, Enum)`: `ANONYMOUS`, `USER`, `ADMIN`, `MECHANIC`, `AUDITOR`.
3. `Severity(str, Enum)`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
4. `VulnerabilityCategory(str, Enum)`: `BOLA`, `BFLA`, `BOPLA`, `BUSINESS_LOGIC`.
5. `Principal`:
   - `id: str`
   - `name: str`
   - `role: Role`
   - `jwt_token: str | None = None`
   - `session_headers: dict[str, str] = field(default_factory=dict)`
6. `TargetObject`:
   - `id: str`
   - `type_name: str` (e.g., `"vehicle_id"`, `"order_id"`)
   - `owner_principal_id: str`
   - `value: str`
   - `attributes: dict[str, Any] = field(default_factory=dict)`
7. `HTTPRequestObservation`:
   - `method: HTTPMethod`
   - `url: str`
   - `headers: dict[str, str]`
   - `body: str | None`
   - `timestamp: datetime`
8. `HTTPResponseObservation`:
   - `status_code: int`
   - `headers: dict[str, str]`
   - `body: str`
   - `latency_ms: int`
   - `body_sha256: str`
   - `timestamp: datetime`
9. `DifferentialTriplet`:
   - `baseline_legitimate: tuple[HTTPRequestObservation, HTTPResponseObservation]`
   - `cross_principal_test: tuple[HTTPRequestObservation, HTTPResponseObservation]`
   - `unauthenticated_control: tuple[HTTPRequestObservation, HTTPResponseObservation]`
10. `OracleVerdict`:
    - `is_vulnerable: bool`
    - `confidence_score: float` (0.0 to 1.0)
    - `rationale: str`
    - `violated_invariants: list[str] = field(default_factory=list)`
11. `Finding`:
    - `id: str`
    - `category: VulnerabilityCategory`
    - `severity: Severity`
    - `title: str`
    - `endpoint_url: str`
    - `method: HTTPMethod`
    - `target_object: TargetObject`
    - `attacker_principal: Principal`
    - `triplet: DifferentialTriplet`
    - `verification_proof: str`
    - `created_at: datetime`

## Definition of Done (DoD)
1. File exists at `src/agentic_pentest/domain/entities.py`.
2. Passes all tests in `tests/unit/test_entities.py`.
3. Passes `ruff check .` with 0 warnings.
4. Passes `mypy --strict src/agentic_pentest/domain/entities.py` with 0 errors.

---

## 📋 Copilot Prompt (Copy & Paste to Copilot Edits / Agent Mode)
```text
Please implement the pure domain entities in `src/agentic_pentest/domain/entities.py` strictly following the specification in `tasks/TASK-001-domain-entities.md`.
Requirements:
1. Use dataclasses with @dataclass(frozen=True, slots=True) or Pydantic frozen models.
2. Ensure all types are strictly annotated (mypy --strict compatible).
3. Do not import any external I/O libraries (no httpx, no sqlite3, no litellm).
4. Ensure it satisfies tests/unit/test_entities.py.
```
