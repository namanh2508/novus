# MASTER AGENTIC PENTEST OS: SOTA IMPLEMENTATION PLAN & MIGRATION BLUEPRINT

> **Living Architectural Roadmap & Capability Extraction Matrix**  
> Documenting the complete synthesis, refactoring, and integration of cutting-edge agentic pentesting architectures from:
> - `repos/` (14 Core SOTA Pentest Engines)
> - `repos/tmp/` (49 Specialized Toolkits & Frameworks)
> - `analyst/repos-agentic/` (`oh-my-pi`, `openclaw`, `opencode`, `hermes-agent`, `for-learn-claude-cli`)
> - `analyst/abc/` (`NanoJev`, `laya`, `jevgrep`, `memsearch`, `agent-beacon`, `single-agent-loop-kit`, `awesome-jev`)

---

## 1. Executive Summary & Architectural Vision

The mission of this repository is to build an **Evidence-Guided, Autonomous Agentic Web/API Pentesting Operating System**. Rather than functioning as a naive chat wrapper or an unconstrained scanner, the system maintains a unified, state-aware **Evidence Graph (NetworkX + SQLite WAL)**, executes **Dual-Brain Hypothesis Planning**, and independently validates all findings via a **3-Way Differential Invariant Oracle** with **Zero False-Positive Verification**.

### The Core Architectural Paradigm: Dual-Brain Pentest Agent
```
                          ┌────────────────────────────────────────────────────────┐
                          │               UNSTRUCTURED TARGET STATE                │
                          │   (Endpoints, Cookies, Headers, ASTs, HTTP Responses)  │
                          └───────────────────────────┬────────────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
        [SYSTEM 1: Reflexive Decision Engine]                         [SYSTEM 2: Strategic Reasoning Engine]
         (Jev / Laya / NanoJev - Sub-50ms)                             (Claude 3.7 / GPT-4o / DeepSeek)
                       │                                                             │
        • Tool dispatch & candidate selection                         • Complex multi-stage attack chaining
        • Safety & Read-only authorization gates                      • Novel business logic hypothesis tree
        • Anti-loop oscillation & stuck checks                        • Target architecture threat modeling
        • Rapid finding severity triage & rubric                      • Semantic remediation patch synthesis
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                                                      ▼
                          ┌────────────────────────────────────────────────────────┐
                          │          EVIDENCE-GUIDED EXECUTION & VERIFICATION      │
                          ├────────────────────────────────────────────────────────┤
                          │ • DeceptionGuard (Canarytokens & Honeypot Evasion)     │
                          │ • Blast Radius Guard (Shadow Clone & Rollback Journal) │
                          │ • 3-Way Differential Oracle (Zero False-Positives)     │
                          │ • Zero-Dependency Reproducible PoC Generator           │
                          └────────────────────────────────────────────────────────┘
```

---

## 2. Resource Deconstruction & Feature Inventory

### 2.1. From `analyst/repos-agentic/` (Production Agent Platforms)

| Source Repository | Core Module / Technology | Target Integration in `agentic_pentest` | Implementation Status |
| :--- | :--- | :--- | :--- |
| **`oh-my-pi`** | `packages/snapcompact` | `application/orchestration/context_compactor.py`: Sliding-window snapshot compaction of HTTP evidence without losing raw bytes. | **Completed (Phase 5)** |
| | `packages/tui` | `presentation/tui/`: Rich interactive terminal interface with live execution cards, progress bars, and hotkeys. | **Completed (Phase 7)** |
| | `crates/pi-ast` | `infrastructure/discovery/sast_bridge.py`: Rapid AST regex extraction for endpoint controllers and route decorators. | **Completed** |
| **`openclaw`** | `packages/worker-runtime` | `infrastructure/executors/worker_runtime.py`: Process isolation and memory heap management for long-running pentest campaigns. | **Completed** |
| | `packages/tool-call-repair` | `infrastructure/reasoning/tool_call_repair.py`: Deterministic recovery and JSON syntax repair for malformed model outputs. | **Completed** |
| | `packages/net-policy` | `domain/safety/net_policy.py`: IP/CIDR scope boundary enforcement and forbidden private network tripwires. | **Completed** |
| **`opencode`** | `packages/http-recorder` | `infrastructure/interception/http_recorder.py`: Bit-for-bit HTTP request/response journaling for deterministic PoC replay. | **Completed** |
| | `packages/effect-drizzle-sqlite` | `infrastructure/storage/sqlite_session_store.py`: Transactional SQLite persistence with schema migrations. | **Completed** |
| **`hermes-agent`** | `hermes_state_wal.py` | `infrastructure/storage/sqlite_audit_store.py`: WAL mode sqlite persistence ensuring zero database lockups during concurrent fuzzing. | **Completed (Phase 5)** |
| | `hermes_state_pidns.py` | `infrastructure/executors/kali_runner.py`: Process group isolation for subprocess CLI tool invocation. | **Completed** |
| **`for-learn-claude-cli`** | `microCompact` | `application/orchestration/evidence_compressor.py`: Compresses verbose tool output while strictly preserving factual finding tokens. | **Completed (Phase 5)** |
| | `autoDream` | `application/orchestration/background_dreamer.py`: Offline idle-time reflection consolidating graph insights into knowledge rules. | **Completed (Phase 5)** |

---

### 2.2. From `analyst/abc/` (System 1 Decision Models & Agent Memory)

| Source Repository | Core Module / Technology | Target Integration in `agentic_pentest` | Implementation Status |
| :--- | :--- | :--- | :--- |
| **`NanoJev` & `laya`** | Non-autoregressive decision model | `infrastructure/reasoning/jev_decision_engine.py`: Sub-50ms typed decisions (`Choice`, `Score`, `Noul`) with calibrated confidence. | **Completed (`9c11702`)** |
| **`awesome-jev`** | Confidence-Gated Escalation | `application/orchestration/dual_brain_router.py`: Fast-path execution when confidence $\ge 0.85$; escalate to System 2 when $< 0.85$. | **Completed (`9c11702`)** |
| **`single-agent-loop-kit`** | Single Agent Loop + Skills | `application/skills/skill_manager.py`: Main agent loop loading specialized playbooks on-demand, cutting prompt bloat by 80%. | **Completed** |
| **`memsearch` & `agent-beacon`** | Markdown Memory + Reranking | `infrastructure/storage/episodic_knowledge.py`: Cross-engagement durable knowledge, WAF bypass memory, and dead-class skip logic. | **Completed (`4847321`)** |
| **`jevgrep`** | Semantic code search | `infrastructure/discovery/semantic_grepper.py`: Identifies vulnerable controller routines without ingesting entire codebases. | **Completed** |

---

### 2.3. From `repos/` & `repos/tmp/` (Specialized Pentesting Frameworks)

| Source Repository | Core Capability | Target Module in `agentic_pentest` | Implementation Status |
| :--- | :--- | :--- | :--- |
| **`Leousum__PoCForge`** | Semantic Invariant Solver | `domain/invariants.py`: `is_semantic_error_response` filtering fake HTTP 200 responses with error bodies. | **Completed** |
| **`BitterSecurity__Decepticon`** | Canary & Honeypot Detection | `domain/deception_guard.py`: Tripwire filtering for canarytokens, honey URIs, and decoy headers. | **Completed** |
| **`0x4m4__hexstrike-ai`** | 100+ OS CLI Tools Discovery | `infrastructure/tools_kali/structured_bridge.py`: PATH scanning for `nmap`, `ffuf`, `nuclei`, `sqlmap`, `katana`, `curl`. | **Completed (`9c11702`)** |
| **`google__mantis`** | Attack Surface Management | `infrastructure/discovery/osint_scanner.py`: Subdomain enumeration, dangling CNAME takeover, and cloud bucket leakage. | **Completed (`4847321`)** |
| **`elementalsouls__Claude-BugHunter`**| Dead-Class Pruning | `infrastructure/storage/episodic_knowledge.py`: Negative finding tracker skipping hopeless test classes after 5 failures. | **Completed (`4847321`)** |
| **`CyberStrikeus__CyberStrike`** | HackBrowser Stealth Evasion | `infrastructure/discovery/playwright_crawler.py`: `navigator.webdriver` masking and anti-bot fingerprint spoofing. | **Completed (`4847321`)** |
| **`jfreemansh__Anonproxy`** | Proxy Rotation & WAF Bypass | `infrastructure/proxy/proxy_rotator.py`: Dynamic Tor / SOCKS5 upstream rotation with IP reputation tracking. | **Completed (Phase 3)** |
| **`Armur-Ai__Pentest-Swarm-AI`** | Multi-Target Swarm Workers | `application/orchestration/swarm_orchestrator.py`: Concurrent task worker pool for subnet and multi-domain pentests. | **Completed (Phase 6)** |
| **`zgsfsec__Full-Chain-Sentinel`** | Threat Intel & OpenAPI Synth | `infrastructure/discovery/threat_intel_bridge.py`: FOFA, 360 Quake, Hunter integration & OpenAPI 3.0 auto-generation. | **Completed (Phase 6)** |

---

## 3. Work Breakdown Structure (WBS) & Phased Milestones

```
[Phase 1] Dual-Brain Intelligence & System 1 Gating       ──> [COMPLETED: Commit 9c11702]
[Phase 2] OSINT, Attack Surface & Anti-Bot Stealth         ──> [COMPLETED: Commit 4847321]
[Phase 3] Proxy Rotation, WAF Bypass & Traffic Anonymity   ──> [COMPLETED: 100% Tests Pass]
[Phase 4] Semantic Invariant Expansion & Zero-Dep PoC      ──> [COMPLETED: 100% Tests Pass]
[Phase 5] Lossless Compaction, SQLite WAL & autoDream      ──> [COMPLETED: 100% Tests Pass]
[Phase 6] Threat Intel Platforms & Multi-Target Swarms     ──> [COMPLETED: 100% Tests Pass]
[Phase 7] Unified TUI & Live SSE Attack Flow Canvas        ──> [COMPLETED: 100% Tests Pass]
```

### Phase 3: Proxy Rotation, WAF Bypass & Traffic Anonymity
- **Goal**: Prevent IP bans, bypass geo-blocking, and cycle upstream proxy nodes cleanly.
- **Components**:
  - `src/agentic_pentest/infrastructure/proxy/proxy_rotator.py`: Implements round-robin and latency-weighted proxy selection (HTTP, SOCKS5, Tor).
  - `src/agentic_pentest/infrastructure/proxy/ip_reputation.py`: Measures health score and egress IP latency before sending exploit payloads.
- **Definition of Done (DoD)**:
  - 100% unit test coverage in `tests/unit/test_proxy_rotator.py`.
  - Upstream proxy failover executes with zero unhandled exceptions.

### Phase 4: Semantic Invariant Expansion & Zero-Dependency PoC
- **Goal**: Expand invariant coverage across Race Conditions, SSRF, JWT, and GraphQL.
- **Components**:
  - `src/agentic_pentest/domain/invariants.py`: Add `check_ssrf_metadata_invariant`, `check_race_condition_toctou_invariant`, `check_jwt_key_confusion_invariant`.
  - `src/agentic_pentest/application/use_cases/generate_poc.py`: Standalone Python scripts strictly utilizing `urllib.request` or `requests` (zero proprietary framework imports).
- **Definition of Done (DoD)**:
  - Every verified finding produces a standalone executable `reproduce_poc.py` that successfully triggers on crAPI fixtures.

### Phase 5: Lossless Compaction, SQLite WAL & autoDream
- **Goal**: Support 100+ turn continuous autonomous pentesting without context overflow or memory leaks.
- **Components**:
  - `src/agentic_pentest/application/orchestration/context_compactor.py`: Implements `microCompact` (compresses raw responses into factual fingerprints).
  - `src/agentic_pentest/application/orchestration/background_dreamer.py`: Consolidates successful exploit paths into reusable heuristics during LLM thinking gaps.
  - Enable `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` across all SQLite stores.
- **Definition of Done (DoD)**:
  - Context size remains bounded $< 16,000$ tokens regardless of crawl depth.

### Phase 6: Threat Intel Platforms & Multi-Target Swarms
- **Goal**: Enterprise-scale external attack surface mapping and parallel microservice auditing.
- **Components**:
  - `src/agentic_pentest/infrastructure/discovery/threat_intel_bridge.py`: Query FOFA, 360 Quake, and Hunter for exposed assets.
  - `src/agentic_pentest/application/orchestration/swarm_orchestrator.py`: Async task pool distributing endpoint subsets across worker coroutines.
  - `src/agentic_pentest/infrastructure/discovery/openapi_reconstructor.py`: Auto-generates standard OpenAPI 3.0 YAML from observed traffic.
- **Definition of Done (DoD)**:
  - Concurrent audit of 10 endpoints executes without race conditions in Evidence Graph.

### Phase 7: Unified TUI & Live SSE Attack Flow Canvas
- **Goal**: Professional operator interface combining terminal agility with visual web control.
- **Components**:
  - `src/agentic_pentest/presentation/tui/`: Textual-based interactive console with task cards, latency gauges, and log streams.
  - `src/agentic_pentest/infrastructure/proxy/interception_dashboard.py`: Port 8090 SSE attack chain graph with real-time node state color coding (UNTESTED, EXECUTING, VERIFIED, CLEAN).
  - `src/agentic_pentest/presentation/cli/sarif_exporter.py`: Full SARIF 2.1.0 output with CVSS v3.1 vector calculations.
- **Definition of Done (DoD)**:
  - Dashboard streams live DAG updates with sub-100ms latency.
  - SARIF schema validates against official OASIS SARIF v2.1.0 specification.

---

## 4. Non-Negotiable Architectural Invariants

1. **Planner & Verifier Decoupling**:
   - The Planner (`AdaptivePlanner`, `AutonomousAttackOrchestrator`) hypothesizes what to test.
   - The Verifier (`DifferentialVerifier`, `DifferentialTriplet`) independently determines whether the invariant holds.
   - The Planner MUST NEVER generate or override a `Finding`. Sole authority belongs to the Verifier.

2. **Clean Architecture Inward Rule**:
   - `domain/` contains pure entities, exceptions, and invariants. It MUST NOT import `httpx`, `litellm`, `sqlite3`, `playwright`, or framework libraries.
   - `application/` depends only on `domain/` and abstracts external drivers via `interfaces/`.
   - `infrastructure/` implements ports defined in `application/interfaces/`.

3. **Blast Radius & Mutation Protection**:
   - Every destructive HTTP method (`DELETE`, `PUT`, `PATCH`) executed against an object MUST be preceded by a **Shadow Object Clone** or registered in the rollback journal.

4. **Zero-Dependency Reproducible PoC**:
   - Every confirmed `Finding` MUST automatically generate a self-contained `reproduce_poc.py` executable directly via `python reproduce_poc.py` using only Python standard library or `requests`.

5. **Prompt Injection & Context Boundary Isolation**:
   - Untrusted target web data (HTTP bodies, headers, error messages) MUST ALWAYS pass through `JevPromptInjectionSanitizer` before reaching decision models.

---

## 5. Verification Commands & Definition of Done

Every implementation phase must satisfy the following pipeline before merging:
```powershell
# 1. Format and Linter validation (0 errors, 0 warnings)
.venv\Scripts\ruff check .
.venv\Scripts\ruff format --check .

# 2. Strict static type analysis (0 errors across all source files)
.venv\Scripts\mypy --strict src/

# 3. Unit test suite execution (100% passing)
.venv\Scripts\pytest -q tests/unit/

# 4. Zero False-Positive differential oracle verification
.venv\Scripts\pytest -v tests/unit/test_semantic_invariants.py
.venv\Scripts\pytest -v tests/unit/test_jev_decision_engine.py
.venv\Scripts\pytest -v tests/unit/test_osint_scanner.py
```
