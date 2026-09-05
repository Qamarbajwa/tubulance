# TP2-G6-B-R2: Formal Claim and Artifact Disposition Matrix

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Claim Dispositions)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. Master Disposition Table

Each item audited from `TP2-G6-B-R1` is assigned exactly one formal disposition:

| Item Identifier | Original Description / Claim | Audited Disposition | Rationale and Corrected Status |
|---|---|---|---|
| **`CLM-028`** | Parabolic Invariance of Intrinsic Stochastic Production | **`SUPERSEDED`** | Domain overstated for fixed torus $\mathbb{T}^3$. Superseded by `CLM-031` with explicit lattice-compatibility qualification. |
| **`CLM-029`** | Maximal Covariance Rank Deficiency Under Positive Trace | **`RETAINED`** | Proof on periodic shear is exact and unconditional. Clarified as sufficient (not uniquely necessary) condition for Bridge $B_3$. |
| **`CLM-030`** | Rigid Branch Adversarial Attack Synthesis | **`SUPERSEDED`** | Conflated R-A data families with R-C blowup sequences, and relied on unproved gradient obstruction. Superseded by `CLM-032`. |
| **`LBR-009`** | Load-Bearing Result: Parabolic Invariance | **`SUPERSEDED`** | Superseded by `LBR-011` incorporating fixed-torus lattice compatibility. |
| **`LBR-010`** | Load-Bearing Result: Maximal Covariance Rank Deficiency | **`RETAINED_WITH_QUALIFICATION`** | Retained with explicit qualification on Bridge $B_3$ sufficiency vs necessity. |
| **`NS-NEG-014`** | Gradient Injection Under Active Vortex Stretching | **`DOWNGRADED`** | Conflated phenomenological scaling with a proved PDE theorem. Downgraded to `OPEN_CONDITIONAL_SCALING_HYPOTHESIS`. |
| **Beltrami Benchmark** | Family 2 in Adversarial Matrix | **`RETAINED_WITH_QUALIFICATION`** | Pointwise $\omega \cdot S \omega \equiv 0$ holds strictly for constant-speed / single-helical modes; multi-mode ABC flows cancel dynamically with advection and have zero mean enstrophy production. |
| **Branch-R Classification** | Periodic Shear & Beltrami realization | **`RETAINED_WITH_QUALIFICATION`** | Re-designated from "Branch R realized" to `SURROGATE_RIGID_SIGNATURE_REALIZED_ACROSS_DATA_FAMILY` (Regime R-A). Regime R-C remains strictly OPEN. |

---

## 2. Formal Definitions of New Canonical Claims

### `CLM-031`: PARABOLIC_SCALING_INVARIANCE_OF_J_WITH_DOMAIN_COMPATIBILITY
- **Type:** `MATHEMATICAL_IDENTITY`
- **Truth Status:** `PROVED_IDENTITY`
- **Milestone:** `TP2-G6-B-R2`
- **Statement:** "Under parabolic rescaling $u_\lambda(x, t) = \lambda u(\lambda x, \lambda^2 t)$, the intrinsic lookback relative production satisfies $J_\lambda(a) \equiv J_0(a)$ for all $\lambda > 0$ on $\mathbb{R}^3$ and across rescaled tori $\mathbb{T}_\lambda^3$. On the fixed unit torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$, $u_\lambda$ is lattice-compatible if and only if $\lambda \in \mathbb{N}$, for which $J_n(a) \equiv J_1(a)$ strictly."
- **Dependencies:** `CLM-003`, `CLM-024`

### `CLM-032`: RIGID_BRANCH_AUDITED_SYNTHESIS_AND_CORRECTION
- **Type:** `PROJECT_SYNTHESIS`
- **Truth Status:** `VERIFIED_SYNTHESIS`
- **Milestone:** `TP2-G6-B-R2`
- **Statement:** "Fail-closed re-audit of the rigid-branch adversarial attack: Inter-solution data families (R-A) smoothly realize vanishing relative production $J_n(a) \to 0$ without stretching (shear, Beltrami). Under active stretching, gradient injection $T = (\nabla S)\omega$ is a conditional scaling hypothesis rather than a proved universal obstruction (counter-configurations exist where $\nabla S = 0$). True singular Branch-R continuation (R-C) remains strictly OPEN."
- **Dependencies:** `CLM-024`, `CLM-029`, `CLM-031`
