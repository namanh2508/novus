# TODOBASE.md — Work Breakdown Structure (WBS) & Task Roadmap

> **Methodology**: Milestone-driven, Test-first for core invariants, Clean Architecture strictness.  
> **Timeline**: 10-Week Academic MVP Plan.  

---

## WBS Task Matrix

| ID | Epic | Task Description | Priority | Dep | Estimate | Deliverable (File Path) | DoD (Definition of Done) |
|---|---|---|:---:|:---:|:---:|---|---|
| **T-001** | Foundation | Define pure Domain entities & exceptions | DONE | - | 2d | `src/agentic_pentest/domain/entities.py` | 100% type annotated, frozen dataclasses, 0 external imports (COMPLETED) |
| **T-002** | Foundation | Implement Semantic Diff & Invariant Checker | DONE | T-001 | 2d | `src/agentic_pentest/domain/invariants.py` | Passes unit tests with 10 synthetic JSON test pairs (COMPLETED) |
| **T-003** | Ingestion | Build OpenAPI 3.0 Parser & Endpoint Discovery | DONE | T-001 | 3d | `src/agentic_pentest/infrastructure/discovery/openapi_parser.py` | Successfully extracts crAPI OpenAPI spec into TargetObjects (COMPLETED) |
| **T-004** | Ingestion | Implement Playbook Registry & YAML Validator | DONE | T-001 | 2d | `src/agentic_pentest/infrastructure/playbooks/registry.py` | Loads and validates `bola_read.yaml` against schema (COMPLETED) |
| **T-005** | Storage | Build NetworkX Evidence Graph Store | DONE | T-001 | 3d | `src/agentic_pentest/infrastructure/storage/networkx_graph.py` | Supports add_principal, add_object, query_paths with tests (COMPLETED) |
| **T-006** | Storage | Build SQLite Immutable Audit Trail Store | DONE | T-001 | 2d | `src/agentic_pentest/infrastructure/storage/sqlite_audit_store.py` | Stores raw HTTP request/response tuples with SHA-256 hash (COMPLETED) |
| **T-007** | Execution | Implement Async HTTPX Executor with Scope Guard | DONE | T-001 | 3d | `src/agentic_pentest/infrastructure/executors/httpx_executor.py` | Enforces URL allowlist, rate limits, raises ScopeViolationError (COMPLETED) |
| **T-008** | Execution | Build Shadow Object Cloner (Mutation Guard) | DONE | T-007 | 2d | `src/agentic_pentest/infrastructure/executors/shadow_cloner.py` | Automatically clones object before destructive PUT/DELETE (COMPLETED) |
| **T-009** | Verification | Implement 3-Way Differential Invariant Oracle | DONE | T-002,T-007 | 4d | `src/agentic_pentest/application/use_cases/verify_differential.py` | Proven zero false-positive on crAPI vehicle location BOLA (COMPLETED) |
| **T-010** | Verification | Build Zero-Dependency PoC Generator | DONE | T-009 | 2d | `src/agentic_pentest/application/use_cases/generate_poc.py` | Emits standalone `reproduce_poc.py` runnable with pure requests (COMPLETED) |
| **T-011** | Planning | Implement LiteLLM Reasoning Adapter & Prompts | DONE | T-001 | 3d | `src/agentic_pentest/infrastructure/reasoning/litellm_client.py` | Connects Claude/GPT/DeepSeek, parses structured JSON plans (COMPLETED) |
| **T-012** | Planning | Implement Evidence-Guided Adaptive Planner | DONE | T-005,T-011 | 4d | `src/agentic_pentest/application/use_cases/plan_next_action.py` | Dynamically updates plan based on evidence graph observations (COMPLETED) |
| **T-013** | SSDLC | Implement SARIF 2.1.0 Exporter with Code Fixes | DONE | T-010 | 2d | `src/agentic_pentest/application/use_cases/export_sarif.py` | Validated by Microsoft SARIF validator tool (COMPLETED) |
| **T-014** | Presentation | Build Typer CLI interface (`agentic-pentest`) | DONE | T-012 | 2d | `src/agentic_pentest/presentation/cli.py` | `agentic-pentest run --spec ... --target ...` works cleanly (COMPLETED) |
| **T-015** | Benchmark | Setup automated crAPI test harness & Baselines | DONE | T-014 | 5d | `src/agentic_pentest/evaluation/crapi_runner.py` | Runs B0 (Schemathesis), B1 (Plain LLM), B3 (Proposed) (COMPLETED) |
| **T-016** | Evaluation | Compute Metrics (Precision, Recall, RPCF, F1) | DONE | T-015 | 3d | `src/agentic_pentest/evaluation/evaluate_metrics.py` | Generates LaTeX tables, boxplots and p-value statistical tests (COMPLETED) |
| **T-017** | Intelligence | System 1 Reflexive Decision Engine & Prompt Guard | DONE | T-011 | 2d | `src/agentic_pentest/infrastructure/reasoning/jev_decision_engine.py` | Sub-50ms non-autoregressive decision model + injection sanitizer (COMPLETED) |
| **T-018** | OSINT | Attack Surface Discovery & Cloud Bucket Leakage | DONE | T-003 | 2d | `src/agentic_pentest/infrastructure/discovery/osint_scanner.py` | crt.sh/subfinder subdomains, S3/GCS/Azure leakage scanner (COMPLETED) |
| **T-019** | Anonymity | Dynamic Proxy Rotator & IP Reputation Verifier | DONE | T-007 | 2d | `src/agentic_pentest/infrastructure/proxy/proxy_rotator.py` | Round-robin, fastest, and health-weighted proxy failover (COMPLETED) |
| **T-020** | Invariants | Extended Semantic Invariants & Pure Stdlib PoC | DONE | T-002,T-010 | 2d | `src/agentic_pentest/domain/invariants.py` | SSRF, Race condition TOCTOU, JWT none + urllib.request PoC (COMPLETED) |
| **T-021** | Persistence | Lossless Compaction, SQLite WAL & autoDream | DONE | T-006 | 2d | `src/agentic_pentest/application/orchestration/context_compactor.py` | Bounded <16k token sliding window + SQLite WAL mode (COMPLETED) |
| **T-022** | Scale | Threat Intel & Multi-Target Swarm Workers | DONE | T-005 | 2d | `src/agentic_pentest/application/orchestration/swarm_orchestrator.py` | Bounded concurrent audit of 10+ endpoints with graph lock (COMPLETED) |
| **T-023** | Operator UI | Rich TUI Canvas & SARIF 2.1.0 with CVSS v3.1 | DONE | T-013,T-014 | 2d | `src/agentic_pentest/presentation/tui/terminal_canvas.py` | Live terminal DAG cards, telemetry gauges, and CVSS metadata (COMPLETED) |
| **T-024** | Resilience | Tool-Call Repair, Net Policy & Semantic Grepper | DONE | T-001 | 2d | `src/agentic_pentest/infrastructure/reasoning/tool_call_repair.py` | Deterministic JSON repair, RFC1918 scope, and source grepper (COMPLETED) |
| **T-025** | Verification | Multi-Agent Consensus Voting Engine & Domain Veto | DONE | T-009 | 2d | `src/agentic_pentest/application/orchestration/consensus_verifier.py` | 3 subagents, 2/3 consensus, domain invariant veto for BOLA/BFLA (COMPLETED) |
| **T-026** | Hermetic CI | Offline VCR / HAR Cassette Recorder & Replay | DONE | T-007 | 2d | `src/agentic_pentest/infrastructure/executors/vcr_recorder.py` | Hermetic execution without live network/container dependency (COMPLETED) |
| **T-027** | Governance | HITL Checkpoint `/save` & `/resume` + Approval Gate | DONE | T-014 | 2d | `src/agentic_pentest/presentation/chat.py` | Session rollback, state export, mutating confirmation gate (COMPLETED) |
| **T-028** | Benchmark | 41-Case Eval Dataset, Gold Labels & SE373 Deliverables | DONE | T-015 | 3d | `evals/questions/questions.jsonl`, `docs/DEMO_SCRIPT.md` | Full 41 cases (36 func + 5 sec), gold labels, 15-min demo script (COMPLETED) |
| **T-029** | Safety | Enterprise Rules of Engagement & Rate Limiting Guard | DONE | T-007 | 2d | `src/agentic_pentest/domain/safety/rules_of_engagement.py` | Pre-flight path blocker, token bucket rate limiter, RoEViolationError (COMPLETED) |
| **T-030** | Intelligence | Coverage Ledger, RFC 7230 Raw PoC & Dead-End Pruner | DONE | T-010,T-012 | 2d | `src/agentic_pentest/domain/coverage_ledger.py` | Attack surface audit ledger, 6-format PoC, automated DAG backtracking (COMPLETED) |
| **T-031** | Observability | OpenTelemetry Execution Tracer & Cost Accounting | DONE | T-001 | 2d | `src/agentic_pentest/domain/telemetry/tracer.py` | Nanosecond spans, token tracker, dynamic model pricing, budget alert (COMPLETED) |
| **T-032** | Compliance | OWASP API Top 10 & MITRE ATT&CK Threat Matrix | DONE | T-001 | 2d | `src/agentic_pentest/domain/safety/threat_matrix.py` | Full taxonomy mapping: OWASP API 2023, MITRE ATT&CK, CWE & CVSS v3.1 (COMPLETED) |
| **T-033** | Orchestration | 6-Stage Attack Chain Lifecycle State Machine | DONE | T-012 | 2d | `src/agentic_pentest/application/orchestration/attack_chain.py` | Finite state machine with stage invariants and rollback safety (COMPLETED) |


