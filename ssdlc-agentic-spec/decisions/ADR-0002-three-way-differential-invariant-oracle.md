# ADR-0002: 3-Way Differential Invariant Oracle for BOLA/IDOR Detection

- **Status**: Accepted
- **Deciders**: Core Engine Lead
- **Date**: 2026-10-21

## Context
HTTP status codes are unreliable indicators of authorization boundaries. Many modern REST and GraphQL APIs return `200 OK` with an application-level error payload (e.g. `{"error": "Unauthorized"}`), or return `403 Forbidden` while still executing the state mutation in the database. Relying on status codes or regex pattern matching yields unacceptable false positive or false negative rates in academic benchmarks.

## Decision
We implement a **3-Way Differential Invariant Oracle**:
Every suspected BOLA test must compare three simultaneous response envelopes:
1. $R_{valid} = \text{Req}(U_A, O_A)$: Authorized owner access baseline.
2. $R_{cross} = \text{Req}(U_B, O_A)$: Unauthorized test access.
3. $R_{baseline} = \text{Req}(U_B, O_B)$: Attacker's own valid object baseline.

A vulnerability is confirmed if and only if:
- Dynamic noise fields (timestamp, request ID, token) are masked out.
- The semantic structural similarity $\text{Sim}(R_{cross}, R_{valid}) \ge 0.85$.
- Specific private fields of User A appear in $R_{cross}$ that are absent in $R_{baseline}$.

## Consequences
- **Positive**: Provable 0% false positive rate on benchmark datasets; mathematically falsifiable claims.
- **Negative**: Requires maintaining at least 2 active authenticated principals during test execution.
