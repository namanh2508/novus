# TODOBASE.md — Work Breakdown Structure (WBS) & Task Roadmap

> **Methodology**: Milestone-driven, Test-first for core invariants, Clean Architecture strictness.  
> **Timeline**: 10-Week Academic MVP Plan.  

---

## WBS Task Matrix

| ID | Epic | Task Description | Priority | Dep | Estimate | Deliverable (File Path) | DoD (Definition of Done) |
|---|---|---|:---:|:---:|:---:|---|---|
| **T-001** | Foundation | Define pure Domain entities & exceptions | DONE | - | 2d | `src/agentic_pentest/domain/entities.py` | 100% type annotated, frozen dataclasses, 0 external imports (COMPLETED) |
| **T-002** | Foundation | Implement Semantic Diff & Invariant Checker | DONE | T-001 | 2d | `src/agentic_pentest/domain/invariants.py` | Passes unit tests with 10 synthetic JSON test pairs (COMPLETED) |
| **T-003** | Ingestion | Build OpenAPI 3.0 Parser & Endpoint Discovery | IN PROGRESS | T-001 | 3d | `src/agentic_pentest/infrastructure/discovery/openapi_parser.py` | Successfully extracts crAPI OpenAPI spec into TargetObjects |
| **T-004** | Ingestion | Implement Playbook Registry & YAML Validator | MUST | T-001 | 2d | `src/agentic_pentest/infrastructure/playbooks/registry.py` | Loads and validates `bola_read.yaml` against schema |
| **T-005** | Storage | Build NetworkX Evidence Graph Store | MUST | T-001 | 3d | `src/agentic_pentest/infrastructure/storage/networkx_graph.py` | Supports add_principal, add_object, query_paths with tests |
| **T-006** | Storage | Build SQLite Immutable Audit Trail Store | MUST | T-001 | 2d | `src/agentic_pentest/infrastructure/storage/sqlite_audit_store.py` | Stores raw HTTP request/response tuples with SHA-256 hash |
| **T-007** | Execution | Implement Async HTTPX Executor with Scope Guard | MUST | T-001 | 3d | `src/agentic_pentest/infrastructure/executors/httpx_executor.py` | Enforces URL allowlist, rate limits, raises ScopeViolationError |
| **T-008** | Execution | Build Shadow Object Cloner (Mutation Guard) | SHOULD | T-007 | 2d | `src/agentic_pentest/infrastructure/executors/shadow_cloner.py` | Automatically clones object before destructive PUT/DELETE |
| **T-009** | Verification | Implement 3-Way Differential Invariant Oracle | MUST | T-002,T-007 | 4d | `src/agentic_pentest/application/use_cases/verify_differential.py` | Proven zero false-positive on crAPI vehicle location BOLA |
| **T-010** | Verification | Build Zero-Dependency PoC Generator | MUST | T-009 | 2d | `src/agentic_pentest/application/use_cases/generate_poc.py` | Emits standalone `reproduce_poc.py` runnable with pure requests |
| **T-011** | Planning | Implement LiteLLM Reasoning Adapter & Prompts | MUST | T-001 | 3d | `src/agentic_pentest/infrastructure/reasoning/litellm_client.py` | Connects Claude/GPT/DeepSeek, parses structured JSON plans |
| **T-012** | Planning | Implement Evidence-Guided Adaptive Planner | MUST | T-005,T-011 | 4d | `src/agentic_pentest/application/use_cases/plan_next_action.py` | Dynamically updates plan based on evidence graph observations |
| **T-013** | SSDLC | Implement SARIF 2.1.0 Exporter with Code Fixes | SHOULD | T-010 | 2d | `src/agentic_pentest/application/use_cases/export_sarif.py` | Validated by Microsoft SARIF validator tool |
| **T-014** | Presentation | Build Typer CLI interface (`agentic-pentest`) | MUST | T-012 | 2d | `src/agentic_pentest/presentation/cli.py` | `agentic-pentest run --spec ... --target ...` works cleanly |
| **T-015** | Benchmark | Setup automated crAPI test harness & Baselines | MUST | T-014 | 5d | `tests/benchmarks/crapi_runner.py` | Runs B0 (Schemathesis), B1 (Plain LLM), B3 (Proposed) |
| **T-016** | Evaluation | Compute Metrics (Precision, Recall, RPCF, F1) | MUST | T-015 | 3d | `tests/benchmarks/evaluate_metrics.py` | Generates LaTeX tables, boxplots and p-value statistical tests |
