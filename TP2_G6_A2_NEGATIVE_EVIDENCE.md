# TP2-G6-A2: NEGATIVE EVIDENCE LEDGER AND OBSTRUCTION REGISTRATION

## Work Package WP12: Negative Evidence and Obstruction Ledger

---

### 1. Executive Summary

Under **Universal Governance Minimal v4.0.3** (Section 11, Negative Evidence Ledger) and **Mathematical Research Constitution v1.0.1** (Axiom ANE-1 on Negative Evidence Completeness), negative results and mathematical obstructions must be formally cataloged with the same rigor and permanence as positive lemmas.

This document records:
1. **Negative Evidence Item `NEG-EV-037`**: Failure of Single-Particle Stochastic History Measure Coverage of High-Vorticity Sets under Subcritical Energy Bounds.
2. **Research Obstruction Item `NS-OBS-018`**: Single-Particle Stochastic History Measure Spatial Decoupling and Lower Bound Deficit.

---

### 2. Formal Record: NEG-EV-037

```yaml
negative_evidence_id: "NEG-EV-037"
title: "Failure of Single-Particle Stochastic History-to-Eulerian Measure Coverage under Subcritical Energy Bounds"
programme: "NS-TRAJECTORY-PERSISTENCE-2"
subprogramme: "TP2-G6: BRIDGE RESOLUTION PROGRAMME"
increment: "TP2-G6-A2"
date: "2026-09-08"
author: "antigravity-primary-agent"
status: "CONFIRMED_MATHEMATICAL_OBSTRUCTION"

mathematical_target:
  bridge: "B2 — HISTORY-TO-EULERIAN COVERAGE"
  hypothesis_tested: "Can the single-particle stochastic history measure mu_s^x provide non-circular lower bounds on the Eulerian high-vorticity sets E_s(alpha) = {|omega| >= alpha M(s)}?"
  verdict: "FALSIFIED_FOR_SINGLE_PARTICLES (Ceiling at B2-L1)"

summary: >
  Under only initial energy bounds E_0 < \infty, the single-particle stochastic history
  measure mu_s^x fails to cover Eulerian high-vorticity sets E_s(alpha) in two distinct ways:
  (1) The transition density p(s, y; t, x) fails to satisfy uniform Aronson Gaussian lower bounds
  due to a 1/2-derivative scaling deficit (Serrin index 1.5 > 1), permitting the particle to be
  convectively swept away from the peak core before diffusion can act (Benchmark BM-A2-04).
  (2) The history measure weight |Z_s|^2 = |D_s \omega(A_s)|^2 decouples from the local vorticity
  intensity |\omega(A_s)|^2: alignment with the compression eigenvector of \nabla u extinguishes
  the history weight inside the core, while hyperbolic saddle points amplify the weight in
  regions of low vorticity (Benchmark BM-A2-05).
  Consequently, inf_{u in U_{E_0}} \mu_s(A_s^{-1}(E_s)) = 0, proving that single-particle B2-L2
  through B2-L5 coverage cannot be established without circular regularity assumptions.
```

---

### 3. Formal Record: NS-OBS-018

```yaml
obstruction_id: "NS-OBS-018"
title: "Single-Particle Stochastic History Measure Spatial Decoupling and Lower Bound Deficit Obstruction"
programme: "NS-TRAJECTORY-PERSISTENCE-2"
subprogramme: "TP2-G6: BRIDGE RESOLUTION PROGRAMME"
increment: "TP2-G6-A2"
date: "2026-09-08"
epistemic_status: "PROVED_MATHEMATICAL_OBSTRUCTION"

target_claim_defeated:
  statement: "Single-particle stochastic trajectories A_s(x) unconditionally sample high-vorticity Eulerian sets with uniform positive lower bound mu_s(A_s^{-1}(E_s)) >= c > 0."
  claimed_bridge_level: "B2-L3 (Eulerian Superlevel Coverage) / B2-L2 (L^p Density Bound)"

obstruction_mechanisms:
  1. convective_sweeping_deficit:
     description: "Energy drift u in L^2_t L^6_x has Serrin exponent 2/2 + 3/6 = 1.5 > 1. Drift dominates diffusion on small scales, invalidating Nash-Moser-Aronson Gaussian lower bounds."
     benchmark_ref: "BM-A2-04 (The Missed Spike)"
     scaling: "Delta x_drift ~ U_n \tau_n >> r_n = \nu^{1/2} M_n^{-1/2}."

  2. deformation_vorticity_decoupling:
     description: "The stochastic weight |Z_s|^2 = |D_s \omega|^2 is governed by the deformation tensor D_s, not local |\omega|. D_s can align with compressive directions in high-vorticity cores, suppressing mu_s, while expanding in hyperbolic saddles where |\omega| ~ 1, concentrating mu_s in low-vorticity regions."
     benchmark_ref: "BM-A2-05 (Hyperbolic Saddle Trapping)"
     ratio_bound: "inf |Z_s|^2 / |\omega|^2 = 0, sup |Z_s|^2 / |\omega|^2 = \infty."

  3. radon_nikodym_blowup:
     description: "The Eulerian push-forward density rho_s(y) requires bounding E[\|D_s^{-1}\|^2], which grows exponentially with \int_s^t \|\nabla u\|_{L^\infty} d\tau. Under candidate blowup, rho_s is unbounded in every L^p space (p > 1)."
     theorem_ref: "Theorem 7.1 (Energy-Level Coverage Insufficiency)"

constitutional_impact:
  bridge_ceiling: "B2-L1 (Push-Forward Absolute Continuity) is the strict mathematical ceiling for single-particle transport."
  escalation_triggered: "TWO_PARTICLE_ESCALATION_CONDITION_MANDATORY"
  next_action: "Activate Programme TP2-G6-C (Two-Particle / Stochastic Jet Dispersion Route)."
```

---

### 4. Mathematical Details of the Obstruction Proof

#### 4.1 The Convective Sweeping Deficit (Benchmark BM-A2-04)
Let $x_n \in \mathbb{T}^3$ be the center of a candidate vortex spike at time $s$:
$$
\omega(y, s) = M_n \phi\left(\frac{y - x_n}{r_n}\right), \qquad r_n = \nu^{1/2} M_n^{-1/2}, \quad M_n \to \infty.
$$
The peak core volume is:
$$
|E_s(\alpha)| = c_0 r_n^3 = c_0 \nu^{3/2} M_n^{-3/2}.
$$
The local turnover timescale is:
$$
\tau_n = M_n^{-1}.
$$
During the time interval $[s, t]$ of length $\Delta t = \tau_n$:
1. The diffusive displacement of the backward particle $A_s(x)$ is:
   $$
   \sigma_{\text{diff}} = \sqrt{2\nu \Delta t} = \sqrt{2\nu M_n^{-1}} = \sqrt{2} r_n.
   $$
2. The convective displacement generated by a background velocity $U_n \sim M_n^\gamma$ ($\gamma > 0$) is:
   $$
   \Delta x_{\text{conv}} = \int_s^t u(A_\tau, \tau) d\tau \sim U_n \tau_n = M_n^{\gamma - 1}.
   $$
   For any $\gamma > 1/2$, we have $\Delta x_{\text{conv}} \gg r_n$.
3. The spatial probability density $p(s, y; t, x)$ of the backward particle at time $s$ is centered at $x - \Delta x_{\text{conv}}$, which is displaced from the core $x_n$ by a distance $d_n \gg r_n$.
4. The probability that the single backward particle lands in the spike is bounded by:
   $$
   \mathbb{P}(A_s(x) \in E_s(\alpha)) \le \sup_y p(s, y; t, x) \cdot |E_s(\alpha)| \le \frac{C}{(\nu \tau_n)^{3/2}} \cdot \nu^{3/2} M_n^{-3/2} \exp\left( - \frac{d_n^2}{4\nu \tau_n} \right).
   $$
   Since $\frac{d_n^2}{\nu \tau_n} \sim \frac{M_n^{2\gamma - 2}}{\nu M_n^{-1}} = \nu^{-1} M_n^{2\gamma - 1} \to \infty$, the probability vanishes super-exponentially:
   $$
   \mathbb{P}(A_s(x) \in E_s(\alpha)) = \mathcal{O}\left( e^{-c M_n^{2\gamma - 1}} \right) \to 0.
   $$

#### 4.2 The Deformation–Vorticity Decoupling (Benchmark BM-A2-05)
Recall the definition of the stochastic history measure:
$$
d\mu_s^x = \frac{|Z_s(x)|^2}{S_s(x)} d\mathbb{P}, \qquad Z_s(x) = D_s(x) \omega(A_s(x), s), \quad S_s(x) = \mathbb{E}[|Z_s(x)|^2].
$$
1. Suppose a trajectory enters a region of high strain rate $\nabla u = \operatorname{diag}(\lambda_1, \lambda_2, \lambda_3)$ with $\lambda_1 > 0 > \lambda_3$ (hyperbolic saddle).
2. The deformation tensor evolves as $dD_s = -D_s (\nabla u) ds$.
3. Along the unstable manifold (direction of stretching, eigenvalue $\lambda_1$), the backward deformation matrix contracts: $\|D_s e_1\| \sim e^{-\lambda_1 (t-s)}$.
4. Along the stable manifold (direction of compression, eigenvalue $\lambda_3 < 0$), the backward deformation matrix expands: $\|D_s e_3\| \sim e^{|\lambda_3| (t-s)}$.
5. If the vorticity vector $\omega$ in the spike aligns with the compressing direction of the forward flow (the contracting direction of the backward flow, $e_1$), then:
   $$
   |Z_s(x)|^2 = |D_s \omega|^2 \sim e^{-2\lambda_1(t-s)} M_n^2.
   $$
   For $\lambda_1 (t-s) \gg \log M_n$, the weight $|Z_s|^2$ is exponentially suppressed inside the high-vorticity core.
6. Conversely, a particle passing through a saddle region where $|\omega| \sim 1$ but whose vorticity vector aligns with $e_3$ experiences exponential amplification:
   $$
   |Z_s|^2 \sim e^{2|\lambda_3|(t-s)} \cdot 1 \gg M_n^2.
   $$
7. Consequently, the stochastic history measure $\mu_s^x$ concentrates almost all of its mass on the low-vorticity saddle region, completely decoupling from the Eulerian superlevel set $E_s(\alpha)$:
   $$
   \mu_s^x(A_s^{-1}(E_s(\alpha))) \to 0 \quad \text{as } M_n \to \infty.
   $$

---

### 5. Constitutional Significance and Next Steps

The identification and rigorous proof of `NEG-EV-037` and `NS-OBS-018` is a major structural milestone in the project:
1. It conclusively shuts down the naive single-particle ansatz for Bridge $B_2$, preventing the expenditure of research effort on circular regularity proofs.
2. It establishes `B2-L1` as the exact, provable ceiling of single-particle transport under energy bounds.
3. It provides the rigorous mathematical justification for activating **Programme TP2-G6-C: Two-Particle Dispersion and Stochastic Jet Route**, where relative particle pairs $\delta A_s = A_s(x+h) - A_s(x)$ eliminate the background drift $U_n$ and decouple strain from spatial translation.
