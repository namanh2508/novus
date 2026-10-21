# AGENTS.md

Operating instructions for any AI coding agent (Claude Code, Cursor, Antigravity, Roo/Cline, Codex) working in
this repository. Read this before reading or modifying code. The constraints below are non-negotiable — treat
them as invariants, not suggestions.

## 1. Project Overview & Architectural Identity

This repository implements **Evidence-Guided Agentic Web/API Pentesting**: an autonomous, adaptive, and
evidence-verified penetration testing framework specifically focused on **Broken Object Level Authorization (BOLA/IDOR)**,
**Broken Function Level Authorization (BFLA)**, and **API Business Logic Flaws**.

Unlike blind scanners (which fuzz payloads) or naive LLM wrappers (which call tools without state awareness),
this system maintains an **in-memory Evidence Graph (NetworkX + SQLite)**, executes **Hypothesis-Driven Planning**,
and validates every suspected vulnerability using a **3-Way Differential Invariant Oracle** to achieve
**Zero False-Positive Verification**.

### Primary Target & Benchmark
- Primary benchmark target: **OWASP crAPI** (Community Rest API) running locally via Docker Compose.
- Secondary targets: OWASP Juice Shop, PortSwigger API labs.

---

## 2. Environment, Build, Test & Lint Commands

```powershell
# Setup virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install runtime & dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run full test suite with coverage
pytest -v --cov=src/agentic_pentest tests/

# Run fast unit tests only (no docker / network dependencies)
pytest -q tests/unit/

# Run differential oracle verification tests
pytest -v tests/unit/test_differential_oracle.py

# Linting & Code formatting (must pass with 0 errors before committing)
ruff check .
ruff format --check .
mypy --strict src/
```

**Definition of Done (DoD) for any code edit**:
1. All unit tests pass (`pytest -q tests/unit/`).
2. `ruff check .` reports no errors or warnings.
3. `mypy --strict src/` reports no type-check failures.
4. No imports violate the **Clean Architecture Inward Dependency Rule**.

---

## 3. Non-Negotiable Engineering Invariants

1. **Planner & Verifier Decoupling**:
   - The `AdaptivePlanner` decides *what* hypothesis to test and what action to execute.
   - The `DifferentialVerifier` independently decides *whether* the test succeeded based on mathematical invariants and response diffing.
   - **Rule**: The Planner MUST NEVER determine or override a vulnerability verdict. The Verifier has sole authority over `Finding` generation.

2. **Clean Architecture Inward Rule**:
   - `domain/` contains pure entities and invariants. It MUST NOT import `httpx`, `litellm`, `sqlite3`, `pydantic_settings`, or any framework driver.
   - `application/` depends only on `domain/` and abstracts external I/O via `interfaces/`.
   - `infrastructure/` implements interfaces defined in `application/interfaces/`.

3. **Blast Radius & Mutation Protection**:
   - Every destructive operation (`DELETE`, `PUT`, `PATCH`) executed against an object MUST be preceded by a **Shadow Object Clone** or registered in the rollback journal.
   - Never issue arbitrary destructive HTTP calls against unseeded or root administrative entities.

4. **Zero-Dependency Reproducible PoC**:
   - Every confirmed `Finding` MUST automatically emit a standalone `reproduce_poc.py` script that can be executed directly with `python reproduce_poc.py` using only `requests` or `urllib3` (zero framework dependencies).

5. **Deterministic Evidence Audit Trail**:
   - Never log freeform LLM text as evidence. Every observation MUST store the raw HTTP request/response tuple, exact headers, latency, timestamp, and SHA-256 fingerprint.

---

## 4. Key Directory & Module Map

```
agent-pentest/
├── .context/                       # Living architectural & operational context
│   ├── AICONTEXT.md                # Scientific thesis, research questions & evidence boundary
│   ├── CODEBASE.md                 # Detailed module, class, and function catalog
│   ├── TODOBASE.md                 # Granular WBS task list, timeline & DoD
│   ├── TESTBASE.md                 # Test harness, crAPI fixtures & oracle test specs
│   └── STYLEBASE.md                # Typing standards, Clean Architecture rules, error types
├── ssdlc-agentic-spec/             # Complete technical specifications & RFCs
│   ├── 01-architecture-and-dataflow.md
│   ├── 02-mindset-and-threat-modeling.md
│   ├── 03-evidence-graph-and-data-model.md
│   ├── 04-playbook-spec-and-knowledge-base.md
│   ├── 05-safety-policy-and-scope-guard.md
│   ├── 06-differential-oracle-and-poc-spec.md
│   ├── 07-ssdlc-pipeline-and-devsecops.md
│   ├── 08-benchmark-and-evaluation-harness.md
│   └── decisions/                  # Architecture Decision Records (ADRs)
├── src/agentic_pentest/             # Production source code
│   ├── domain/                     # Pure business logic, entities, invariants
│   ├── application/                # Use cases, planner, verifier, orchestrator
│   ├── infrastructure/             # HTTPX, SQLite, NetworkX, LiteLLM adapters
│   └── presentation/               # CLI & GitHub Actions SARIF runner
└── tests/                          # Test suites (unit, integration, benchmarks)
```
