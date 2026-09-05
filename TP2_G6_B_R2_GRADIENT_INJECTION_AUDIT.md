# TP2-G6-B-R2: Re-examination and Downgrade of NS-NEG-014 (Gradient Injection)

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Question 4)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Context and Audit Objective

In milestone `TP2-G6-B-R1`, record `NS-NEG-014` asserted:
> "In any localized 3D flow structure undergoing intense nonlinear vortex stretching $\omega \cdot S \omega \sim M_n^2$, the non-local source term $T = (\nabla S)\omega$ in the vorticity-gradient transport equation injects gradient perturbations at rate $\|T\| \gtrsim M_n^2 / \ell_n$, forcing $J_n(a) \ge c_0 > 0$ on viscous scales."

This audit re-examines the mathematical foundation of `NS-NEG-014` strictly from the exact Navier–Stokes transport equations.

---

## 2. Separation of Exact Equations from Scaling Assumptions

The starting point is the exact vorticity-gradient transport tensor equation (`CLM-006`):
\[
(D_t - \nu \Delta) G = S G - G A + T, \quad \text{where } T_{ij} = (\partial_j S_{ik})\omega_k = [(\nabla S)\omega]_{ij},
\]
with $G = \nabla \omega$, $A = \nabla u$, and $S = \frac{1}{2}(A + A^\top)$.

### Audit of Each Component in the R1 Argument:

| Component in R1 Argument | Mathematical Nature | Audited Status |
|---|---|---|
| $(D_t - \nu \Delta)G = SG - GA + T$ | Exact tensor transport identity | **PROVED EXACT IDENTITY** |
| $T = (\nabla S)\omega$ | Exact definition of source term | **PROVED EXACT IDENTITY** |
| $\|T\| \gtrsim \frac{M_n \|S\|}{\ell_n}$ | Dimensional scaling heuristic | **UNPROVED SCALING HYPOTHESIS** |
| $S \omega \ne 0 \implies (\nabla S)\omega \ne 0$ | Implication | **FALSE IN GENERAL (Counterexamples exist)** |
| $\ell_n \sim M_n^{-1/2}$ (Kolmogorov scale) | Phenomenological scale assumption | **CONDITIONAL ASSUMPTION (Not proved for NS singularities)** |
| $\Xi \sim M_n$ | Order-of-magnitude estimate | **CONDITIONAL HEURISTIC** |
| $J_n(a) \ge c_0 > 0$ under active stretching | Claimed universal lower bound | **UNPROVED SCALING CONJECTURE** |

---

## 3. Explicit Counter-Configurations: $S \omega \ne 0$ with $(\nabla S)\omega = 0$

Can intense vortex stretching coexist with a vanishing gradient source term $T = (\nabla S)\omega$?

### 3.1 Kinematic / Local Polynomial Counterexample
Consider a local velocity field around $x_0 = 0$:
\[
u(x) = S_0 x + \mathcal{O}(|x|^3),
\]
where $S_0 = \operatorname{diag}(\alpha_1, \alpha_2, \alpha_3)$ is a constant symmetric trace-free matrix with $\alpha_1 > 0$, $\alpha_1 + \alpha_2 + \alpha_3 = 0$.
Let $\omega_0 = e_1$.
- Active vortex stretching at $x = 0$:
  \[
  \omega_0 \cdot S_0 \omega_0 = \alpha_1 |\omega_0|^2 = \alpha_1 > 0 \quad (\text{Strictly positive vortex stretching}).
  \]
- Spatial derivative of strain at $x = 0$:
  Because the quadratic velocity terms are chosen to vanish ($\nabla^2 u(0) = 0$):
  \[
  \nabla S(0) = 0 \implies \boxed{ T(0) = (\nabla S(0))\omega_0 \equiv 0 }.
  \]
Thus, active vortex stretching does **not** algebraically force $T \ne 0$ at a point.

### 3.2 Strain Extrema in Periodic Divergence-Free Fields
In any smooth periodic Navier–Stokes flow on $\mathbb{T}^3$, the scalar components of the strain tensor $S_{ik}(x)$ achieve local spatial extrema.
At any point $x_*$ where $\nabla S_{ik}(x_*) = 0$ for the dominant stretching components:
\[
\|T(x_*)\| = \|(\nabla S(x_*))\omega(x_*)\| = 0,
\]
even if $S(x_*)$ and $\omega(x_*)$ are both arbitrarily large!
Near $x_*$, $\|\nabla S(x)\| \le C |x - x_*|$ is small, so $T$ cannot satisfy a uniform pointwise lower bound $\|T\| \ge c M_n^2 / \ell_n$ across the core.

---

## 4. Formal Disposition of NS-NEG-014

- **Audit Verdict:** The claim that $T = (\nabla S)\omega$ provides a universal, mathematically proved lower bound on $J_n(a)$ is **UNPROVED**. It conflated a dimensional/phenomenological turbulence estimate with a rigorous PDE theorem.
- **Disposition of `NS-NEG-014`:** **DOWNGRADED** from `PROVED_NEGATIVE_EVIDENCE_OBSTRUCTION` to:
  \[
  \boxed{ \mathbf{OPEN\_CONDITIONAL\_SCALING\_HYPOTHESIS} }
  \]
- **Correction to Bridge Strategy:** `NS-NEG-014` must **not** be cited as a proved obstruction narrowing Bridge $B_1$ exclusively to pressure-strain coupling. The question of whether active vortex stretching can coexist with $J_n(a) \to 0$ remains strictly **`OPEN`**.
