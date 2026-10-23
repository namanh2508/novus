# Changelog

All notable changes to the **Evidence-Guided Agentic Web/API Pentesting Platform** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-10-24

### Added
- **UC-12 Concurrency & TOCTOU Race Condition Auditor**:
  - Implements burst HTTP dispatch (`asyncio.gather` with microsecond synchronization) to detect race conditions and double-spending logic bugs on coupon/credit endpoints.
  - Zero-FP verification via idempotency invariant checks.
- **UC-13 GraphQL Security Auditor**:
  - Probes GraphQL endpoints for introspection exposure, schema extraction, and query batching DoS amplification vulnerabilities.
- **UC-14 JWT Cryptographic Auditor**:
  - Detects `alg: none` header bypasses, signature stripping vulnerabilities, and offline HMAC-SHA256 dictionary cracking on weak secrets.
- **UC-15 Secret Leakage & Memory Dump Exposure Auditor**:
  - Scans sensitive endpoint paths (`.env`, `.git/HEAD`, `/actuator/heapdump`, `/metrics`, `/debug/pprof`) and runs high-entropy API key regex scanning.
- **AI Code Guard & AST Tree Coverage Engine**:
  - Implements static AST parsing, taint tracking from tainted sources to dangerous execution sinks (`eval`, `exec`, `subprocess.Popen`, raw SQL `format`), and mathematical guard coverage metric:
    $$\text{RiskScore}(\mathcal{T}) = \min\left(100, \sum_{p \in \mathcal{P}(S \to K)} w(K) \cdot [1 - \gamma(p)] \cdot \mathcal{D}(p)\right)$$
- **SE373 Benchmark Evaluation Harness**:
  - 30-case golden benchmark dataset (`evals/questions/questions.jsonl`) spanning Recon, Auth, IDOR/BOLA, BFLA, Race Condition, GraphQL, JWT, Secret Leaks, and AI Code Defense.
  - Measures Task Execution Accuracy (EX), latency, and tool selection precision.
- **14 Model Context Protocol (MCP) Tools**:
  - Registered in `PentestToolRegistry` and exposed via FastMCP server (`agentic-pentest mcp`) for agentic ecosystems (Claude Code, Cursor, Antigravity, Roo/Cline).
- **Interactive Cyber-Whale Mascot Banner & Terminal UX**:
  - Custom ASCII Cyber-Whale mascot in terminal banner with live target status, permission mode, and working memory stats.
  - Quick action numeric shortcuts (`0` to `10`), `/learn` episodic memory injection, `/guide` playbooks, and `/compact` output collapsing.
- **Cross-Platform Kali / Ubuntu / Windows Bridge**:
  - Structured CLI bridge with `shutil.which` detection for native Kali tools (`nmap`, `ffuf`, `nuclei`) and pure-Python fallback pipelines on Windows and Ubuntu.

### Changed
- Standardized terminal indicators to Unicode `✓` (`\u2713`) and `✗` (`\u2717`) and ASCII brackets `[*]`, `[+]`, `[-]`.
- Updated `VulnerabilityCategory` enum in `domain/entities.py` with `RACE_CONDITION`, `GRAPHQL_INJECTION`, `JWT_FLAW`, `SECRET_LEAK`, and `CODE_SECURITY`.
- Enhanced `RemediationPatchGenerator` with Git diff code patches for all new vulnerability classes.
- Updated `ObsidianVaultExporter` with CWE and OWASP API Top 10 mappings for all new classes.
- Updated `pyproject.toml` with Python 3.12 support and strict mypy overrides.

### Fixed
- Fixed unescaped quotation marks in `chat.py` banner string.
- Fixed typing annotations in `scratch/generate_eval_dataset.py`.
- Fixed duplicate `show_banner` declaration in `chat.py`.
- Cleaned up inline imports in `structured_bridge.py`.

---

## [0.1.0] - 2026-10-21

### Added
- Core 4-layer Clean Architecture (`domain/`, `application/`, `infrastructure/`, `presentation/`).
- 3-Way Differential Invariant Oracle ($O_{legit}$, $O_{cross}$, $O_{anon}$) for zero false-positive BOLA/BFLA verification.
- Hybrid Evidence Graph (NetworkX directed multigraph + SQLite audit trail).
- Hypothesis-Driven Adaptive Planner (`AdaptivePlanner` and `InteractivePentestPlanner`).
- Single Page Application (SPA) Dynamic Crawler and AST Route Extractor (`SPADynamicCrawler`, `SASTBridgeRouteExtractor`).
- Shadow Object Cloner with rollback journal.
- Zero-dependency reproducible Python PoC generator (`PoCGenerator`).
- Interactive CLI and REPL session runner.
- OWASP crAPI benchmark environment.
