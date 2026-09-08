# TP2-G6-C1: CIRCULARITY FIREWALL AND REGULARITY CONDITION AUDIT

## Work Package WP13: Epistemic Classification of Two-Particle Estimates

---

### 1. Executive Summary and Constitutional Purpose

Under **Universal Governance Minimal v4.0.3** and the **Mathematical Research Constitution v1.0.1** (Axiom ARC-1, Non-Circularity), this work package evaluates every mathematical quantity, identity, and estimate developed in increment `TP2-G6-C1`.

The goal of this audit is to prevent circularity: ensuring that no analytical step relies on regularity hypotheses (such as $\|\nabla u\|_{L^\infty} \in L^1_t$, Beale–Kato–Majda, or Ladyzhenskaya–Prodi–Serrin integrability) as an unproven premise in a line of reasoning intended to investigate regularity.

---

### 2. Epistemic Classification Taxonomy

Every mathematical statement in `TP2-G6-C1` is assigned to one of five strict epistemic classes:

1. **`NON_CIRCULAR`**: Provable unconditionally from the Navier–Stokes equations and initial energy bounds $\mathcal{E}_0 < \infty$, or exact kinematic/geometric identities holding for all $C^1$ vector fields.
2. **`CONDITIONAL_SUBCRITICAL`**: A bound that holds unconditionally in an integral or average sense, but which cannot be upgraded to pointwise/pathwise control without additional hypotheses.
3. **`CONTINUATION_EQUIVALENT`**: A condition quantitatively or logically equivalent to global regularity past candidate blowup $T^*$ by classical PDE criteria.
4. **`CIRCULAR`**: An assumption that directly assumes the target conclusion or invokes a `CONTINUATION_EQUIVALENT` premise to claim a regularity result.
5. **`UNKNOWN_DEPENDENCE`**: An unverified dependency requiring further mathematical decomposition.

---

### 3. Formal Circularity Firewall Matrix

| Mathematical Object / Estimate | Analytical Expression | Epistemic Classification | Justification & Dependency Boundary |
|---|---|---|---|
| **Common-Mode Cancellation** | $u(A^{(2)}) - u(A^{(1)}) = v(A^{(2)}) - v(A^{(1)})$ | **`NON_CIRCULAR`** | Exact algebraic identity. Valid for all vector fields. Eliminates uniform translation $U(t)$ without regularity assumptions. |
| **Pathwise Relative SDE (C-SYNC)** | $d(\delta A_s) = - \mathcal{S}_s \delta A_s ds$ | **`NON_CIRCULAR`** | Exact consequence of fundamental theorem of calculus along straight segments for any $C^1$ field. |
| **Independent Relative SDE (C-IND)** | $d(\delta A_s) = - \mathcal{S}_s \delta A_s ds + \sqrt{4\nu} dB_s$ | **`NON_CIRCULAR`** | Exact Itô differential. Relative noise is a standard 3D Brownian motion scaled by $\sqrt{4\nu}$. |
| **Separation Energy Itô Correction** | $+ 12\nu\, ds$ in $d|\delta A_s|^2$ | **`NON_CIRCULAR`** | Exact trace of $4\nu I_3$: $\operatorname{tr}(4\nu I_3) = 3 \times 4\nu = 12\nu$. |
| **Non-Collision of Independent Paths** | $\mathbb{P}(\tau_0 \in [0, t]) = 0$ in $d=3$ | **`NON_CIRCULAR`** | Kakutani's theorem (1944). Points are polar for 3D Brownian motion. Repulsive drift $+ 4\nu/r_s$. |
| **Second-Order Jet limit $\Xi^{\text{pair}}$** | $\frac{\|D_s J_\omega D_s + H_s : \omega\|_F^2}{|D_s \omega|^2}$ | **`NON_CIRCULAR`** | Exact Taylor expansion of $Z_s(x+h) - Z_s(x)$ under C-SYNC. Bilateral deformation pullback. |
| **$L^2$ Structure Function Bound** | $S_2(h, t) \le |h|^2 \|\nabla u(t)\|_{L^2}^2$ | **`NON_CIRCULAR`** | Follows from Jensen's inequality and Fubini on $\mathbb{T}^3$. Exact for all $H^1$ fields. |
| **Time-Integrated $S_2(h)$ Bound** | $\int_0^T S_2(h, t) dt \le \frac{\mathcal{E}_0}{2\nu} |h|^2$ | **`NON_CIRCULAR`** | Direct consequence of Leray energy inequality $\nu \int_0^T \|\nabla u\|_{L^2}^2 dt \le \mathcal{E}_0$. |
| **Maximal Function Increment Bound** | $|u(x+h) - u(x)| \le C |h| (M|\nabla u|(x) + M|\nabla u|(x+h))$ | **`CONDITIONAL_SUBCRITICAL`** | Hajłasz inequality. Holds Lebesgue-a.e. with $M|\nabla u| \in L^2_t L^2_x$. |
| **Pathwise Exponential Bound on $|\delta A_s|$** | $|\delta A_s| \le |h| \exp(C \int_s^t M|\nabla u| d\tau)$ | **`CONDITIONAL_SUBCRITICAL`** | Valid pathwise, but exponential moment diverges because Serrin index of $M|\nabla u|$ is $2.5 > 1$. |
| **Uniform Pathwise Lipschitz Bound** | $\|\nabla u(\cdot, t)\|_{L^\infty} \le C(t)$ with $\int_0^{T^*} C(t) dt < \infty$ | **`CONTINUATION_EQUIVALENT`** | Beale–Kato–Majda theorem (1984). Assuming this premise assumes regularity. |
| **Uniform Pair Transition Density Bound** | $p_{\text{rel}}(s, y; t, x, h) \ge c (t-s)^{-3/2} e^{-C \frac{|y-h|^2}{t-s}}$ | **`CONTINUATION_EQUIVALENT`** | Aronson theorem (1968). Requires drift in Serrin class $\frac{2}{q} + \frac{3}{p} \le 1$. Energy drift misses by $0.5$. |
| **Uniform Bounding of Jet $D_s$ or $H_s$** | $\sup_{s \in [0, t]} \|D_s\| \le C < \infty$ as $t \to T^*$ | **`CONTINUATION_EQUIVALENT`** | Equivalent to $\int_0^{T^*} \|\nabla u\|_{L^\infty} ds < \infty$ (BKM). |
| **Decoupling Immunity Assumption** | Assuming $W_s^\nabla \ge c |\nabla \omega(A_s)|^2$ in cores | **`CIRCULAR`** | Quarantined by BM-C1-04: deformation tensor $D_s$ aligns with compressing axes, extinguishing $W_s^\nabla$. |

---

### 4. Enforcement Protocols

1. **Firewall Protocol FP-C1-1**: The exact identities (Common-mode cancellation, SDE derivations, $12\nu$ Itô correction, $S_2(h)$ bound, $\Xi^{\text{pair}}$ jet limit) are certified **`NON_CIRCULAR`** and enter the canonical repository as permanent foundations.
2. **Firewall Protocol FP-C1-2**: Any attempt to infer pathwise exponential bounds on $|\delta A_s|$ or relative transition density lower bounds from the energy-level bounds is blocked by the **supercritical Serrin deficit** ($2.5 > 1$).
3. **Firewall Protocol FP-C1-3**: Bridge $B_2$ and Bridge $B_3$ cannot be declared closed in C1. Increment C1 establishes the exact foundation; quantitative dispersion theorems require the multi-particle ensemble methods of C2.
