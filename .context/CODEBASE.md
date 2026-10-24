# CODEBASE.md — Module, Class & Function Catalog

---

## 1. Directory Tree & Responsibilities

```
src/agentic_pentest/
├── __init__.py
├── domain/                          # LAYER 1: PURE DOMAIN
│   ├── __init__.py
│   ├── entities.py                  # Core entities: Principal, Object, Finding, AgentTurn
│   ├── invariants.py                # Mathematical rules: SemanticDiff, SSRF, TOCTOU, JWT
│   ├── mutation.py                  # Polymorphic mutator
│   ├── denoiser.py                  # Advanced fuzzy entropy denoiser
│   ├── deception_guard.py           # Canarytokens & Honeypot detection
│   ├── coverage_ledger.py           # Attack surface coverage ledger & matrix
│   ├── telemetry/                   # Observability & financial telemetry
│   │   ├── __init__.py
│   │   └── tracer.py                # OpenTelemetry agent spans & LLM cost accounting
│   ├── safety/                      # Scope, RoE and network perimeter safety
│   │   ├── __init__.py
│   │   ├── net_policy.py            # NetworkScopePolicy (CIDR scope guard, URL redactor)
│   │   ├── rules_of_engagement.py   # Enterprise RoE & Leaky-Bucket Rate Limiter
│   │   └── threat_matrix.py         # OWASP API 2023, MITRE ATT&CK & CWE mapping
│   └── exceptions.py                # Typed domain exceptions
│
├── application/                     # LAYER 2: APPLICATION USE CASES & ORCHESTRATION
│   ├── __init__.py
│   ├── interfaces/                  # Abstract protocols (Dependency Inversion)
│   ├── orchestration/
│   │   ├── dual_brain_router.py     # System 1 / System 2 confidence router
│   │   ├── context_compactor.py     # microCompact sliding window (<16k tokens)
│   │   ├── background_dreamer.py    # autoDream offline heuristic consolidation
│   │   ├── swarm_orchestrator.py    # Bounded parallel worker pool with graph locks
│   │   ├── consensus_verifier.py    # 3-Agent Consensus Voting Engine with Domain Veto
│   │   ├── dead_end_detector.py     # Unviable path cycle detection & DAG backtracking
│   │   ├── attack_chain.py          # 6-Stage Attack Chain Lifecycle State Machine
│   │   ├── autonomous_orchestrator.py
│   │   ├── dynamic_auth.py
│   │   └── dynamic_harvester.py
│   └── use_cases/
│       ├── tool_registry.py         # PentestToolRegistry (MCP compliant)
│       ├── verify_differential.py   # VerifyDifferentialUseCase (3-way oracle)
│       ├── generate_poc.py          # Standalone PoC Generator (Python, urllib, cURL, Go, Node, Raw HTTP)
│       ├── eval_runner.py           # 41-case benchmark evaluation harness
│       └── export_sarif.py          # SARIF 2.1.0 with CVSS v3.1 vector calculations
│
├── infrastructure/                  # LAYER 3: ADAPTERS & DRIVERS
│   ├── __init__.py
│   ├── executors/
│   │   ├── httpx_executor.py        # Async HTTPX driver with scope guard
│   │   ├── shadow_cloner.py         # Shadow object cloning & rollback journal
│   │   └── vcr_recorder.py          # Hermetic VCR/HAR cassette record & replay

│   ├── __init__.py
│   ├── discovery/
│   │   ├── openapi_parser.py        # OpenAPI spec parser
│   │   ├── openapi_reconstructor.py # Reverse engineers OpenAPI 3.0 from traffic
│   │   ├── osint_scanner.py         # Subdomain, S3/GCS bucket leak, CNAME takeover
│   │   ├── semantic_grepper.py      # Semantic code triage (jevgrep pattern)
│   │   ├── threat_intel_bridge.py   # Cyberspace search (FOFA, Quake, Hunter, Shodan)
│   │   └── playwright_crawler.py    # Headless crawler with anti-bot stealth
│   ├── proxy/
│   │   ├── proxy_rotator.py         # Dynamic multi-protocol proxy rotation & quarantine
│   │   ├── ip_reputation.py         # Egress IP verification & leak detection
│   │   └── interception_dashboard.py# Port 8090 real-time SSE packet dashboard
│   ├── reasoning/
│   │   ├── jev_decision_engine.py   # Jev/Laya System 1 engine + injection sanitizer
│   │   ├── tool_call_repair.py      # Deterministic JSON repair (openclaw pattern)
│   │   └── litellm_client.py        # System 2 LiteLLM adapter (Claude/GPT/DeepSeek)
│   ├── storage/
│   │   ├── networkx_graph.py        # In-memory Evidence Graph adapter
│   │   ├── sqlite_audit_store.py    # WAL-mode persistent audit trail
│   │   ├── episodic_knowledge.py    # Cross-engagement durable heuristic database
│   │   └── sqlite_session_store.py  # Checkpoint & turn persistence
│   └── tools_kali/
│       └── structured_bridge.py     # PATH-discovery of 100+ OS pentest tools
│
└── presentation/                    # LAYER 4: OPERATOR INTERFACE & REPORTING
    ├── __init__.py
    ├── cli.py                       # Typer CLI application (`agentic-pentest run`)
    ├── chat.py                      # Interactive Cyber-Whale shell with slash commands
    ├── sarif_exporter.py            # SARIF 2.1.0 presentation exporter
    └── tui/
        ├── __init__.py
        └── terminal_canvas.py       # Rich interactive terminal DAG & telemetry canvas
```

---

## 2. Key Interfaces & Function Signatures

### `application.interfaces.verifier.IIndependentVerifier`
```python
from typing import Protocol, Tuple
from ...domain.entities import EvidenceObservation, Finding


class IIndependentVerifier(Protocol):
    async def verify_observation(
        self, observation: EvidenceObservation
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
        self, active_hypotheses: List[Hypothesis], remaining_budget: int
    ) -> Optional[TestAction]:
        """
        Evaluates current evidence graph state and remaining request budget
        to select the highest-value next testing action.
        """
        ...
```
