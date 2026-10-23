# Evidence-Guided Agentic Web/API Pentesting

[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Clean%20Architecture-4--Layer-green.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Benchmark](https://img.shields.io/badge/Benchmark-OWASP%20crAPI-red.svg)](https://github.com/OWASP/crAPI)
[![Go](https://img.shields.io/badge/Go-Prober%20v1.0-cyan.svg)](https://golang.org)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An autonomous, adaptive, and evidence-verified penetration testing framework designed to discover and mathematically prove **Broken Object Level Authorization (BOLA/IDOR)**, **Broken Function Level Authorization (BFLA)**, and **API Business Logic Flaws** without false positives.

---

## 🎯 Key Differentiators

1. **Decoupled Planner & Verifier**:
   - The **Adaptive Planner** selects targets and hypotheses based on an in-memory Evidence Graph.
   - The **Differential Verifier** independently judges vulnerability verdicts based on a **3-Way Differential Invariant Oracle** ($O_{legit}$, $O_{cross}$, $O_{anon}$).
2. **Hybrid Architecture (Python + Go)**:
   - **Python 3.12+**: Agentic reasoning, Knowledge Graph (NetworkX + SQLite), Clean Architecture domain models, and LLM semantic diffing.
   - **Go Prober (`tools/fastprobe`)**: High-speed concurrent wire-level HTTP replay and noise-masked SHA-256 fingerprinting.
3. **Shadow Object Mutation Isolation**:
   - Never issues blind destructive mutations (`PUT`, `DELETE`) on real data. Uses automated shadow cloning and rollback journals.
4. **Zero-Dependency Reproducible PoC**:
   - Automatically emits standalone `reproduce_poc.py` executable scripts using standard Python (`requests`/`urllib3`).

---

## 🏗️ Architecture Overview

```
src/agentic_pentest/
├── domain/                  # Pure entities, value objects, and invariant checks
├── application/             # Use cases, planner, verifier, orchestrator
│   ├── planner/             # Hypothesis generator and DAG task selector
│   ├── verifier/            # 3-Way Differential Invariant Oracle
│   ├── poc/                 # Zero-dependency PoC script generator
│   └── interfaces/          # Clean Architecture ports (HTTP, Graph, LLM, Store)
├── infrastructure/          # Adapters, SQLite, NetworkX, Respx, Go Prober
│   ├── graph/               # Hybrid NetworkX + SQLite Evidence Graph
│   ├── playbooks/           # Machine-executable YAML attack playbooks
│   └── adapters/            # HTTPX and Go fastprobe subprocess adapters
└── presentation/            # CLI and SARIF 2.1.0 report exporter

tools/fastprobe/             # High-concurrency Go HTTP prober & response hasher
deployments/                 # Docker Compose benchmark lab (OWASP crAPI)
benchmarks/                  # Ground truth test datasets & evaluation harness
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `venv`
- Go 1.22+ (for `fastprobe`)
- Docker & Docker Compose (for benchmark target)

### 2. Install Dependencies
```powershell
# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"
```

### 3. Build Go Prober Engine
```powershell
cd tools/fastprobe
go build -o fastprobe.exe main.go
cd ../..
```

### 4. Start Local Benchmark Target (crAPI)
```powershell
# Start OWASP crAPI containers
.\deployments\run_crapi.ps1 -Action start

# Check status
.\deployments\run_crapi.ps1 -Action status
### 5. Run Verification Test Suite
```powershell
# Run fast unit tests (99+ tests)
$env:PYTHONPATH="src"; pytest -q tests/unit/

# Run lint and strict type checking (0 errors)
ruff check .
mypy --strict src/
```

### 6. Interactive Chat & Operator Terminal
Launch the interactive agentic session featuring the compact Cyber-Whale mascot terminal UX:

**Method 1: Direct Python module execution (recommended across all platforms):**
```powershell
# Windows PowerShell
.venv\Scripts\python -m agentic_pentest.presentation.cli chat --target http://localhost:8888

# Linux / macOS
./.venv/bin/python -m agentic_pentest.presentation.cli chat --target http://localhost:8888
```

**Method 2: Using installed entrypoint (after `pip install -e .`):**
```powershell
agentic-pentest chat --target http://localhost:8888
```

---

## 🛠️ Complete CLI Command Catalog (25 Commands)

Execute any standalone tool directly from the terminal or CI/CD pipelines via `.venv\Scripts\python -m agentic_pentest.presentation.cli <command>`:

| Command | Category | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| `chat` | REPL | Launch interactive chat session with Cyber-Whale mascot | `python -m agentic_pentest.presentation.cli chat --target http://localhost:8888` |
| `scan` | Autonomous | Run full 3-Way Differential Oracle verification on OpenAPI spec | `python -m agentic_pentest.presentation.cli scan --spec openapi.json` |
| `loop` | Autonomous | Multi-turn autonomous pentest loop with hypothesis generation | `python -m agentic_pentest.presentation.cli loop --target http://localhost:8888` |
| `multi-agent` | Orchestration | Orchestrate 3 specialized agents (Recon, Verifier, Patch) | `python -m agentic_pentest.presentation.cli multi-agent --target http://localhost:8888` |
| `plan` | Planning | Interactive OWASP Top 10 hypothesis planning session | `python -m agentic_pentest.presentation.cli plan --target http://localhost:8888` |
| `race` | Audit (UC-12) | Burst concurrency audit for TOCTOU & coupon reuse bugs | `python -m agentic_pentest.presentation.cli race --endpoint http://localhost:8888/api/coupon` |
| `graphql` | Audit (UC-13) | Probe GraphQL Introspection exposure & batching DoS | `python -m agentic_pentest.presentation.cli graphql --target http://localhost:8888` |
| `jwt` | Audit (UC-14) | Probe `alg: none`, signature stripping & crack weak HMAC | `python -m agentic_pentest.presentation.cli jwt --token <jwt_token>` |
| `secrets` | Audit (UC-15) | Probe sensitive paths (`.env`, `.git`) & scan API keys | `python -m agentic_pentest.presentation.cli secrets --url http://localhost:8888` |
| `ai-guard` | Code Guard | AST Taint Reachability & Guard Coverage risk evaluation | `python -m agentic_pentest.presentation.cli ai-guard src/app.py` |
| `crawl` | Recon | Headless SPA crawler harvesting endpoints from JS bundles | `python -m agentic_pentest.presentation.cli crawl --url http://localhost:8888` |
| `sast` | Recon | AST route extractor for FastAPI / Express / Flask code | `python -m agentic_pentest.presentation.cli sast src/` |
| `proxy` | Interception | Real-time traffic sniffer and MITM proxy | `python -m agentic_pentest.presentation.cli proxy --port 8080` |
| `cve` | Intelligence | Advisory intelligence scanning technology fingerprints | `python -m agentic_pentest.presentation.cli cve --target http://localhost:8888` |
| `audit-headers` | Audit | Audit HSTS, CSP, and defensive HTTP response headers | `python -m agentic_pentest.presentation.cli audit-headers http://localhost:8888` |
| `audit-cookies` | Audit | Audit HttpOnly, SameSite, Secure cookie attributes | `python -m agentic_pentest.presentation.cli audit-cookies http://localhost:8888` |
| `audit-cors` | Audit | Detect wildcard Access-Control-Allow-Origin & reflections | `python -m agentic_pentest.presentation.cli audit-cors http://localhost:8888` |
| `audit-login` | Audit | Audit login rate limiting and brute force protection | `python -m agentic_pentest.presentation.cli audit-login http://localhost:8888/api/login` |
| `seed-crapi` | Benchmark | Seed OWASP crAPI benchmark environment (Alice/Bob/Vehicles) | `python -m agentic_pentest.presentation.cli seed-crapi --target http://localhost:8888` |
| `eval` | Benchmark | Run 30-case SE373 evaluation suite measuring Accuracy EX | `python -m agentic_pentest.presentation.cli eval --spec evals/questions/questions.jsonl` |
| `demo-server` | Lab | Start live mock target server for offline demonstration | `python -m agentic_pentest.presentation.cli demo-server --port 8888` |
| `export-vault` | Reporting | Export evidence, attack graphs & findings to Obsidian Vault | `python -m agentic_pentest.presentation.cli export-vault --output reports/vault` |
| `sessions` | Audit Trail | Inspect persisted SQLite sessions and evidence graphs | `python -m agentic_pentest.presentation.cli sessions` |
| `interactive` | Planning | Multi-turn goal-driven pentest planner REPL | `python -m agentic_pentest.presentation.cli interactive` |
| `mcp-server` | Integration | Launch FastMCP server over stdio for Claude Code / IDEs | `python -m agentic_pentest.presentation.cli mcp-server` |

---

## ⚡ Interactive Chat REPL Commands & Numeric Shortcuts

Inside the `chat` operator terminal, use numeric keys or direct command names for instant action:

- **`0` / `status`**   : Display active target, principal sessions (Alice/Bob), and Safe-Mode status.
- **`1` / `crawl`**    : Run headless crawler on client JS bundles to extract hidden API routes.
- **`2` / `sast`**     : Run AST route extractor on backend source files.
- **`3` / `scan`**     : Run 3-Way Differential Invariant verification for BOLA / BFLA.
- **`4` / `race`**     : Dispatch synchronized concurrent burst requests to audit TOCTOU race conditions.
- **`5` / `graphql`**  : Probe GraphQL schema introspection exposure and batching DoS limits.
- **`6` / `jwt`**      : Test JWT `alg: none` bypass, signature stripping, and crack weak secrets.
- **`7` / `secrets`**  : Probe sensitive paths (`.env`, `.git/HEAD`, heapdumps) and scan API key entropy.
- **`8` / `ai-guard`** : Calculate AST Tree Coverage and Taint Reachability risk scores on code.
- **`9` / `diff`**     : Generate unified Git diff remediation patches for all verified findings.
- **`10` / `eval`**    : Run the 30-case SE373 Benchmark test suite and calculate Task Accuracy (EX).
- **`guide`**          : Display the 6-phase S-SDLC pentest execution matrix.
- **`learn <rule>`**   : Inject an offensive invariant into `MEMORY.md` and SQLite episodic memory.
- **`compact`**        : Toggle between compact summarized view and verbose raw audit stream.
- **`vault`**          : Export findings and graph relationships to Obsidian Markdown Vault (`reports/vault/`).
- **`sarif`**          : Export findings to OASIS SARIF 2.1.0 format for GitHub Code Scanning alerts.
- **`poc`**            : Generate standalone, zero-dependency reproducible Python exploit scripts.
- **`seed`**           : Seed test principals (Alice/Bob) and resources into the target lab.
- **`headers`**        : Audit HSTS, CSP, and defensive security headers.
- **`cookies`**        : Audit HttpOnly, SameSite, and Secure flags on session cookies.
- **`cors`**           : Audit CORS origin reflection and credentials allowance.
- **`login`**          : Audit login rate limiting and brute force countermeasures.
- **`ask <query>`**    : Consult the AI reasoning engine for advice or next steps.
- **`demo`**           : Start the mock demo target server.
- **`exit` / `quit`**  : Exit the interactive operator session.

---

## 🧠 Two-Tier Memory Architecture & Topic Splitting

Aligned with **SE373.R11 (Agentic AI Engineering)** and the **12-Factor Agent** principles:

### 1. Bounded Tier 1 Working Index (`MEMORY.md`)
- `MEMORY.md` lives in the project root as a human-readable, bounded Markdown file ($< 2,200$ characters / $< 500$ tokens).
- It is injected as a **frozen snapshot** into the system prompt at cold-start to prevent context bloat and preserve prefix caching.

### 2. Handling Memory Overflow: The Topic Splitting Pattern
When learned knowledge exceeds the 2,200-character budget:
- `MEMORY.md` acts strictly as an **Index Table of Contents** pointing to topic-specific files.
- Granular findings, schemas, and extensive traces are automatically offloaded to:
  `memories/topics/<category>_<target>.md` (e.g., `memories/topics/bola_localhost_8888.md`, `memories/topics/jwt_invariants.md`).
- In `MEMORY.md`, a single compact line is kept:
  `- [JWT] Weak HMAC secret cracked -> see memories/topics/jwt_invariants.md`
- **Compaction & Deduplication**: When new rules supersede old constraints, the agent automatically marks old rules `[SUPERSEDED]` and removes redundant entries to stay within the character budget.
- **Tier 2 Backing Store**: All raw packets, hash chains, and session history remain persisted in SQLite (`agent_sessions.db` & `episodic_knowledge.db`) with FTS5 full-text indexing for cross-session semantic search.

This repository exposes **14 production-grade pentest tools** over the FastMCP protocol, enabling direct tool execution inside AI developer environments like **Claude Code**, **Cursor**, **Antigravity**, or **Roo/Cline**:

```powershell
# Start FastMCP server on stdio
agentic-pentest mcp
```

### Exposed MCP Tools (14 Tools):
1. `audit_cookies`: Audit `HttpOnly`, `SameSite`, and `Secure` cookie attributes.
2. `audit_cors`: Detect wildcard `Access-Control-Allow-Origin` and credential reflections.
3. `audit_headers`: Audit `HSTS`, `CSP`, and defensive response headers.
4. `audit_login_bruteforce`: Verify rate limiting and exponential backoff on auth endpoints.
5. `audit_race_condition`: Probe concurrency race conditions via burst synchronization.
6. `audit_graphql_security`: Extract introspection schemas and probe batching DoS.
7. `audit_jwt_security`: Probe `alg: none`, signature stripping, and crack weak HMAC secrets.
8. `audit_secret_leak`: Discover `.env`, heapdumps, `.git`, and high-entropy API keys.
9. `audit_ai_code_security`: Calculate AST Tree Coverage and Taint Reachability risk scores.
10. `verify_bola`: Mathematically prove IDOR vulnerabilities with 3-Way Differential Oracle.
11. `verify_bfla`: Verify administrative privilege escalations across roles.
12. `generate_poc`: Generate zero-dependency reproducible Python exploit scripts.
13. `generate_patch`: Generate unified git diff patches and mitigation recommendations.
14. `run_benchmark`: Execute the 30-case evaluation harness against the target.

---

## 🐧 Cross-Platform Deployment (Kali Linux / Ubuntu / Windows)

The system features an adaptive execution engine:
- **Core Engine (Pure Python)**: Runs identically across **Kali Linux**, **Ubuntu**, and **Windows** without requiring system-level packages. HTTPX, SQLite, NetworkX, and AST analysis are 100% OS-agnostic.
- **External CLI Tools (`KaliCommandRunner`)**: Automatically detects tools (`nmap`, `ffuf`, `nuclei`) via `shutil.which()`.
  - On **Kali Linux**: Uses installed high-speed binaries with structured XML/JSON parsing.
  - On **Ubuntu / Windows**: Seamlessly falls back to internal pure-Python discovery (`SPADynamicCrawler`, `SASTBridgeRouteExtractor`) without crashing or requiring manual configuration.

---

## 📖 Living Context & Specifications

All deep technical specifications and operating instructions are documented in:
- `.context/AICONTEXT.md`: Scientific thesis, Research Questions (RQ1-RQ3), and mathematical formulations.
- `.context/BUSINESS.md`: Business domain, SSDLC integration, and compliance value proposition.
- `.context/FLOW.md`: End-to-end 4-phase operational workflow and Mermaid sequence diagrams.
- `.context/MODULES.md`: Detailed module contracts and interface specifications.
- `.context/ORCHESTRATION.md`: Multi-agent pairing between Antigravity (Architect) and GitHub Copilot (Coder).
- `ssdlc-agentic-spec/`: 8 full specification RFCs and Architecture Decision Records (ADRs).
