---
title: "Target Attack Surface Map"
target: "http://localhost:8888"
tags:
  - pentest/attack_surface
---

# 🗺️ Target Attack Surface Map

## Target Information
- **Base URL**: `http://localhost:8888`
- **Security Assessment Scope**: REST API Endpoints, Identity Services, Workshop, Community.
- **Authorization Lattice**: Multi-tenant RBAC (USER vs ADMIN, Cross-tenant Object Isolation).

## Tested Endpoints & Verified Invariant Status
| Endpoint | Method | Tested Vulnerability | Verdict |
|---|:---:|---|:---:|
| `/identity/api/v2/vehicle/{id}/location` | GET | BOLA (API1:2023) | **VULNERABLE** |
| `/community/api/v2/coupon/new-coupon` | POST | BFLA (API5:2023) | **VULNERABLE** |
| `/identity/api/v2/user/change-email` | POST | BOPLA / Mass Assignment | SECURE |
| `/identity/api/auth/login` | POST | Authentication Audit | SECURE |

---
*Return to [[00_Index|Vault Index]]*
