# ADR-0004: NetworkX and SQLite Hybrid Evidence Graph

- **Status**: Accepted
- **Deciders**: Data Architecture Lead
- **Date**: 2026-10-21

## Context
The agent needs both graph traversal capabilities (finding relationships between users, roles, endpoints, and objects) and immutable, high-throughput audit logging (recording full HTTP headers and response bodies for scientific reproducibility). Dedicated graph databases (Neo4j) introduce heavy operational overhead for local test runners and CI pipelines.

## Decision
We adopt a hybrid storage pattern:
1. **NetworkX** for in-memory, zero-dependency graph queries, centrality calculation, and path finding across authorization entities.
2. **SQLite** (in WAL mode) for persistent, tamper-evident audit logging of raw HTTP request/response payloads, indexed by SHA-256 hash.

## Consequences
- **Positive**: Zero external service dependencies (runs in pure Python inside CI or containers); instant startup; fully reproducible in memory.
- **Negative**: Does not scale to millions of nodes (acceptable as pentest target footprints rarely exceed 10,000 entities).
