# Topic Store: Closed-Loop Adaptation & Error Reflection

## 1. Multi-Turn Self-Correction Mindset
In autonomous agentic pentesting, HTTP probes often fail initially with $400 \text{ Bad Request}$ or $422 \text{ Unprocessable Entity}$ due to:
- Missing required query/body parameters (e.g. `mechanic_code`, `coupon_code`).
- Data type mismatches (string vs integer).
- Missing required headers (CSRF tokens, content-type).

Rather than reporting a failure, the Agent executes a closed-loop perception-action cycle:
$$\text{Perception (Error 4xx)} \to \text{Reflection (AST/Regex Analysis)} \to \text{Action (Amended Payload)} \to \text{Observation}$$

## 2. Invariant Protection
- Self-correction is bounded by `max_attempts = 2` to prevent infinite probe loops.
- All retry attempts are immutably logged into `SQLiteAuditStore` with raw HTTP request/response tuples and SHA-256 hashes.
