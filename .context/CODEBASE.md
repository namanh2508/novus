# CODEBASE.md — Module, Class & Function Catalog

---

## 1. Directory Tree & Responsibilities

```
src/agentic_pentest/
├── __init__.py
├── domain/                          # LAYER 1: PURE DOMAIN
│   ├── __init__.py
│   ├── entities.py                  # Core entities: Principal, Object, Finding
│   ├── invariants.py                # Mathematical rules: SemanticDiff, TokenEntropy
│   └── exceptions.py                # Typed domain exceptions
│
├── application/                     # LAYER 2: APPLICATION USE CASES
│   ├── __init__.py
│   ├── interfaces/                  # Abstract protocols (Dependency Inversion)
│   │   ├── __init__.py
│   │   ├── executor.py              # IHttpExecutor protocol
│   │   ├── planner.py               # IAdaptivePlanner protocol
│   │   ├── verifier.py              # IIndependentVerifier protocol
│   │   └── store.py                 # IEvidenceGraphStore protocol
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── plan_next_action.py      # PlanNextActionUseCase
│   │   ├── execute_safe_action.py   # ExecuteSafeActionUseCase (with shadow copy)
│   │   ├── verify_differential.py   # VerifyDifferentialUseCase (3-way oracle)
│   │   ├── generate_poc.py          # GeneratePocUseCase
│   │   └── export_sarif.py          # ExportSarifUseCase
│
├── infrastructure/                  # LAYER 3: ADAPTERS & IMPLEMENTATIONS
│   ├── __init__.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   └── openapi_parser.py        # OpenApiSchemaParser (extracts paths & schemas)
│   ├── executors/
│   │   ├── __init__.py
│   │   ├── httpx_executor.py        # HttpxExecutorAdapter (async HTTP engine)
│   │   ├── playwright_sandbox.py    # PlaywrightBrowserSandbox (DOM / browser state)
│   │   └── shadow_cloner.py         # ShadowObjectCloner (idempotent rollback)
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── networkx_graph.py        # NetworkXEvidenceGraphAdapter
│   │   └── sqlite_audit_store.py    # SqliteAuditStoreAdapter (immutable trace log)
│   ├── reasoning/
│   │   ├── __init__.py
│   │   ├── litellm_client.py        # LiteLLMReasoningClient (structured prompt calling)
│   │   └── prompt_templates.py      # Jinja2 prompt rendering engine
│   └── playbooks/
│       ├── __init__.py
│       ├── registry.py              # PlaybookRegistry (loads WSTG YAML specs)
│       └── data/                    # Bundled executable playbooks
│           ├── bola_read.yaml
│           ├── bola_write.yaml
│           └── bfla_admin.yaml
│
└── presentation/                    # LAYER 4: USER INTERFACE & CI RUNNER
    ├── __init__.py
    ├── cli.py                       # Typer CLI application (`agentic-pentest run`)
    └── ci_gate.py                   # GitHub Actions PR Gate entrypoint
```

---

## 2. Key Interfaces & Function Signatures

### `application.interfaces.verifier.IIndependentVerifier`
```python
from typing import Protocol, Tuple
from ...domain.entities import EvidenceObservation, Finding

class IIndependentVerifier(Protocol):
    async def verify_observation(
        self,
        observation: EvidenceObservation
    ) -> Tuple[bool, float, Optional[Finding]]:
        """
        Executes 3-way differential verification.
        Returns: (is_confirmed: bool, confidence: float, finding: Optional[Finding])
        """
        ...
```

### `application.interfaces.planner.IAdaptivePlanner`
```python
from typing import Protocol, List
from ...domain.entities import TestAction, Hypothesis

class IAdaptivePlanner(Protocol):
    async def select_next_action(
        self,
        active_hypotheses: List[Hypothesis],
        remaining_budget: int
    ) -> Optional[TestAction]:
        """
        Evaluates current evidence graph state and remaining request budget
        to select the highest-value next testing action.
        """
        ...
```
