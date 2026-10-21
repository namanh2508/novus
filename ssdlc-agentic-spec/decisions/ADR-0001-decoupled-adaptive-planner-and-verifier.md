# ADR-0001: Decoupled Adaptive Planner and Independent Verifier Architecture

- **Status**: Accepted
- **Deciders**: Security Architecture Lead, Research Lead
- **Date**: 2026-10-21

## Context
Traditional LLM pentest agents bundle decision-making, tool execution, and vulnerability evaluation into a single monolithic prompt loop. When the same model that invents an attack hypothesis is also responsible for judging whether the attack succeeded, cognitive confirmation bias occurs: models frequently hallucinate success on irrelevant HTTP 200 responses, error pages, or generic reflections, leading to high False Positive Rates (FPR).

## Decision
We enforce strict architectural decoupling between **Hypothesis Planning** and **Vulnerability Verification**:
1. The `AdaptivePlanner` operates as a generator: it proposes the next test action based on the evidence graph state and remaining budget.
2. The `DifferentialVerifier` operates as an independent discriminator: it evaluates test results against ground-truth mathematical invariants and baseline differential responses.
3. The Planner has **zero authority** over the vulnerability verdict; a `Finding` is created solely when approved by the Verifier.

## Consequences
- **Positive**: Eliminates hallucinated findings; establishes rigorous scientific boundaries; allows ablation benchmarking of planner and verifier independently.
- **Negative**: Increases request count slightly per candidate vulnerability due to verification checks (compensated by lower wasted requests overall).
