# Topic Store: BOLA Authorization Lattice & Differential Invariants

## 1. Mathematical Formulation
Let:
- $\mathcal{P} = \{P_1, P_2, \dots, P_n\}$ be the set of principals.
- $\mathcal{O} = \{O_1, O_2, \dots, O_m\}$ be the set of target domain objects.
- $\mathcal{R}$ be the set of HTTP methods and actions.
- $\mathcal{L} = \langle \mathcal{S}, \sqsubseteq \rangle$ be the authorization lattice where $S_{anon} \sqsubset S_{user} \sqsubset S_{admin}$.

An authorization mapping $\Phi: \mathcal{P} \times \mathcal{O} \to \mathcal{P}(\mathcal{R})$ defines allowed operations.

A Broken Object Level Authorization (BOLA) vulnerability exists if and only if:
$$\exists P_a, P_b \in \mathcal{P}, O_k \in \mathcal{O}, r \in \mathcal{R} \text{ such that } P_a \neq P_b \land r \in \Phi(P_a, O_k) \land r \notin \Phi(P_b, O_k) \land \text{Obs}(P_b, r, O_k) = \text{Success}$$

## 2. 3-Way Triplet Invariant Verification
To prevent false positives from public endpoints or broken authentication:
1. $O_{legit}(P_a, r, O_k) \to 200 \text{ OK}$ (Baseline)
2. $O_{cross}(P_b, r, O_k) \to 200 \text{ OK}$ (Cross-Principal Access)
3. $O_{anon}(\emptyset, r, O_k) \in \{401, 403\}$ (Control - must reject anonymous)
4. $\text{SemanticSimilarity}(Body_{legit}, Body_{cross}) \ge 0.8$ after dynamic noise masking.
