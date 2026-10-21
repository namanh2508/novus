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
```

### 5. Run Verification Test Suite
```powershell
# Run fast unit tests
pytest -q tests/unit/

# Run lint and type checking
ruff check .
mypy --strict src/
```

---

## 📖 Living Context & Specifications

All deep technical specifications and operating instructions are documented in:
- `.context/AICONTEXT.md`: Scientific thesis, Research Questions (RQ1-RQ3), and mathematical formulations.
- `.context/BUSINESS.md`: Business domain, SSDLC integration, and compliance value proposition.
- `.context/FLOW.md`: End-to-end 4-phase operational workflow and Mermaid sequence diagrams.
- `.context/MODULES.md`: Detailed module contracts and interface specifications.
- `.context/ORCHESTRATION.md`: Multi-agent pairing between Antigravity (Architect) and GitHub Copilot (Coder).
- `ssdlc-agentic-spec/`: 8 full specification RFCs and 5 Architecture Decision Records (ADRs).
