# Two-Tier Agentic Memory Index (Active Conventions)

> **Role**: Ultra-compact (<500 tokens) living index injected into System Prompt.

---

## 1. Active Conventions & Invariants
- `[ACTIVE]` **INV-01 (Planner-Verifier Decoupling)**: Planner proposes action; only Differential Verifier generates `Finding`. [ADR-0001](file:///c:/Users/vuong/Downloads/agent-pentest/ssdlc-agentic-spec/decisions/ADR-0001-decoupled-planner-verifier.md).
- `[ACTIVE]` **INV-02 (3-Way Differential Invariant)**: BOLA requires $O_{legit}=200 \land O_{cross}=200 \land O_{anon} \in \{401, 403\} \land \text{Sim} \ge 0.8$. [ADR-0002](file:///c:/Users/vuong/Downloads/agent-pentest/ssdlc-agentic-spec/decisions/ADR-0002-three-way-differential-oracle.md).
- `[ACTIVE]` **INV-03 (Blast Radius Guard)**: Destructive ops (`PUT/DELETE`) MUST target Shadow Object clones. [ADR-0003](file:///c:/Users/vuong/Downloads/agent-pentest/ssdlc-agentic-spec/decisions/ADR-0003-shadow-object-mutation-isolation.md).
- `[ACTIVE]` **INV-04 (Hybrid Engine)**: Python (Brain & Knowledge Graph) + Go fastprobe (Wire-level fidelity & noise masking).
- `[ACTIVE]` **INV-05 (Zero-Dep PoC)**: Every Finding emits standalone `reproduce_poc.py` using pure `requests`.

---

## 2. Topic Stores
- Details on Authorization Lattice: [.context/topics/bola_authorization_lattice.md](file:///c:/Users/vuong/Downloads/agent-pentest/.context/topics/bola_authorization_lattice.md)
- Details on Reflection & Closed-Loop Adaptation: [.context/topics/closed_loop_adaptation.md](file:///c:/Users/vuong/Downloads/agent-pentest/.context/topics/closed_loop_adaptation.md)
- Detailed Code Catalog: [.context/CODEBASE.md](file:///c:/Users/vuong/Downloads/agent-pentest/.context/CODEBASE.md)
