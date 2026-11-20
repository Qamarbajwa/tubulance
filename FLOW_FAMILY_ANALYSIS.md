# FLOW-FAMILY ANALYSIS & HIGH-PRIORITY PHYSICS+PARTICLE REPORT

```
EXPERIMENT INVESTIGATION:
EXPANDED 8-FLOW TOPOLOGICAL DECOMPOSITION & PHYSICS COMPLEMENTARITY
(TH2 VALIDATION & PHASE 8 TEST)

EVIDENCE STATUS:
LEVEL 2 — TECHNICALLY VERIFIED
NOT EXTERNALLY ATTESTED

FLOW REALIZATIONS:
8 INDEPENDENT FLOWS (4 ISOTROPIC DECAY G1, 4 STRUCTURED G3)

SAMPLE POPULATION:
512 TOTAL MATERIAL OBJECTS (3,584 SAMPLES ACROSS REPRESENTATIONS)

SOURCE ARTIFACT:
evidence/flow_family_analysis_results.json
```

---

## §1. Flow-Family Hypothesis (TH2) Evaluation

**Hypothesis TH2**: *The predictive value of material connectivity depends on flow topology, large-scale anisotropy, and coherent structure.*

### Comparative Performance by Flow Family

| Metric | G1 Isotropic Turbulence (4 Seeds) | G3 Structured Flows (2 TG + 2 Shear Layer) | Full 8-Flow Combined | Family Dependence Verdict |
|:---|:---:|:---:|:---:|:---:|
| **P0 Point-Particle History ROC** | **$0.7231$** | $0.5329$ | $0.6280$ | Isotropic Point Dominance ($+0.1902$) |
| **P1 Material-Thread History ROC** | $0.4892$ | **$0.5890$** | $0.5391$ | Structured Thread Advantage ($+0.0998$) |
| **Connectivity Effect ($C_{\text{ROC}} = P1 - P0$)** | **$-0.2339$** | **$+0.0561$** | **$-0.0889$** | **Strong Family Divergence ($\Delta = +0.2900$)** |
| **Memory Effect ($M_{\text{ROC}} = P1_{\text{ord}} - P1_{\text{shuff}}$)** | $-0.0086$ | **$+0.0676$** | $+0.0295$ | Memory preserved in structured flows |
| **Eulerian Physics Alone ROC** | $0.7854$ | **$0.8945$** | $0.8399$ | High baseline across all regimes |
| **Physics + P0 Particle History ROC** | $0.8033$ | $0.8640$ | $0.8336$ | Slight lift in G1 ($+0.0179$), penalty in G3 |
| **Physics + P1 Thread History ROC** | $0.7677$ | $0.8890$ | $0.8284$ | Consistent slight penalty |

---

## §2. Per-Flow Topological Ledger

| Flow ID | Family | Tier | Prevalence | P0 Particle ROC | P1 Thread ROC | Connectivity $C_{\text{ROC}}$ | Memory $M_{\text{ROC}}$ | Physics ROC | Physics+P0 ROC | Physics+P1 ROC |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `flow_iso_seed101` | Isotropic | G1 | $0.250$ | $0.7865$ | $0.5039$ | $-0.2826$ | $-0.0312$ | $0.7891$ | $0.8346$ | $0.7253$ |
| `flow_iso_seed102` | Isotropic | G1 | $0.250$ | $0.7487$ | $0.4583$ | $-0.2904$ | $+0.0339$ | $0.7760$ | $0.7708$ | $0.7383$ |
| `flow_iso_seed103` | Isotropic | G1 | $0.219$ | $0.6914$ | $0.5629$ | $-0.1286$ | $-0.0029$ | $0.8400$ | $0.8814$ | $0.8529$ |
| `flow_iso_seed104` | Isotropic | G1 | $0.312$ | $0.6659$ | $0.4318$ | $-0.2341$ | $-0.0341$ | $0.7364$ | $0.7261$ | $0.7545$ |
| `flow_tg_phase01` | Taylor-Green | G3 | $0.359$ | $0.4878$ | $0.5133$ | $+0.0255$ | $-0.0339$ | $0.9555$ | $0.9088$ | $0.9385$ |
| `flow_tg_phase02` | Taylor-Green | G3 | $0.125$ | $0.4688$ | $0.6942$ | $+0.2254$ | $+0.2210$ | $0.9911$ | $0.9598$ | $0.9821$ |
| `flow_shear_layer01`| Shear Layer | G3 | $0.219$ | $0.5357$ | $0.5729$ | $+0.0371$ | $-0.0129$ | $0.7643$ | $0.7429$ | $0.7671$ |
| `flow_shear_layer02`| Shear Layer | G3 | $0.312$ | $0.6391$ | $0.5754$ | $-0.0638$ | $+0.0964$ | $0.8673$ | $0.8445$ | $0.8682$ |

---

## §3. Analysis of High-Priority Phase 8 Test (Physics vs Physics + History)

1. **Eulerian Physics Dominance**:
   * Instantaneous Eulerian field variables (strain rate, local vorticity, velocity gradients) achieve an out-of-fold generalization score of $\text{ROC} = 0.8399$.
2. **Lagrangian Point-Particle Complementarity ($G_{\text{particle}}$)**:
   * Adding ordered point-particle trajectory history ($\mathbf{x}(\tau)$) yields $\text{ROC} = 0.8336$ (overall $\Delta = -0.0063$).
   * In isotropic decay (G1), adding point particle history provides modest positive synergy ($\Delta = +0.0179$), raising ROC from $0.7854$ to $0.8033$.
   * In structured flows (G3), adding particle trajectories slightly lowers out-of-fold generalization ($\Delta = -0.0305$).
3. **Lagrangian Material Thread Complementarity ($G_{\text{thread}}$)**:
   * Adding 1D material thread geometry history to physics yields $\text{ROC} = 0.8284$ ($\Delta = -0.0116$).
4. **Conclusion**:
   * Lagrangian memory does **not** provide universal incremental value over instantaneous Eulerian physics for downstream vorticity forecasting.
   * However, in homogeneous isotropic turbulence, single-particle Lagrangian trajectory histories capture advective transport that slightly enhances Eulerian forecasts.
