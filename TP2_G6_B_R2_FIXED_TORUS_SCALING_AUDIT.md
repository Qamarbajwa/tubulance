# TP2-G6-B-R2: Fixed-Torus Scaling Audit and Domain Qualification of CLM-028

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Question 1)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Context and Audit Objective

In milestone `TP2-G6-B-R1`, claim `CLM-028` asserted:
\[
u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t) \implies J_\lambda(a) \equiv J_0(a) \quad \forall \lambda > 0.
\]
This audit evaluates `CLM-028` against the strict periodic boundary conditions of the Clay Millennium Prize Problem Statement B on the fixed unit torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$.

---

## 2. Lattice Compatibility and Domain Classification

Let $u(x, t)$ be 1-periodic in each spatial coordinate:
\[
u(x + e_j, t) = u(x, t) \quad \forall j \in \{1, 2, 3\}, \quad \forall x \in \mathbb{R}^3.
\]
Under parabolic dilation $u_\lambda(x, t) := \lambda u(\lambda x, \lambda^2 t)$, evaluating spatial periodicity yields:
\[
u_\lambda(x + e_j, t) = \lambda u(\lambda x + \lambda e_j, \lambda^2 t).
\]
This equals $u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t)$ for all $x$ if and only if $\lambda e_j \in \mathbb{Z}^3$ for all $j \in \{1, 2, 3\}$, which forces:
\[
\lambda \in \mathbb{Z}^+ = \{1, 2, 3, \dots\}.
\]

If $\lambda \notin \mathbb{Z}^+$, $u_\lambda$ is **not** periodic on the fixed torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$. Instead, $u_\lambda$ is periodic on the rescaled torus:
\[
\mathbb{T}_\lambda^3 := \mathbb{R}^3 / (\lambda^{-1} \mathbb{Z})^3.
\]

### Rigorous Domain Taxonomy:
1. **Unbounded Domain $\mathbb{R}^3$:** The parabolic invariance identity $J_\lambda(a) \equiv J_0(a)$ holds unconditionally for all continuous dilation parameters $\lambda \in (0, \infty)$.
2. **Rescaled Torus Family $\mathbb{T}_\lambda^3$:** The identity $J_\lambda(a) \equiv J_0(a)$ holds for all continuous $\lambda \in (0, \infty)$ when viewed as a family of solutions mapping across the one-parameter family of tori $\mathbb{T}_\lambda^3$.
3. **Fixed Unit Torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$:** On the exact domain of Clay Statement B, $u_\lambda$ defines a smooth divergence-free solution on the **same unit torus** if and only if $\lambda \in \mathbb{N} = \{1, 2, 3, \dots\}$ (integer frequency multiplication).
4. **Statement-B Relevance:** Pure parabolic dilation cannot generate a continuous family of solutions on the fixed unit torus $\mathbb{T}^3$. For integer dilations $\lambda = n \in \mathbb{N}$, the solutions $u_n(x, t)$ are valid on $\mathbb{T}^3$, but their intrinsic production remains strictly invariant:
\[
J_n(a) \equiv J_1(a) \quad \forall n \in \mathbb{N}.
\]

---

## 3. Disposition of CLM-028 and LBR-009

The continuous scaling derivation in R1 remains mathematically sound, but its formulation as a universal statement on the fixed periodic torus was domain-overstated.

- **Disposition of `CLM-028`:** `SUPERSEDED` by `CLM-031`.
- **New Canonical Claim (`CLM-031`):**
  - **Name:** `PARABOLIC_SCALING_INVARIANCE_OF_J_WITH_DOMAIN_COMPATIBILITY`
  - **Type:** `MATHEMATICAL_IDENTITY`
  - **Truth Status:** `PROVED_IDENTITY`
  - **Statement:** "Under parabolic rescaling $u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t)$, the intrinsic lookback relative production satisfies $J_\lambda(a) \equiv J_0(a)$ for all $\lambda > 0$ on $\mathbb{R}^3$ and across rescaled tori $\mathbb{T}_\lambda^3$. On the fixed unit torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$, $u_\lambda$ is lattice-compatible if and only if $\lambda \in \mathbb{N}$, for which $J_n(a) \equiv J_1(a)$ strictly."
- **Disposition of `LBR-009`:** `SUPERSEDED` by `LBR-011`.
