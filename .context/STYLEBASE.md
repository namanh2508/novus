# STYLEBASE.md — Technical Standards, Clean Architecture & Coding Conventions

> **Language**: Python 3.11+ (Strict Typing, Pydantic v2, Asyncio)  
> **Linter & Formatter**: Ruff (`ruff check .`, `ruff format .`)  
> **Type Checker**: Mypy (`mypy --strict src/`)  

---

## 1. Clean Architecture Layering Rules

Our architecture enforces 4 strict concentric rings. **Dependencies only point inward.**

```
+-------------------------------------------------------------------------+
| [4. Frameworks & Drivers]                                              |
|   CLI (Typer), LiteLLM Gateway, HTTPX Async Client, Playwright Sandbox  |
+-------------------------------------------------------------------------+
       | implements interfaces defined one layer in
       v
+-------------------------------------------------------------------------+
| [3. Interface Adapters]                                                 |
|   OpenApiParserAdapter, SqliteEvidenceStore, NetworkXGraphAdapter,      |
|   PlaybookYamlRegistry, SarifReportPresenter                           |
+-------------------------------------------------------------------------+
       |
       v
+-------------------------------------------------------------------------+
| [2. Application (Use Cases)]                                            |
|   PlanNextAction, ExecuteSafeExploit, VerifyDifferentialOracle,         |
|   GenerateReproduciblePoC, ExportSarifReport                           |
+-------------------------------------------------------------------------+
       |
       v
+-------------------------------------------------------------------------+
| [1. Domain (Entities & Business Invariants)]                            |
|   Principal, TargetObject, EvidenceObservation, Finding, OracleVerdict. |
|   *Strict rule*: ZERO external I/O. No httpx, litellm, or sqlite3.      |
+-------------------------------------------------------------------------+
```

---

## 2. Coding Standards & Conventions

1. **Strict Type Annotations**:
   - Every function and method parameter and return value MUST have explicit type annotations.
   - Use `typing.Self`, `typing.Protocol`, `typing.Optional`, `typing.Sequence`, `typing.Mapping`.
   - Never use untyped `dict` or `Any` where a Pydantic model or dataclass is appropriate.

2. **Immutable Data Transfer Objects (DTOs)**:
   - Domain entities that represent factual history (`EvidenceObservation`, `Finding`, `IdentityToken`) must be decorated with `@dataclass(frozen=True)`.
   - State mutations are represented by constructing new instances or updating the repository via explicit use cases.

3. **Error Handling Hierarchy**:
   All custom exceptions inherit from `PentestAgentException`:
   ```python
   class PentestAgentException(Exception):
       """Base exception for all agent domain and application errors."""


   class ScopeViolationError(PentestAgentException):
       """Raised when an executor attempts an action outside the approved scope."""


   class SideEffectBlockedError(PentestAgentException):
       """Raised when an action violates the blast radius policy without shadow clone."""


   class OracleVerificationError(PentestAgentException):
       """Raised when the differential oracle detects inconsistent data invariants."""


   class BudgetExceededError(PentestAgentException):
       """Raised when the request count or token limit has been exhausted."""
   ```

4. **Structured Logging**:
   - Use `loguru` exclusively. Never use raw `print()` statements in library code.
   - Include structured contextual keys in logs: `logger.info("Executing differential check", endpoint=ep, principal=p_id, object=o_id)`.
