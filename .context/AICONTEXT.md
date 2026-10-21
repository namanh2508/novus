# AICONTEXT.md — Scientific Mission & Evidence Boundary

> **System**: Evidence-Guided Agentic Web/API Pentest Platform  
> **Version**: 1.0.0-dev | **Status**: Active Architecture & Implementation  
> **Academic Target**: Top-Tier Security Conference / Master Thesis (SSDLC Focused)  

---

## 1. Research Questions (RQs)

- **RQ1 (Adaptive Planning vs. Blind RAG)**: Does an explicit, graph-grounded evidence representation enable an LLM planner to discover significantly more verified BOLA/BFLA vulnerabilities with lower request volume than naive zero-shot or stateless RAG agents?
- **RQ2 (3-Way Differential Oracle vs. Syntactic Status Checking)**: To what degree does a multi-identity differential invariant oracle reduce false positive rates on complex API business logic compared to traditional status-code and schema fuzzing baselines?
- **RQ3 (Resource & Budget Efficiency)**: Can state-aware test planning reduce total network requests and LLM token expenditure by at least 40% while maintaining equivalent or superior recall against standard benchmarks (OWASP crAPI)?

---

## 2. Scientific Evidence Boundary & Invariants

This project is an empirical scientific tool. We maintain rigorous standards for claim verification:

1. **Ground Truth Adjudication**:
   - A finding is NOT counted as a valid vulnerability simply because an LLM claims it or because an endpoint returned `HTTP 200 OK`.
   - A vulnerability claim is verified if and only if the **Differential Invariant Oracle** proves semantic cross-tenant data leakage or unauthorized state mutation under active test identities.
2. **Deterministic Reproducibility**:
   - Every confirmed finding MUST produce an immutable, self-contained Python script (`reproduce_poc.py`).
   - Re-running `python reproduce_poc.py` outside of the agent runtime against the frozen lab container must reproduce the security invariant violation 100% of the time.
3. **Negative Result Retention**:
   - If an adaptive heuristic fails to outperform the baseline or encounters a plateau, the negative result is retained in the evaluation logs and reported honestly. No selective metric cherry-picking.

---

## 3. Core Domain Entities & Mathematical Formulation

Let the target API system be defined as:
$$\mathcal{S} = \langle \mathcal{P}, \mathcal{R}, \mathcal{O}, \mathcal{E}, \mathcal{T} \rangle$$
where:
- $\mathcal{P} = \{p_1, p_2, \dots, p_n\}$: Set of test principals (identities).
- $\mathcal{R}$: Role lattice $(\mathcal{R}, \le)$ defining hierarchical privilege levels.
- $\mathcal{O} = \{o_1, o_2, \dots, o_m\}$: Set of objects / data entities owned by principals.
- $\mathcal{E} = \{e_1, e_2, \dots, e_k\}$: Set of API endpoints exposing operations $\text{op} \in \{\text{GET}, \text{POST}, \text{PUT}, \text{DELETE}\}$.
- $\pi: \mathcal{P} \times \mathcal{O} \times \text{op} \to \{0, 1\}$: Ground-truth authorization policy function (1 = permitted, 0 = forbidden).

A **BOLA Vulnerability** exists at $\langle e, op, o \rangle$ if:
$$\exists p_{attacker}, o_{victim} \text{ such that } \pi(p_{attacker}, o_{victim}, op) = 0 \quad \wedge \quad \text{Exec}(e, op, p_{attacker}, o_{victim}) \models \text{Success}$$
where $\models \text{Success}$ is evaluated not by HTTP status alone, but by semantic payload similarity to the authorized owner's response:
$$\text{Sim}_{\text{semantic}}(R_{attacker \to victim}, R_{victim \to victim}) \ge \tau \quad (\tau = 0.85)$$
