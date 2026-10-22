# EPIC-01: Ingestion & Storage Infrastructure (Batch Tasks T-003 to T-006)

> **Objective**: Implement the complete Ingestion and Evidence Storage layer in a single batch to maximize throughput and test coverage.

---

## 📦 Scope of Deliverables

| Task | Target File | Interface to Implement | Reference Test |
| :--- | :--- | :--- | :--- |
| **T-003** | `src/agentic_pentest/infrastructure/discovery/openapi_parser.py` | `IOpenAPIParser` ([discovery.py](file:///c:/Users/vuong/Downloads/agent-pentest/src/agentic_pentest/application/interfaces/discovery.py)) | `tests/unit/test_openapi_parser.py` |
| **T-004** | `src/agentic_pentest/infrastructure/playbooks/registry.py` | `IPlaybookRegistry` ([playbooks.py](file:///c:/Users/vuong/Downloads/agent-pentest/src/agentic_pentest/application/interfaces/playbooks.py)) | `tests/unit/test_playbook_registry.py` |
| **T-005** | `src/agentic_pentest/infrastructure/storage/networkx_graph.py` | `IEvidenceGraph` ([graph.py](file:///c:/Users/vuong/Downloads/agent-pentest/src/agentic_pentest/application/interfaces/graph.py)) | `tests/unit/test_networkx_graph.py` |
| **T-006** | `src/agentic_pentest/infrastructure/storage/sqlite_audit_store.py` | `IAuditStore` ([audit.py](file:///c:/Users/vuong/Downloads/agent-pentest/src/agentic_pentest/application/interfaces/audit.py)) | `tests/unit/test_sqlite_audit.py` |

---

## 🛠️ Detailed Specifications

### 1. `OpenAPIParser` (`src/agentic_pentest/infrastructure/discovery/openapi_parser.py`)
- Parse JSON or YAML string/dict into `list[EndpointDefinition]`.
- Extract `path_parameters` (e.g. from `/vehicle/{vehicle_id}/location` $\to$ `['vehicle_id']`).
- Check `security`: if an operation specifies `security: []`, then `auth_required = False`, otherwise `True`.
- `extract_candidate_objects`: scans parameters to identify target object candidates (`_id` suffix or UUIDs).

### 2. `PlaybookRegistry` (`src/agentic_pentest/infrastructure/playbooks/registry.py`)
- Reads YAML files from directory (loads `bola_read.yaml`, `bola_write.yaml` from `src/agentic_pentest/infrastructure/playbooks/data/`).
- Returns list of `AttackPlaybook` with `PlaybookStep` items.
- Supports `get_playbook(playbook_id)` and `get_playbooks_for_category(category)`.

### 3. `NetworkXEvidenceGraph` (`src/agentic_pentest/infrastructure/storage/networkx_graph.py`)
- Uses `networkx.DiGraph`.
- Nodes: `principal:{id}` (type='principal', data=Principal), `object:{id}` (type='object', data=TargetObject).
- Edges: `(principal_id, object_id)` with attribute `relation` (e.g. `'OWNS'`).
- `get_principal_objects(principal_id)`: returns objects connected via `'OWNS'`.
- `get_cross_principal_targets(attacker_id)`: returns all objects in graph NOT owned by `attacker_id`.

### 4. `SQLiteAuditStore` (`src/agentic_pentest/infrastructure/storage/sqlite_audit_store.py`)
- Uses Python `sqlite3`.
- Creates table `observations (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, method TEXT, url TEXT, req_headers TEXT, req_body TEXT, status_code INT, resp_headers TEXT, resp_body TEXT, latency_ms INT, body_sha256 TEXT, timestamp TEXT)`.
- `record_observation`: stores tuple, returns `row_id`.
- `get_session_observations`: retrieves list of `(HTTPRequestObservation, HTTPResponseObservation)` ordered by timestamp.

---

## 📋 Master Prompt for Copilot (Agent Mode / Copilot Edits)
```text
Please implement the 4 infrastructure modules specified in `tasks/EPIC-01-ingestion-and-storage.md`:

1. `src/agentic_pentest/infrastructure/discovery/openapi_parser.py` (implements IOpenAPIParser in `application/interfaces/discovery.py`)
2. `src/agentic_pentest/infrastructure/playbooks/registry.py` (implements IPlaybookRegistry in `application/interfaces/playbooks.py`)
3. `src/agentic_pentest/infrastructure/storage/networkx_graph.py` (implements IEvidenceGraph in `application/interfaces/graph.py` using NetworkX)
4. `src/agentic_pentest/infrastructure/storage/sqlite_audit_store.py` (implements IAuditStore in `application/interfaces/audit.py` using sqlite3)

All code must:
- Pass `pytest tests/unit/` (all 4 test files: test_openapi_parser.py, test_playbook_registry.py, test_networkx_graph.py, test_sqlite_audit.py).
- Pass `ruff check .` with 0 warnings.
- Be strictly typed (mypy --strict compliant).
- Commit your changes with: `git commit -am "feat(infra): implement EPIC-01 ingestion and storage infrastructure"`
```
