# External Evidence Intake: Alpöge–Buckmaster & Córdoba–Martínez-Zoroa Euler Singularity Results
## Intake ID: `EXT-INTAKE-20260908-ABCMZ-001`

**Intake Date:** `2026-09-08`  
**Intake Status:** `INTAKE_RECORDED_NOT_ASSIMILATED`  
**Governing Standard:** Universal Governance Minimal v4.0.3 & Mathematical Research Constitution v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** Strictly **`UNRESOLVED`**  

---

## 1. Programme A: Alpöge–Buckmaster / Córdoba–Martínez-Zoroa Route

- **Authors:** Levent Alpöge and Tristan Buckmaster.
- **Construction Strategy:** Córdoba–Martínez-Zoroa-type iterative blow-up construction; parabolic/hyperbolic coordinate collapse with computer-assisted and formal verification techniques.
- **Target Equation:** Forced 3D incompressible Euler equations with smooth external forcing ($f \ne 0$) on $\mathbb{R}^3$.
- **Formalization:** Public `fluid_lean` repository formalized in Lean 4 (authored by the paper's authors / formalization team as supported by the public repository).
- **Ledger ID:** `EXT-004` (`INTAKE_RECORDED_NOT_ASSIMILATED`).
- **Transfer Status:** `NO_DIRECT_TRANSFER_ESTABLISHED`.

---

## 2. Programme B: Ganeshram–Duruisseaux–Anandkumar Candidate Route

- **Authors:** Vignesh Ganeshram, Valentin Duruisseaux, and Anima Anandkumar.
- **Scope & Methodology:** Independent research programme exploring machine-assisted singularity detection, physics-informed neural networks (PINNs), and computer-assisted numerical bounding in Euler dynamics.
- **Epistemic Classification:** Candidate / numerical / PINN-supported route. Because a complete, self-contained, and rigorous analytical stability proof is not yet established in available peer-reviewed literature, this route is classified strictly as a numerical candidate rather than an established blowup theorem.
- **Independence:** Distinct and unmerged from the Alpöge–Buckmaster programme.
- **Ledger ID:** `EXT-005` (`INTAKE_RECORDED_NOT_ASSIMILATED`).
- **Transfer Status:** `NO_DIRECT_TRANSFER_ESTABLISHED`.

---

## 3. Strict Navier–Stokes Statement B Transfer Analysis

> [!WARNING]
> **This external evidence does NOT resolve or alter the Clay Millennium Prize Problem Statement B for 3D Navier–Stokes.**

### Exact Physical and Mathematical Mismatch:

$$
\boxed{
\text{forced Euler on }\mathbb{R}^3
\quad\neq\quad
\text{unforced Navier–Stokes on }\mathbb{T}^3
}
$$

1. **Viscous Dissipation:**  
   Standard incompressible Navier–Stokes introduces the additional positive-viscosity term

   $$
   \nu\Delta u,
   $$

   producing high-frequency dissipation absent from Euler. The currently assimilated public evidence does not establish whether the Alpöge–Buckmaster / Córdoba–Martínez-Zoroa amplification construction extends to the standard unforced Navier–Stokes Statement-B target.

2. **External Forcing:**  
   The Alpöge–Buckmaster construction explicitly relies on smooth external forcing $f \ne 0$ to sustain unstable self-similar profiles. Clay Statement B strictly specifies autonomous unforced flow ($f \equiv 0$).

3. **Spatial Domain:**  
   The external blowup construction is on $\mathbb{R}^3$, whereas Statement B is strictly posed on the flat periodic torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$.

---

## 4. Program Disposition & Next Actions

- **Disposition:** Neutral external evidence recorded for research memory and literature awareness under `NO_DIRECT_TRANSFER_ESTABLISHED`.
- **Intake Status:** Retained strictly as `EXT-004 = INTAKE_RECORDED_NOT_ASSIMILATED` and `EXT-005 = INTAKE_RECORDED_NOT_ASSIMILATED`.
- **Exploratory Programme Status:** The exploratory investigation programme `NS-EXT-ABCMZ-001` is **NOT** launched.
- **Clay Statement B Status:** Strictly **`UNRESOLVED`**.

