# TP2-G6-C1: NEGATIVE EVIDENCE LEDGER AND RESEARCH OBSTRUCTION REGISTRATION

## Work Package WP15: Formal Negative Evidence and Structural Obstruction Catalog

---

### 1. Executive Summary

In strict compliance with **Universal Governance Minimal v4.0.3** (Section 11, Negative Evidence Ledger) and the **Mathematical Research Constitution v1.0.1** (Axiom ANE-1, Negative Evidence Completeness), this document records the structural obstructions and negative findings established during the investigation of increment `TP2-G6-C1`.

While `TP2-G6-C1` successfully proved the **Common-Mode Cancellation Theorem** (decisively eliminating the uniform sweeping deficit of A2), our adversarial stress-testing identified a profound mathematical dilemma at the core of the two-particle framework: the **Brownian Coupling Duality Dilemma** (`NS-OBS-019`).

We formally register:
1. **Negative Evidence Record `NEG-EV-038`**: Failure of Synchronous Two-Particle Transport to Provide Autonomous Relative Diffusion and Multidirectional Dispersion in Planar Shear.
2. **Research Obstruction Record `NS-OBS-019`**: The Two-Particle Brownian Coupling Duality Dilemma and Strain Decoupling Persistence Obstruction.

---

### 2. Formal Record: NEG-EV-038

```yaml
negative_evidence_id: "NEG-EV-038"
title: "Failure of Synchronous Two-Particle Transport to Provide Autonomous Relative Diffusion and Multidirectional Dispersion in Planar Shear"
programme: "NS-TRAJECTORY-PERSISTENCE-2"
subprogramme: "TP2-G6: BRIDGE RESOLUTION PROGRAMME"
route: "TP2-G6-C — TWO-PARTICLE DISPERSION AND STOCHASTIC JET ROUTE"
increment: "TP2-G6-C1"
date: "2026-09-08"
author: "antigravity-primary-agent"
status: "CONFIRMED_MATHEMATICAL_OBSTRUCTION"

mathematical_target:
  bridges: ["B2 — HISTORY-TO-EULERIAN COVERAGE", "B3 — COVARIANCE SPECTRUM"]
  hypotheses_tested:
    - "Hypothesis 1: Synchronous Brownian coupling (C-SYNC) provides relative stochastic diffusion to sample Eulerian high-vorticity sets."
    - "Hypothesis 2: Two-particle relative transport unconditionally overcomes the rank-1 covariance obstruction of CLM-029 in periodic shear flows."
  verdict: "FALSIFIED_FOR_SYNCHRONOUS_COUPLING"

summary: >
  Under Coupling C-SYNC (where both particles share the same Brownian motion), the Brownian noise
  cancels identically pathwise: d(\delta A_s) = -\mathcal{S}_s \delta A_s ds.
  This has two fatal negative consequences:
  (1) The relative diffusivity is identically zero (\nu_rel = 0). If the velocity gradient vanishes,
  the particles undergo rigid translation with zero relative spreading, failing to provide autonomous
  stochastic exploration of spatial domains.
  (2) In 1D periodic shear flows u = (U(y), 0, 0), the transverse separations are strictly constant:
  \delta A_s^y \equiv h_y, \delta A_s^z \equiv h_z. Consequently, the centered fluctuating pair
  covariance tensor \tilde{C}_s^pair remains strictly rank 1 (\lambda_2 = \lambda_3 = 0), confirming
  that C-SYNC cannot overcome the covariance spectral underdetermination of CLM-029.
```

---

### 3. Formal Record: NS-OBS-019

```yaml
obstruction_id: "NS-OBS-019"
title: "The Two-Particle Brownian Coupling Duality Dilemma and Strain Decoupling Persistence Obstruction"
programme: "NS-TRAJECTORY-PERSISTENCE-2"
subprogramme: "TP2-G6: BRIDGE RESOLUTION PROGRAMME"
route: "TP2-G6-C — TWO-PARTICLE DISPERSION AND STOCHASTIC JET ROUTE"
increment: "TP2-G6-C1"
date: "2026-09-08"
epistemic_status: "PROVED_STRUCTURAL_OBSTRUCTION"

target_claim_defeated:
  statement: "Two-particle stochastic Lagrangian transport simultaneously preserves the stochastic jet limit (\Xi connection) and provides autonomous relative spatial diffusion to close Bridge B2 and B3 under subcritical energy bounds."
  claimed_bridge_level: "B2-L3 (Eulerian Superlevel Coverage) / B3 (Multidirectional Dispersion)"

obstruction_mechanisms:
  1. brownian_coupling_duality_dilemma (C-OBS-7):
     description: >
       The two-particle framework is split into two mutually exclusive regimes:
       - Regime C-SYNC (Synchronous Noise): Preserves spatial flow differentiability and generates
         the exact stochastic jet limit D_s = \lim \delta A_s / h and bilateral pullback \Xi^pair,
         but has zero relative diffusion (\nu_rel = 0), failing to provide autonomous spatial spreading.
       - Regime C-IND (Independent Noise): Provides genuine 3D relative Brownian diffusion
         (d|\delta A_s|^2 = -2 \delta A \cdot \delta u ds + 12\nu ds + martingale) and full-rank
         covariance (\lambda_3 \ge 4\nu \Delta t), but completely destroys spatial differentiability:
         the difference quotient \delta A_s / |h| explodes as |h|^{-1} almost surely, severing the
         direct connection to the deterministic flow derivative D_s and the canonical \Xi framework.
       No single Brownian coupling simultaneously possesses both flow differentiability and autonomous
       relative diffusion.

  2. persistent_strain_decoupling (C-OBS-3):
     description: >
       While Theorem 2.1 eliminates uniform background translation U(t), the relative velocity
       increment \delta u \approx S \delta A is governed by the local strain tensor S.
       In candidate blowup cores with strain rate \sim M_n, the separation vector stretches along the
       unstable manifold, expelling particles from the core. Furthermore, the deformation tensor D_s
       continues to multiply the vorticity gradient in \delta Z_s = D_s \delta \omega + (\nabla D_s) \omega,
       leaving the two-particle history weights vulnerable to alignment-induced extinction in compressive
       strain regions (Benchmark BM-C1-04).

constitutional_impact:
  bridge_status: "B2 and B3 remain UNRESOLVED within increment C1."
  authorizing_condition: "Increment C1 establishes foundational SDEs and common-mode cancellation, but requires C2 to address the coupling duality via multi-scale / scale-dependent noise coupling."
  next_action: "Proceed to C1 Synthesis and prepare C2 (Quantitative Pair Dispersion)."
```

---

### 4. Detailed Mathematical Analysis of Obstruction Mechanisms

#### 4.1 The Coupling Duality Proof
Let $A_s^{(1)}$ and $A_s^{(2)}$ be two backward trajectories with separation $\delta A_s = A_s^{(2)} - A_s^{(1)}$:
$$
d(\delta A_s) = - \left[ u(A_s^{(2)}, s) - u(A_s^{(1)}, s) \right] ds + \sqrt{2\nu} dW_s^{(2)} - \sqrt{2\nu} dW_s^{(1)}.
$$
Let the cross-correlation between the Brownian motions be parameterized by a correlation tensor $\rho(x, x+h) \in \mathbb{R}^{3 \times 3}$:
$$
\mathbb{E}[ dW_s^{(1)} \otimes dW_s^{(2)} ] = \rho(x, x+h)\, ds.
$$
1. **Case $\rho \equiv I$ (C-SYNC)**:
   $$
   \mathbb{E}\left[ |dW_s^{(2)} - dW_s^{(1)}|^2 \right] = 2\nu \operatorname{tr}(I + I - 2I) ds = 0.
   $$
   The noise cancels pathwise.
   - Flow map $x \mapsto A_s(x)$ is $C^1$-diffeomorphic.
   - Jet limit $\lim_{h \to 0} \frac{\delta A_s}{h} = D_s(x)$ exists pathwise.
   - But relative diffusion is zero: $\operatorname{Var}(\delta A_s \mid u \equiv 0) = 0$. Two particles cannot diffuse apart.
2. **Case $\rho \equiv 0$ (C-IND)**:
   $$
   \mathbb{E}\left[ |dW_s^{(2)} - dW_s^{(1)}|^2 \right] = 2\nu \operatorname{tr}(I + I) ds = 4\nu \times 3\, ds = 12\nu\, ds.
   $$
   Relative diffusion is strictly positive: $\operatorname{Var}(\delta A_s \mid u \equiv 0) = 4\nu (t - s) I$.
   - But the difference quotient satisfies:
     $$
     \frac{\delta A_s}{h} = I - \int_s^t \frac{\delta u}{h} d\tau + \frac{\sqrt{4\nu} (B_t - B_s)}{h}.
     $$
     Because $|B_t - B_s| > 0$ almost surely for $s < t$, as $|h| \to 0$ the quotient diverges as $|h|^{-1}$.
   - The flow map fails to be differentiable; no spatial tangent vector exists.

**Conclusion**: The requirements of **spatial differentiability** (for the $\Xi$ jet framework) and **autonomous relative diffusion** (for spatial coverage) are in fundamental tension under constant Brownian couplings.

---

### 5. Architectural Significance

The discovery and formalization of `NS-OBS-019` and `NEG-EV-038`:
1. Prevents unjustified claims that "two particles automatically solve everything that one particle lost."
2. Proves that common-mode cancellation (Theorem 2.1) is a necessary breakthrough, but not a sufficient closure.
3. Points the mathematical research toward **scale-dependent Brownian couplings** (where $\rho(h) \approx I$ for $|h| \ll r_n$ and $\rho(h) \to 0$ for $|h| \gg r_n$), which provides the exact theoretical motivation for successor milestone `TP2-G6-C2`.
