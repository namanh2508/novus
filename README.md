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
Launch the interactive agentic session featuring the Cyber-Whale mascot terminal UX:
```powershell
agentic-pentest chat --target http://localhost:8888
```

Quick-action command shortcuts in interactive chat:
- `0` / `status`   : Show current target, authentication, and permission state
- `1` / `crawl`    : SPA headless crawl & JS bundle endpoint harvesting
- `2` / `sast`     : AST route extraction from backend source code
- `3` / `scan`     : 3-Way Differential Invariant verification (BOLA / BFLA)
- `4` / `race`     : Burst concurrency audit for TOCTOU & coupon reuse race conditions
- `5` / `graphql`  : GraphQL introspection and batching DoS exposure probe
- `6` / `jwt`      : JWT `alg: none` bypass, signature stripping & weak secret cracker
- `7` / `secrets`  : Sensitive file probe (`.env`, `.git`, heapdumps) and API key scanner
- `8` / `ai-guard` : AST Taint Reachability & Guard Coverage risk evaluation on code
- `9` / `diff`     : Generate unified git diff remediation patches
- `10` / `eval`    : Run 30-case SE373 Benchmark test suite (Accuracy EX & Latency)
- `guide`          : Show full pentest operator phase matrix
- `learn <rule>`   : Inject domain constraints into active episodic memory
- `compact`        : Toggle between compact summarized view and verbose audit stream

---

## 🔌 Model Context Protocol (MCP) Integration

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
