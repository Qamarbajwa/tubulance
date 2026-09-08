# TP2-G6-C1: ADVERSARIAL BENCHMARK STRESS MATRIX

## Work Package WP12: System Benchmark Evaluations for Two-Particle Transport

---

### 1. Benchmark Suite Overview

In accordance with **Mathematical Research Constitution v1.0.1** (Axiom AEV-2, Adversarial Stress Testing), this work package evaluates the two-particle relative transport framework against six rigorous benchmark flow configurations:

1. **BM-C1-01**: Uniform Time-Varying Translation (Exact NS).
2. **BM-C1-02**: Periodic Planar Shear Flow (Exact NS).
3. **BM-C1-03**: Corrected 3D Beltrami Eigenflow (Exact NS).
4. **BM-C1-04**: 3D Hyperbolic Saddle Point (Kinematic Strain Model).
5. **BM-C1-05**: The A2 Missed Spike Configuration with Pair Trajectories.
6. **BM-C1-06**: Synthetic Rough Energy Drift ($u \in L^2_t H^1_x$).

---

### 2. Detailed Benchmark Evaluation Matrix

| Benchmark ID | Physical Velocity Field | Exact Navier–Stokes? | Coupling Tested | Pair Separation $\delta A_s$ | Covariance Rank $\operatorname{rank}(C_s^{\text{pair}})$ | High-Vorticity Coverage $\mathcal{H}_{\text{seg}}$ | Deformation-Weight Behavior | Benchmark Verdict |
|---|---|---|---|---|---|---|---|---|
| **BM-C1-01** | $u(x, t) = U(t)$<br>(Uniform translation) | **YES**<br>($\Delta u = 0$, $\nabla p = -\dot{U}$) | C-SYNC & C-IND | C-SYNC: $\delta A_s \equiv h$<br>C-IND: $h + \sqrt{4\nu} B_s$ | C-SYNC: Rank 1 ($h \otimes h$)<br>C-IND: Rank 3 ($\lambda_3 = 4\nu \Delta t$) | N/A<br>($\omega \equiv 0$) | N/A<br>($\omega = 0$) | **PASS**<br>(Common-mode cancels identically; confirms Thm 2.1) |
| **BM-C1-02** | $u = (U(y, t), 0, 0)$<br>$\omega = (0, 0, -U_y)$ | **YES**<br>($\partial_t U = \nu U_{yy}$) | C-SYNC & C-IND | $\delta A_s^y = h_y$<br>$\delta A_s^z = h_z$<br>$\delta A_s^x = h_x - \int \delta U ds$ | C-SYNC: **Rank 1** (centered)<br>C-IND: Rank 3 (Brownian only) | Localized in $y$; does not spread in $z$ under C-SYNC | Decouples from $U_y$ gradient via neutral direction | **OBSTRUCTED**<br>(C-SYNC remains rank 1; confirms CLM-029) |
| **BM-C1-03** | $\operatorname{curl} u = \lambda u$<br>(Beltrami eigenflow) | **YES**<br>($u(t) = e^{-\nu \lambda^2 t} u_0$) | C-SYNC | Exponential separation along chaotic trajectories | Full rank 3 via 3D chaotic Lagrangian stretching | Core does not blow up; smooth decay | Stretching uncoupled from vortex production ($\omega \cdot S \omega = 0$) | **PASS**<br>(Exposes 3D stretching without blowup) |
| **BM-C1-04** | $\nabla u = \operatorname{diag}(\lambda_1, \lambda_2, \lambda_3)$<br>$\lambda_1 > 0 > \lambda_3$, $\operatorname{tr}=0$ | Kinematic local model | C-SYNC | $\delta A_s^i = h_i e^{-\lambda_i(t-s)}$<br>(stretches along $e_1$, contracts along $e_3$) | Rank 1 along $e_1$<br>(dominated by $\lambda_1$) | Particles expelled along unstable axis | $\delta Z_s$ extinguished if $\nabla \omega \parallel e_3$; amplified if $\parallel e_1$ | **OBSTRUCTED**<br>(Deformation decoupling survives in pair framework) |
| **BM-C1-05** | Candidate spike $M_n \to \infty$<br>Background velocity $U_n$<br>Core $r_n = \nu^{1/2} M_n^{-1/2}$ | Asymptotic local scaling | C-SYNC & C-IND | Common $U_n$ cancelled!<br>Internal strain rate $M_n$ expels segment | C-SYNC: Rank 1<br>C-IND: Transverse $\lambda_3 \sim \nu M_n^{-1} \to 0$ | Segment misses unless center is within $r_n$ ($|E| \sim M_n^{-3/2} \to 0$) | Decoupling extinguishes history weight in core | **OBSTRUCTED**<br>(Overcomes sweeping, but fails on internal strain & decoupling) |
| **BM-C1-06** | Rough drift $u \in L^2_t H^1_x$<br>with $M|\nabla u| \in L^2_t L^2_x$ | Weak solution envelope | C-SYNC & C-IND | $S_2(h) \le |h|^2 \|\nabla u\|_2^2$<br>holds on spatial average | Depends on spatial direction spectrum | Lebesgue average $\ne$ pathwise trajectory probability | $\int M|\nabla u| ds$ diverges along singular paths | **OBSTRUCTED**<br>(Supercritical Serrin deficit prevents pathwise closure) |

---

### 3. Key Analytical Deductions from the Benchmark Suite

#### 3.1 Confirmation of Common-Mode Triumph (BM-C1-01 & BM-C1-05)
Benchmarks BM-C1-01 and BM-C1-05 verify that Theorem 2.1 is mathematically robust: the background translation velocity $U_n$, which completely destroyed single-particle coverage in BM-A2-04, **cancels identically from the relative equations of motion**. In relative coordinates, the two particles do not experience uniform translation.

#### 3.2 Survival of Deformation–Vorticity Decoupling (BM-C1-04 & BM-C1-05)
Benchmark BM-C1-04 proves that **two-particle transport does not eliminate the deformation-vorticity decoupling obstruction**:
- In the presence of local strain rate $\lambda \sim M_n$, the separation vector stretches along the unstable axis ($\delta A_s^1 \sim |h| e^{M_n(t-s)}$) and contracts along the stable axis ($\delta A_s^3 \sim |h| e^{-M_n(t-s)}$).
- If the physical vorticity gradient $\nabla \omega$ aligns with the stable axis, the transported difference $\delta Z_s$ is multiplied by $e^{-M_n(t-s)}$, driving the two-particle weight $W_s^\nabla \to 0$ inside the high-vorticity core.
- Conversely, in hyperbolic saddles where $\nabla \omega \sim 1$, alignment with the unstable axis amplifies $W_s^\nabla$ by $e^{2 M_n(t-s)}$, concentrating the two-particle history measure outside the core.

#### 3.3 The Covariance Shear Barrier (BM-C1-02)
Benchmark BM-C1-02 confirms that under Coupling C-SYNC, planar shear flows produce **zero transverse relative motion** ($\delta A_s^y \equiv h_y, \delta A_s^z \equiv h_z$). Thus, C-SYNC is powerless to generate multidirectional dispersion in anisotropic geometries, maintaining the rank-1 barrier of `CLM-029`. Under C-IND, full rank is generated solely by isotropic Brownian noise ($4\nu \Delta t$), which carries no dynamical fluid information.
