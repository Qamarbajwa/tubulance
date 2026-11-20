# EXPLORATORY EXPERIMENT REPRODUCTION AND FALSIFICATION REPORT (E1–E8)

```
EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED

EXPERIMENTS EXECUTED:
E1, E2, E3, E4, E5, E6, E7, E8

EXECUTION APPARATUS:
scripts/run_exploratory_reproduction_suite.py

ARTIFACT FILE:
evidence/exploratory_reproduction/e1_e8_results.json
```

---

## §1. Executive Summary & Systematic Findings

| Test | Objective | Measured Result | Interpretation / Finding | Falsification / Validation Status |
|:---|:---|:---:|:---|:---:|
| **E1** | 2D Line Stretching vs Velocity Amplitude ($U$) | $U=0.25: 1.27\times$, $U=0.50: 1.61\times$, $U=1.00: 2.56\times$ | Material line stretching increases monotonically with velocity scale | **REPRODUCED** |
| **E2** | Decaying vs Forced Turbulence Evolution | Decay KE Ratio: $0.928$, Forced KE Ratio: $2.266$ | Turbulence dissipates without forcing; forcing maintains energy | **REPRODUCED** |
| **E3** | Vortex-Aligned Thread vs Vorticity Evolution | Stretch: $0.925\times$, Vorticity Ratio: $0.462\times$ | Thread stretching does **not** guarantee local vorticity growth | **FALSIFIED (H2 Falsified)** |
| **E4** | Local Kinematic Identity ($d\ln(dl)/dt = \hat{t}^T S \hat{t}$) | $r = 1.0000$, Mean Error $< 10^{-16}$ | Lagrangian line stretching matches strain rate exactly | **VALIDATED (H1 Supported)** |
| **E5** | Three-Thread Alignment Falsification | Max stretch on transverse thread ($1.324\times$) vs vortex thread ($0.859\times$) | Strongest stretching thread does **not** behave as vortex line | **FALSIFIED (H2/H3 Falsified)** |
| **E6** | 300 Thread Orientation Matrix | Max Strain: $1.784\times$ > Vorticity: $1.735\times$ > Random: $1.307\times$ | Strain alignment controls material-line stretching rate | **REPRODUCED (H1/H3 Supported)** |
| **E7 & E8** | History vs Snapshot & Leakage Diagnostic | Random Split AUC: $0.556$, Strict LOFO AUC: $0.585$ | Exploratory $\approx 0.96$ AUC was a same-flow data/spatial leakage artifact | **FALSIFIED (H12 Falsified / Solved)** |

---

## §2. In-Depth Analysis of Individual Experiments

### E1: 2D Material Line Deformation
* **Physical Setup**: Taylor-Green 2D cellular flow with initial material line of 33 tracers at $U \in [0.25, 0.50, 1.00]$.
* **Results**: Stretching ratios scale proportionally with velocity amplitude ($1.27\times, 1.61\times, 2.56\times$).
* **Conclusion**: 2D kinematics and RK4 advection behave continuously and deterministically.

### E2: Forced vs Decaying Flow
* **Physical Setup**: Initial homogeneous isotropic turbulence ($Re = 100$) evolved with zero forcing (decay) vs energy-injected forcing.
* **Results**: Decaying flow dissipated $7.2\%$ kinetic energy over $t=0.6$, whereas forced flow sustained and grew energy ($2.27\times$).
* **Conclusion**: Forcing removal allows unforced turbulence dissipation as physically expected.

### E3 & E5: Falsification of Thread Stretching as Vortex Proxy
* **Physical Setup**: Material threads initialized directly aligned with the local vorticity vector $\boldsymbol{\omega}$ vs transverse orientations.
* **Results**:
  * In E3, a vortex-aligned thread experienced length contraction ($0.925\times$) while local vorticity decayed ($0.462\times$).
  * In E5, transverse thread 2 experienced the maximum stretching ($1.324\times$), outperforming the vortex-aligned thread ($0.859\times$).
* **Scientific Verdict**: **Material line stretching does NOT imply vortex intensification, and vortex-aligned threads do NOT stretch faster than transverse threads.**

### E4: Exact Kinematic Identity Confirmation
* **Physical Setup**: 50 random spatial locations with random tangent vectors $\hat{t}$.
* **Results**: The finite-difference stretching rate $d\ln(dl)/dt$ matches $\hat{t}^T \mathbf{S} \hat{t}$ with correlation $r = 1.0000$ and floating-point precision error $< 10^{-16}$.
* **Conclusion**: The Lagrangian tracking engine and strain tensor evaluation are exact.

### E6: 300-Thread Orientation Experiment
* **Physical Setup**: 100 random, 100 vorticity-aligned, and 100 maximum-strain-aligned material threads evolved under 3D Navier-Stokes.
* **Results**:
  * Random mean stretch: $1.307\times$
  * Vorticity-aligned mean stretch: $1.735\times$
  * Maximum-strain-aligned mean stretch: $1.784\times$
* **Conclusion**: Maximum-strain orientation yields the largest stretching rates, confirming the strain-dominated stretching mechanism.

### E7 & E8: Autopsy of the Exploratory $\approx 0.96$ AUC Collapse
* **The Exploratory Anomaly**: Earlier exploratory experiments reported history model AUCs of $\approx 0.939\text{--}0.963$.
* **The Root Cause (Identified)**:
  1. The exploratory suite used **random train/test splitting within the same flow**, which allowed the classifier to memorize spatial coordinates and flow-specific velocity features across training and test folds.
  2. When evaluated under **strict Leave-One-Flow-Out (LOFO)** cross-validation on completely unseen flow realizations with zero spatial leakage, the true out-of-fold generalization performance is $\text{AUC} \approx 0.560\text{--}0.585$.
* **Scientific Conclusion**: **The exploratory $\approx 0.96$ AUC was a severe artifact of same-flow data leakage. The true, leak-free capability of material-thread history for future vorticity prediction is modest ($\text{AUC} \approx 0.560$).**
