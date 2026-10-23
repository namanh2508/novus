# Agentic Pentest — Complete CLI Command Reference Catalog

This document details all 27 CLI commands and interactive chat actions available in the **Evidence-Guided Agentic Web/API Pentesting Platform**.

---

## Direct Invocation Pattern

Every tool can be executed directly as a standalone CLI utility:
```powershell
# Windows PowerShell
.venv\Scripts\python -m agentic_pentest.presentation.cli <command> [options]

# Linux / macOS / Bash
./.venv/bin/python -m agentic_pentest.presentation.cli <command> [options]
```

---

## 1. Core & REPL Commands

### `chat`
Launch the interactive terminal chat session featuring the Cyber-Whale mascot, inline auto-suggestions, and Tab completion.
```powershell
python -m agentic_pentest.presentation.cli chat --target http://localhost:8888 --mode interactive
```

### `scan`
Execute full 3-Way Differential Invariant Oracle verification on an OpenAPI specification.
```powershell
python -m agentic_pentest.presentation.cli scan --spec fixtures/crapi_openapi.json --target http://localhost:8888
```

### `loop`
Run the multi-turn autonomous pentest loop with hypothesis generation and closed-loop reflexion.
```powershell
python -m agentic_pentest.presentation.cli loop --target http://localhost:8888 --turns 8
```

### `multi-agent`
Orchestrate 3 specialized sub-agents: Recon Agent, Differential Verifier Agent, and Remediation Patch Agent.
```powershell
python -m agentic_pentest.presentation.cli multi-agent --target http://localhost:8888
```

### `plan`
Launch an interactive OWASP Top 10 hypothesis planning session with step-by-step operator approval.
```powershell
python -m agentic_pentest.presentation.cli plan --target http://localhost:8888
```

---

## 2. Level 5 Multi-Modal Cyber OS Commands

### `browser`
Deep Headless Browser Crawling & Dynamic API Discovery using Playwright. Simulates human button clicks, tab switches, and form triggers to capture background XHR/Fetch API calls.
```powershell
python -m agentic_pentest.presentation.cli browser http://localhost:8888 --clicks 25
```

### `dashboard`
Start the real-time Burp Suite-style Interception Proxy Web Dashboard on port 8090. Includes packet interception, live request/response editor, and forward/drop controls.
```powershell
python -m agentic_pentest.presentation.cli dashboard --port 8090
```

---

## 3. Specialized Security Audit Commands (UC-12 to UC-15)

### `race` (UC-12)
Dispatch microsecond-synchronized concurrent HTTP requests to detect TOCTOU race conditions and coupon re-use flaws.
```powershell
python -m agentic_pentest.presentation.cli race --endpoint http://localhost:8888/community/api/v2/coupon/new-coupon --concurrency 10
```

### `graphql` (UC-13)
Audit GraphQL endpoints for Introspection schema exposure, batching query DoS, and nested depth limits.
```powershell
python -m agentic_pentest.presentation.cli graphql --target http://localhost:8888
```

### `jwt` (UC-14)
Audit JSON Web Tokens for `alg: none` bypass, signature stripping, and brute-force weak HMAC secrets against high-frequency dictionaries.
```powershell
python -m agentic_pentest.presentation.cli jwt --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### `secrets` (UC-15)
Probe sensitive web directories (`.env`, `.git/HEAD`, `heapdump`, `/actuator`) and calculate Shannon entropy for leaked API keys.
```powershell
python -m agentic_pentest.presentation.cli secrets --url http://localhost:8888
```

### `ai-guard`
Analyze Python source code using AST Taint Reachability to detect dangerous unprotected sinks (`eval`, `exec`, `os.system`) and score Guard Coverage.
```powershell
python -m agentic_pentest.presentation.cli ai-guard -f src/agentic_pentest/application/use_cases/audit_jwt.py
```

---

## 4. Reconnaissance & Intelligence Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `crawl` | `cli crawl --url <url>` | Static SPA crawler extracting API routes from JS bundles |
| `sast` | `cli sast <dir>` | AST route extractor for FastAPI / Flask / Express |
| `proxy` | `cli proxy --port 8080` | Passive in-line traffic sniffer streaming into Evidence Graph |
| `cve` | `cli cve --banner <sig>` | Advisory intelligence querying NVD/CVSS for server signatures |

---

## 5. Defensive Baseline Audits

| Command | Usage | Description |
| :--- | :--- | :--- |
| `audit-headers` | `cli audit-headers <url>` | Audit HSTS, CSP, X-Frame-Options, X-Content-Type-Options |
| `audit-cookies` | `cli audit-cookies <url>` | Audit HttpOnly, SameSite, Secure cookie flags |
| `audit-cors` | `cli audit-cors <url>` | Detect wildcard Access-Control-Allow-Origin & reflections |
| `audit-login` | `cli audit-login <url>` | Audit login endpoint brute force rate limiting |

---

## 6. Benchmarks, Lab & Reporting

| Command | Usage | Description |
| :--- | :--- | :--- |
| `seed-crapi` | `cli seed-crapi -t <url>` | Seed OWASP crAPI benchmark environment (Alice/Bob/Vehicles) |
| `eval` | `cli eval -q <path>` | Run standardized 30-case evaluation suite (Task Accuracy EX) |
| `demo-server` | `cli demo-server -p 8888` | Start live mock target server for offline demonstration |
| `export-vault` | `cli export-vault -o <dir>` | Export evidence, attack graphs & findings to Obsidian Vault |
| `sessions` | `cli sessions` | Inspect persisted SQLite sessions and evidence graphs |
| `mcp-server` | `cli mcp-server` | Launch FastMCP server over stdio for Claude Code / IDEs |
