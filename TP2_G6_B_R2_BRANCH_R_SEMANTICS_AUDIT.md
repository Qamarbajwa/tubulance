# TP2-G6-B-R2: Semantic Disambiguation of Branch R Realization

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R2 (Audit Question 3)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$  
**Target Status:** `UNRESOLVED`  

---

## 1. The Three Semantic Regimes of Branch R

A critical ambiguity identified in `TP2-G6-B-R1` was the unqualified statement that Branch R was "smoothly realized" by periodic shear and Beltrami flows as amplitude $A_n \to \infty$.

To preserve absolute epistemic integrity, the project formally partitions the concept of Branch R into three distinct mathematical regimes:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               REGIME R-A: INTER-SOLUTION AMPLITUDE FAMILY              │
│  A sequence of distinct smooth initial data {u_0^(n)} where            │
│  M_n -> infty and J_n(a) -> 0 across different physical solutions.      │
│  Canonical Status: SURROGATE_RIGID_SIGNATURE_REALIZED_ACROSS_DATA_FAMILY│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ distinct from
┌───────────────────────────────────▼────────────────────────────────────┐
│      REGIME R-B: SINGLE SMOOTH SOLUTION HIGH-INTENSITY SEQUENCE        │
│  A single fixed smooth global solution u(x, t) with evaluation points   │
│  (x_n, t_n) where M_n is large and J_n(a) is small (e.g. transient     │
│  turbulent burst without blow-up).                                     │
│  Canonical Status: SMOOTH_TRANSIENT_RIGID_REGIME                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ distinct from
┌───────────────────────────────────▼────────────────────────────────────┐
│              REGIME R-C: HYPOTHETICAL BLOW-UP SEQUENCE                 │
│  A single solution approaching finite-time singularity t_n -> T_* < infty│
│  with M_n = ||omega(t_n)||_L^\infty -> infty and J_n(a) -> 0.          │
│  Canonical Status: DANGEROUS_BLOWUP_BRANCH_R (Direct Target of Clay B) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Formal Classification of R1 Benchmark Findings

1. **What R1 Actually Proved:**
   The periodic shear family $U_n(y, t) = A_n e^{-\nu k^2 t} \sin(ky)$ and the constant-speed Beltrami family with $A_n \to \infty$ establish **Regime R-A only**:
   \[
   \boxed{ \mathbf{CLASSIFICATION:\ SURROGATE\_RIGID\_SIGNATURE\_REALIZED\_ACROSS\_DATA\_FAMILY} }
   \]
   They demonstrate that across a family of varying initial data profiles, one can drive $M_n \to \infty$ while the relative-history production $J_n(a) \to 0$.
2. **What R1 Did NOT Prove:**
   R1 did **not** prove that a single solution can develop a finite-time singularity while maintaining $J_n(a) \to 0$ (Regime R-C).
   Nor did R1 prove that Regime R-C is impossible for solutions with active vortex stretching.
3. **Disambiguation Rule:**
   No inter-solution amplitude sequence ($A_n \to \infty$) may be promoted or cited as an exclusion or realization of the Clay continuation branch (Regime R-C).
   All occurrences of "Branch R realized" in R1 artifacts are formally re-designated as `SURROGATE_RIGID_SIGNATURE_REALIZED_ACROSS_DATA_FAMILY`.

---

## 3. Epistemic Impact on Bridge $B_1$

This disambiguation sharpens the frontier of Bridge $B_1$:
- The fact that laminar amplitude families (R-A) have $J_n(a) \to 0$ does **not** falsify the potential role of $\Xi$ in controlling hypothetical blow-up sequences (R-C).
- Rather, it proves that any non-circular regularity theorem based on $\Xi$ must differentiate between laminar/shear geometries (where $M_n \to \infty$ is benign initial data scaling) and genuine nonlinear vortex-stretching blowup sequences (where enstrophy production diverges).
