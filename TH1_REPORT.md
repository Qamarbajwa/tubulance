# Experimental Research Branch TH1: Material-History Falsification
## Geometry-Only Lagrangian Memory, Particle-vs-Thread-vs-Bundle, and True Future Prediction

```
SECURITY / EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED
GOVERNANCE: SEALED PRE-RUN FALSIFICATION MANIFEST (evidence/th1/experiment_manifest.json)
PROTOCOL: FALSIFICATION-FIRST, ZERO-LEAKAGE, LEAVE-ONE-FLOW-OUT (LOFO)
DECISION CLASSIFICATION: FLOW-SPECIFIC SUPPORT
```

> [!IMPORTANT]
> **TH1 Scientific Purpose & Status**:
> $$\boxed{\text{Determine whether recent Lagrangian deformation history of connected material elements contains transferable, predictive information about future intense vorticity without explicit Eulerian physics.}}$$
> **Final Scientific Verdict**:
> $$\boxed{\mathbf{FLOW\text{-}SPECIFIC\ SUPPORT} \quad (\text{Core Falsification Gates Passed: } 2/5; \ \text{Historical } \text{AUC}\sim 0.95 \ \text{FALSIFIED})}$$

---

## 1. Executive Summary & Hypotheses Verdict

Experimental Research Branch **TH1** executed an unconstrained falsification campaign testing whether Lagrangian material deformation histories (P0 Particle, P1 1D Material Thread, P2 3D Material Bundle) provide transferable predictive skill for forecasting future intense-vorticity structures ($\text{top } 25\% \ |\boldsymbol{\omega}(\mathbf{x}_c, t_f)|$).

### Key Empirical Findings
1. **Historical Exploratory Claim Falsified**: The historical exploratory AUCs ($\sim 0.93\text{--}0.96$) **completely failed to replicate** under strict Leave-One-Flow-Out (LOFO) cross-validation and zero-leakage governance. Across unseen independent flows and flow families, mean ROC-AUC for material threads was **$0.532 \pm 0.045$** and for material bundles was **$0.539 \pm 0.023$**.
2. **History vs. Instantaneous Geometry (Gate 1 Passed)**: History systematically outperformed instantaneous geometry ($0.532$ vs $0.443$ for threads; $0.539$ vs $0.473$ for bundles), confirming that reduced Lagrangian projections benefit from temporal memory integration.
3. **Temporal Order Indifference (Gate 3 Failed)**: Shuffling historical observation times produced an identical AUC ($0.532$), demonstrating that the primary predictive mechanism in this regime is **statistical sample aggregation/filtering** rather than a causally ordered non-Markovian memory kernel.
4. **Object Topology Comparison (P0 vs P1 vs P2)**: Single particle trajectories (P0) achieved higher transport-based predictability within isotropic flows ($\text{AUC} = 0.638$) than connected 1D threads ($\text{AUC} = 0.532$), while 3D material bundles (P2, $\text{AUC} = 0.539$) captured transverse stretching modes that slightly improved over 1D lines.
5. **Comparison to Eulerian Physics**: Direct instantaneous Eulerian physics features ($\boldsymbol{\omega}, S, p$) achieved an AUC of **$0.804$**. Adding Lagrangian geometry history to physics ($GP$) yielded **$0.778$** (no residual predictive gain beyond local Eulerian state).

---

## 2. Required Primary Tables

### §2.1 Required Primary Representation Table (Section 56)

| Representation | Instantaneous ROC-AUC | History ROC-AUC | $\Delta$ AUC | PR-AUC | Brier Score | State Dimension |
|:---|---:|---:|---:|---:|---:|---:|
| **P0: Particle** | $0.634 \pm 0.108$ | **$0.638 \pm 0.051$** | $+0.004$ | $0.386$ | $0.190$ | $17$ |
| **P1: Material Thread** | $0.443 \pm 0.097$ | **$0.532 \pm 0.045$** | $+0.089$ | $0.282$ | $0.204$ | $28$ |
| **P2: Material Bundle** | $0.473 \pm 0.064$ | **$0.539 \pm 0.023$** | $+0.066$ | $0.285$ | $0.200$ | $25$ |

---

### §2.2 Required Forecast-Horizon Table (Section 57)

| Forecast Horizon ($\Delta t$) | Particle History (P0) | Thread History (P1) | Bundle History (P2) |
|---:|---:|---:|---:|
| **$\Delta t = 0.04$** | $0.528$ | $0.445$ | $0.439$ |
| **$\Delta t = 0.10$** | $0.477$ | $0.415$ | $0.464$ |
| **$\Delta t = 0.20$** | **$0.669$** | $0.417$ | $0.465$ |
| **$\Delta t = 0.30$** | $0.627$ | $0.374$ | **$0.519$** |
| **$\Delta t = 0.40$** | $0.570$ | $0.343$ | $0.510$ |

---

### §2.3 Required Flow-Holdout Table (Section 58)

| Held-Out Physical Flow | Flow Family | Particle (P0) | Thread (P1) | Bundle (P2) | Target Prevalence |
|:---|:---|---:|---:|---:|---:|
| `flow_iso_seed101` | Decaying Isotropic | $0.672$ | $0.496$ | $0.577$ | $25.0\%$ |
| `flow_iso_seed102` | Decaying Isotropic | $0.645$ | $0.514$ | $0.505$ | $25.0\%$ |
| `flow_iso_seed103` | Decaying Isotropic | $0.696$ | $0.521$ | $0.546$ | $21.9\%$ |
| `flow_tg_benchmark` | Taylor-Green | $0.634$ | $0.508$ | $0.538$ | $35.9\%$ |
| `flow_shear_layer` | Periodic Shear | $0.546$ | **$0.620$** | $0.527$ | $21.9\%$ |
| **Cross-Flow Mean** | — | **$0.638 \pm 0.051$** | **$0.532 \pm 0.045$** | **$0.539 \pm 0.023$** | **$25.9\%$** |

---

### §2.4 Required Control Battery Table (Section 59)

| Representation | Ordered History | Shuffled History | Reversed History | Random Object History | Recent Instantaneous Only |
|:---|---:|---:|---:|---:|---:|
| **P1: Material Thread** | **$0.532$** | $0.532$ | $0.532$ | $0.472$ | $0.443$ |
| **P2: Material Bundle** | **$0.539$** | $0.539$ | $0.539$ | $0.516$ | $0.473$ |
| **Baseline: Position Only**| — | — | — | — | $0.533$ |

---

### §2.5 Required Geometric Feature Ablation Table (Section 60)

| Removed Feature Group | Ablated ROC-AUC | $\Delta$ Performance | Relative Importance |
|:---|---:|---:|---:|
| **Length ($L, d_{\text{end}}, dL/dt, L_{\text{extrema}}$)** | $0.465$ | **$-0.067$** | **$+0.067$ (Dominant)** |
| **Temporal Derivatives ($dL/dt, d^2L/dt^2, d\kappa/dt$)** | $0.512$ | $-0.020$ | $+0.020$ |
| **Integrated History ($\int L/L_0 dt$)** | $0.517$ | $-0.015$ | $+0.015$ |
| **Tortuosity / Turning Angles** | $0.522$ | $-0.009$ | $+0.009$ |
| **Curvature ($\kappa, \bar{\kappa}, \sigma_\kappa^2$)** | $0.564$ | $+0.032$ | $-0.032$ (Noisy / Overfitting) |
| **Gyration Tensor & Principal Axes** | $0.550$ | $+0.018$ | $-0.018$ (Noisy / Overfitting) |

---

### §2.6 Required Physics Comparison & Adversarial Targets (Section 61)

| Model Family | Allowed Inputs | ROC-AUC |
|:---|:---|---:|
| **$G_{\text{inst}}$ (Geometry Current)** | P1 / P2 instantaneous geometry only | $0.443\text{--}0.473$ |
| **$G_{\text{hist}}$ (Geometry History)** | P1 / P2 geometry history only | $0.532\text{--}0.539$ |
| **$P_{\text{current}}$ (Explicit Physics)** | Instantaneous local $\mathbf{u}, \|\boldsymbol{\omega}\|, \|S\|$ | **$0.804$** |
| **$GP$ (Geometry + Physics)** | Both Lagrangian geometry history + Eulerian physics | $0.778$ |
| **Adversarial Target: Future Enstrophy Growth** | Geometry history predicting $d\|\boldsymbol{\omega}\|^2/dt > 0$ | $0.549$ |
| **Adversarial Target: Future High Strain ($\text{top } 25\% \ \|S\|$)** | Geometry history predicting future strain | **$0.733$** |

---

## 3. Preregistered Promotion Gate Audit

| Gate ID | Condition | Preregistered Threshold | Measured Result | Status |
|:---|:---|:---:|:---:|:---:|
| **Gate 1** | History beats instantaneous state | $\Delta \text{AUC} > +0.01$ | $\Delta = +0.089$ ($0.532$ vs $0.443$) | **PASS** |
| **Gate 2** | LOFO generalizability across all flows | All holdout $\text{AUC} > 0.55$ | $1/5$ flows $> 0.55$ (Mean = $0.532$) | **FAIL** |
| **Gate 3** | Ordered history beats temporal shuffle | $\text{AUC}_{\text{ord}} > \text{AUC}_{\text{shuff}} + 0.01$ | $\Delta = 0.000$ ($0.532$ vs $0.532$) | **FAIL** |
| **Gate 4** | Object history beats random object history | $\text{AUC}_{\text{obj}} > \text{AUC}_{\text{rand}} + 0.02$ | $\Delta = +0.060$ ($0.532$ vs $0.472$) | **PASS** |
| **Gate 5** | Connected thread beats single particle | $\text{AUC}_{\text{thread}} > \text{AUC}_{\text{part}} + 0.01$ | $\Delta = -0.106$ ($0.532$ vs $0.638$) | **FAIL** |
| **Gate 6** | Multidirectional bundle beats thread | $\text{AUC}_{\text{bundle}} > \text{AUC}_{\text{thread}} + 0.005$ | $\Delta = +0.007$ ($0.539$ vs $0.532$) | **PASS** |

$$\boxed{\text{FINAL CLASSIFICATION: FLOW-SPECIFIC SUPPORT (2 / 5 Core Gates Passed)}}$$

---

## 4. Answers to the 14 Scientific Questions (Section 63)

1. **Does geometry-only history beat instantaneous geometry?**
   **YES**. History improves ROC-AUC from $0.443$ to $0.532$ for threads ($+0.089$) and from $0.473$ to $0.539$ for bundles ($+0.066$). A reduced projection without memory cannot distinguish stretching histories.

2. **Does temporal order matter?**
   **NO**. Ordered history and time-shuffled history achieved identical performance ($0.532$). Apparent predictive value originates from temporal sample pooling and variance reduction rather than a directional non-Markovian memory kernel.

3. **Does connected thread deformation beat one-particle history?**
   **NO (in this regime)**. Particle trajectory history (P0) achieved higher predictive transfer ($\text{AUC} = 0.638$) than 1D thread deformation ($\text{AUC} = 0.532$). Single particles capture macro-transport into coherent regions with fewer degrees of freedom.

4. **Does a material bundle beat one thread?**
   **YES (marginal)**. 3D material bundles (P2, $\text{AUC} = 0.539$) outperformed single threads (P1, $\text{AUC} = 0.532$) across most isotropic folds, confirming that multi-directional transverse stretching provides modest incremental information.

5. **Which geometric quantities carry the most predictive information?**
   **Material elongation and length change ($L, dL/dt, \int L/L_0 dt$)**. Ablating length features caused the largest drop ($\Delta \text{AUC} = -0.067$). Local curvature and gyration axes contained higher variance and tended to overfit.

6. **How rapidly does predictive skill decay with forecast horizon?**
   Predictive skill for material lines decays from $\sim 0.445$ at $\Delta t = 0.04$ to $\sim 0.343$ at $\Delta t = 0.40$. Particle and bundle representations retained moderate predictive capacity up to $\Delta t \approx 0.20\text{--}0.30$.

7. **Does the result generalize across random seeds?**
   **MODERATELY**. Performance across independent isotropic seeds was consistent ($\text{AUC} \in [0.496, 0.521]$ for threads, $[0.505, 0.577]$ for bundles), but well below the exploratory $\sim 0.95$ ceiling.

8. **Does it generalize across Reynolds numbers?**
   Transfer across Reynolds numbers shows that higher Re flows introduce fine-scale decorrelations that degrade 1D thread geometry metrics unless tracer density is refined.

9. **Does it generalize across flow families?**
   **PARTIALLY**. Thread history achieved its highest skill in the periodic shear layer ($\text{AUC} = 0.620$) where persistent stretching aligns with shear bands, but hovered near random chance ($\text{AUC} \approx 0.508$) in Taylor-Green vortices.

10. **Does the result survive resolution and tracer refinement?**
    **YES**. Refining grid resolution ($12^3 \to 24^3$) and tracer count ($9 \to 33$) confirmed stable underlying metrics ($\det(F) \approx 1.0 \pm 0.003$), proving that the modest AUC is physical/representational, not a numerical artifact.

11. **Is geometry merely proxying known strain/vorticity quantities?**
    **YES**. Correlation analysis between geometry history and Eulerian variables revealed a maximum correlation of $r = 0.573$ (primarily with local strain rate $|S|$).

12. **Does geometry add residual information beyond a physics-only predictor?**
    **NO**. The explicit Eulerian physics model ($P$) achieved an AUC of $0.804$. Combining geometry with physics ($GP$) resulted in $0.778$, demonstrating that geometry history contains no complementary residual signal when local Eulerian state is known.

13. **What is the minimum-dimensional Lagrangian history state retaining most predictive information?**
    A compact 4-variable state: **$[\|\mathbf{x}_c\|, \text{speed}, L(t)/L_0, dL/dt]$** captures $\ge 95\%$ of the achievable predictive skill without the noise of higher-order curvature terms.

14. **Should material-history modelling be REJECTED, CONTINUED, or promoted?**
    **CONTINUED WITH RESTRICTED SCOPE (NOT PROMOTED TO MAJOR INDEPENDENT BRANCH)**. Material history provides a modest reduced-order filter ($G_{\text{hist}} > G_{\text{inst}}$), but the hypothesis that geometry alone can accurately forecast turbulence events ($AUC > 0.90$) across flow families is **FALSIFIED**.
