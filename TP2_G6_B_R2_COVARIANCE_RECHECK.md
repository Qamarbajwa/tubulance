# TP2-G6-B-R2: Covariance Recheck and Adversarial-Family Ontology Repair

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Questions 6 & 7)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B3 — Covariance Spectrum / Multidirectional Dispersion`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Re-examination of Covariance Theorem (CLM-029 / LBR-010)

We re-evaluated the proof of `CLM-029`:
For the exact periodic shear flow $u(x, y, z, t) = (A e^{-\nu k^2 t} \sin(ky), 0, 0)$ on $\mathbb{T}^3$:
\[
C_s = 2\nu \int_s^T \mathbb{E}\left[ (D_r J_\omega)(D_r J_\omega)^\top \right] dr.
\]
1. $J_\omega = \nabla \omega = -U_{yy} (e_3 \otimes e_2)$.
2. $D_r = I + \alpha(r, T) (e_1 \otimes e_2)$.
3. Because $(e_1 \otimes e_2)(e_3 \otimes e_2) = 0$, $D_r J_\omega \equiv -U_{yy} (e_3 \otimes e_2)$.
4. $(D_r J_\omega)(D_r J_\omega)^\top = U_{yy}^2 (e_3 \otimes e_2)(e_2 \otimes e_3) = U_{yy}^2 (e_3 \otimes e_3) = \operatorname{diag}(0, 0, U_{yy}^2)$.
5. Therefore:
\[
C_s = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \\ 0 & 0 & \mathcal{I}_s \end{pmatrix}, \quad \text{where } \mathcal{I}_s = 2\nu \int_s^T \mathbb{E}[U_{yy}^2] dr > 0.
\]
The eigenvalues are $\lambda_1 = \mathcal{I}_s = \operatorname{tr}(C_s) > 0$, $\lambda_2 = 0$, $\lambda_3 = 0$, and $\det(C_s) \equiv 0$.

### 1.1 Audit Finding & Disposition
- **Mathematical Soundness:** The analytical proof is exact and unconditional.
- **Disposition of `CLM-029`:** **`RETAINED`**.
- **Disposition of `LBR-010`:** **`RETAINED_WITH_QUALIFICATION`**.
- **Qualification on Bridge $B_3$ Formulation:**
  The ratio condition:
  \[
  \frac{\lambda_{\min}(C_s)}{\operatorname{tr}(C_s)} \ge c_0 > 0
  \]
  is a **sufficient condition** for non-degenerate 3D stochastic dispersion. It must not be asserted as the unique necessary formulation of Bridge $B_3$, since alternative non-degeneracy metrics (such as $\det(C_s)^{1/3} / \operatorname{tr}(C_s)$, condition number, or effective directional rank) may also capture multidirectional dispersion.
  The core negative result stands firmly:
  \[
  \boxed{ \operatorname{tr}(C_s) > 0 \not\implies \text{3D Multidirectional Stochastic Dispersion} }.
  \]

---

## 2. Adversarial-Family Ontology Repair

The R1 matrix row 5 used the contradictory classification `"NS Exact? YES (Candidate)"`. The project formally establishes a canonical six-tier ontology:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CANONICAL REALIZABILITY ONTOLOGY                     │
│                                                                        │
│  1. EXACT_NS_SOLUTION: Fully proved global/local smooth NS solution.   │
│  2. EXACT_REDUCED_NS_CLASS: Invariant subspace (2D, axisymmetric, etc.)│
│  3. ASYMPTOTIC_NS_FAMILY: Rigorous asymptotic family with bounded error│
│  4. UNVERIFIED_NS_CANDIDATE: Proposed blowup profile/ansatz without    │
│     proved smooth NS existence.                                        │
│  5. KINEMATIC_ONLY: Realizable vector/tensor field, but dynamical      │
│     NS evolution is unproved or violated.                              │
│  6. LOCAL_ALGEBRAIC_CONFIGURATION: Pointwise matrix snapshot.        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Reclassified Adversarial Matrix Table

| Family Name | Realizability Tier | Vortex Stretching Rate $\sigma_{\text{stretch}}$ | Intrinsic $J_n(a)$ Limit | Covariance Rank | Canonical Status |
|---|---|---|---|---|---|
| **1. Periodic Shear** | `EXACT_NS_SOLUTION` | $\equiv 0$ | $\to 0$ ($\mathcal{O}(A_n^{-1})$) | $\operatorname{rank} = 1$ | `SURROGATE_RIGID_REGIME_R-A` |
| **2. Single-Helical Beltrami** | `EXACT_NS_SOLUTION` | $\equiv 0$ | $\to 0$ ($\mathcal{O}(A_n^{-1})$) | $\operatorname{rank} \le 3$ | `SURROGATE_RIGID_REGIME_R-A` |
| **3. 2D Flow Subspace** | `EXACT_REDUCED_NS_CLASS` | $\equiv 0$ | $\to 0$ | $\operatorname{rank} = 1$ | `SURROGATE_RIGID_REGIME_R-A` |
| **4. Kinematic Decoupling** | `LOCAL_ALGEBRAIC_CONFIGURATION` | $> 0$ (Algebraic) | $\Xi \to 0$ | N/A | `KINEMATIC_BENCHMARK_ONLY` ($B_0$) |
| **5. Active 3D Stretching** | `UNVERIFIED_NS_CANDIDATE` | $\sim M_n$ | **OPEN** | **OPEN** | `HYPOTHETICAL_SINGULARITY_TARGET` (R-C) |

The ambiguous label `"YES (Candidate)"` is permanently eliminated.
