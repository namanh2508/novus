# Level 5: Full Multi-Modal Cyber OS Specification

## 1. Executive Summary & Repo Comparison

| Capability | Strix (usestrix) | Decepticon (BitterSecurity) | agent-pentest (Level 5) |
| :--- | :--- | :--- | :--- |
| **Headless Browser Execution** | Full Playwright container clicking interactive DOM | None (relies on manual browser) | **PlaywrightDynamicCrawler**: Simulates human clicks on buttons, forms, tabs with networkidle hooks; graceful AST fallback |
| **Interception Proxy GUI** | None | Mitmproxy streaming to web UI | **InterceptionProxyDashboard**: In-browser Burp Suite-style glassmorphism GUI with live Intercept, Request Editor, Forward/Drop, and Repeater on port 8090 |
| **Verification Oracle** | Fuzzing & heuristic LLM | Rule-based triage | **3-Way Differential Invariant Oracle** ($O_{legit}$, $O_{cross}$, $O_{anon}$) for 0% False Positives |
| **Reproducible PoC** | Unformatted logs | Raw HTTP dumps | Standalone, zero-dependency Python script (`reproduce_poc.py`) |
| **Memory Scaling** | Unbounded prompt injection | External DB | Two-Tier Bounded Memory ($< 500$ tok `MEMORY.md` TOC + topic splitting + SQLite FTS5) |

---

## 2. Deep Headless Browser Architecture (`PlaywrightDynamicCrawler`)

When assessing modern Single-Page Applications (React 19, Angular, Vue 3, Next.js) or Canvas/WebGL interfaces:
1. **Dynamic Event Interception**: Modern apps do not expose static `<a href="/api/...">` links; APIs are triggered only when JavaScript state machines transition upon click events.
2. **Execution Flow**:
   - `PlaywrightDynamicCrawler` launches headless Chromium with `--no-sandbox` and custom security headers.
   - Listens to `page.on("request")` and `page.on("response")`.
   - Queries visible interactive selectors (`button`, `a`, `input[type="submit"]`, `[role="button"]`, `.btn`, `.nav-link`).
   - Simulates human click interactions (`await elem.click()`) with micro-delays (300ms) to allow AJAX requests to resolve.
   - Captures all background XHR/Fetch API endpoints and synchronizes them directly into the NetworkX Evidence Graph.
3. **Resilience & Fallback**: If Playwright browser binaries are missing in minimal docker containers or CI runners, it logs a clean warning and falls back to `SPADynamicCrawler` (AST bundle analysis).

---

## 3. Real-Time Interception Proxy GUI (`InterceptionProxyDashboard`)

1. **Architecture**:
   - Built on `aiohttp.web` running asynchronously on `http://127.0.0.1:8090/`.
   - Listens for proxy traffic from browser or upstream tools.
2. **Two Operating Modes**:
   - **Pass-through Mode**: Live passive sniffing. Packets are streamed in real time to the dark-mode Web Dashboard.
   - **Intercept Mode**: Outgoing requests pause execution (`asyncio.Event`). The pentester can view the raw headers/body, edit payload fields in the in-browser textarea, and click **Forward** or **Drop**.
3. **Operator Experience**:
   - Pentester can browse target web applications normally in Google Chrome / Firefox with proxy set to `127.0.0.1:8090`.
   - Every packet is visible in the web UI with status codes, latency, and endpoints.
   - The autonomous Agent concurrently consumes intercepted flows to enrich its Evidence Graph.
