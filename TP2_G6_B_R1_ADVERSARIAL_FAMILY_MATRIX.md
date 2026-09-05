# TP2-G6-B-R1: Adversarial Flow Family Benchmark Matrix

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R1 (Work Package 2)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Objective and Evaluation Methodology

Work Package 2 re-evaluates all canonical project flow families and benchmark configurations against the hardened Branch-R signature:
\[
M_n \to \infty, \quad J_n(a) = 2\nu \int_{s_n}^{t_n} \mathbb{E}_{\mu_r}[\Xi_r] dr \to 0, \quad \frac{\omega \cdot S \omega}{|\omega|^2} > 0.
\]
For each family, we rigorously compute or bound:
- Vorticity $|\omega|$ and stretching rate $\frac{\omega \cdot S \omega}{|\omega|^2}$.
- Denominator $R = |D_s \omega|^2$ and Numerator $N = \|D_s J_\omega\|_F^2$.
- Primary Relative QV Density $\Xi = N/R$.
- Amplitude and Direction components $M_D, C_D$.
- Accumulated Intrinsic-Window Production $J_n(a)$.
- Covariance Tensor $C_s$, its trace $\operatorname{tr}(C_s)$, eigenvalues $\lambda_i(C_s)$, and determinant $\det(C_s)$.

---

## 2. Adversarial Benchmark Flow Families

### Family 1: Unforced Periodic Shear Family (`CLM-005`)
- **Velocity Field:** $u(x, y, z, t) = (U(y, t), 0, 0)$ on $\mathbb{T}^3$, with $U(y, t) = A e^{-\nu k^2 t} \sin(ky)$.
- **Navier–Stokes Solution:** Solves unforced 3D Navier–Stokes on $\mathbb{T}^3$ exactly:
  \[
  \partial_t U = \nu \partial_{yy} U, \quad (u \cdot \nabla)u = 0, \quad \nabla p = 0, \quad \nabla \cdot u = 0.
  \]
- **Vorticity & Gradient:**
  \[
  \omega = (0, 0, -U_y) = (0, 0, -A k e^{-\nu k^2 t} \cos(ky)), \quad M(t) = A k e^{-\nu k^2 t}.
  \]
  \[
  J_\omega = \nabla \omega = -U_{yy} (e_3 \otimes e_2) = (A k^2 e^{-\nu k^2 t} \sin(ky)) (e_3 \otimes e_2).
  \]
- **Vortex Stretching:**
  \[
  S = \frac{1}{2} U_y (e_1 \otimes e_2 + e_2 \otimes e_1) \implies \omega \cdot S \omega = 0 \quad (\text{Vortex stretching is identically zero}).
  \]
- **Cauchy Deformation Action:**
  \[
  D_s = I + \alpha(s, t) (e_1 \otimes e_2), \quad \alpha(s, t) = \int_s^t U_y(y(r), r) dr.
  \]
  Since $(e_1 \otimes e_2)(e_3 \otimes e_2) = 0$ and $(e_1 \otimes e_2) e_3 = 0$:
  \[
  D_s J_\omega \equiv J_\omega = -U_{yy} (e_3 \otimes e_2), \quad D_s \omega \equiv \omega = -U_y e_3.
  \]
- **Relative QV Density $\Xi$:**
  \[
  R = |D_s \omega|^2 = U_y^2, \quad N = \|D_s J_\omega\|_F^2 = U_{yy}^2 \implies \Xi = \frac{U_{yy}^2}{U_y^2} = k^2 \tan^2(ky) = \kappa_\omega^2.
  \]
  *Critical Feature:* $\Xi$ is strictly independent of amplitude $A$ and deformation $\alpha$.
- **Components $M_D$ and $C_D$:**
  Since deformation acts as identity on $\omega$ and $J_\omega$:
  \[
  M_D \equiv \Xi = k^2 \tan^2(ky), \quad C_D \equiv 0.
  \]
- **Intrinsic Window Production $J_n(a)$:**
  At $t_n = 0$, $M_n = A_n k \to \infty$ as $A_n \to \infty$.  
  Lookback window $L_n = a / M_n = \frac{a}{A_n k} \to 0$.  
  Over $[ -L_n, 0 ]$, $U(y, r)$ and $y(r)$ vary by $\mathcal{O}(L_n) = \mathcal{O}(A_n^{-1})$.  
  Since $\mathbb{E}_{\mu_r}[\Xi_r] = \mathcal{O}(k^2)$ is uniformly bounded:
  \[
  \boxed{ J_n(a) = 2\nu \int_{-L_n}^0 \mathbb{E}_{\mu_r}[\Xi_r] dr \sim 2\nu k^2 L_n = \frac{2\nu k a}{A_n} \longrightarrow 0 \quad \text{as } A_n \to \infty }.
  \]
- **Covariance Tensor $C_s$ and Spectral Audit:**
  \[
  D_r J_\omega = -U_{yy} (e_3 \otimes e_2) \implies (D_r J_\omega)(D_r J_\omega)^\top = U_{yy}^2 (e_3 \otimes e_3) = \operatorname{diag}(0, 0, U_{yy}^2).
  \]
  \[
  \boxed{ C_s = \operatorname{diag}\left(0, 0, 2\nu \int_s^T \mathbb{E}[U_{yy}^2] dr\right) }.
  \]
  - $\operatorname{tr}(C_s) = 2\nu \int_s^T \mathbb{E}[U_{yy}^2] dr > 0$.
  - $\lambda_1(C_s) = \operatorname{tr}(C_s)$, $\lambda_2(C_s) = 0$, $\lambda_3(C_s) = 0$.
  - $\det(C_s) \equiv 0, \quad \frac{\lambda_{\min}(C_s)}{\operatorname{tr}(C_s)} \equiv 0$.
- **Adversarial Assessment:** Periodic shear **realizes the Branch-R signature $J_n(a) \to 0$ smoothly** as $A_n \to \infty$, and demonstrates **maximal covariance rank deficiency ($\operatorname{rank} C_s = 1$)**. However, it **completely lacks nonlinear vortex stretching** ($\omega \cdot S \omega = 0$).

---

### Family 2: Decaying 3D Beltrami Eigenflows (`CLM-013`)
- **Velocity Field:** $\nabla \times u_0 = \lambda u_0$ on $\mathbb{T}^3$ ($\lambda \neq 0$), $u(x, t) = e^{-\nu \lambda^2 t} u_0(x)$.
- **Navier–Stokes Solution:**
  Because $(u \cdot \nabla)u = (\nabla \times u) \times u + \frac{1}{2} \nabla |u|^2 = \frac{1}{2} \nabla |u|^2 = -\nabla p$, the nonlinear advection is a pure gradient absorbed completely by pressure. $u(x, t)$ solves unforced Navier–Stokes exactly.
- **Vorticity & Stretching:**
  \[
  \omega(x, t) = \lambda u(x, t) \implies \omega \parallel u \implies (\omega \cdot \nabla)u = \lambda (u \cdot \nabla)u = \lambda \nabla p.
  \]
  The nonlinear vortex stretching rate is identically zero:
  \[
  \omega \cdot S \omega = \omega \cdot \nabla\left(\frac{1}{2}|u|^2\right) = \lambda u \cdot \nabla\left(\frac{1}{2}|u|^2\right) = 0 \quad (\text{since } \nabla \cdot u = 0).
  \]
- **Deformation & Gradient Growth:**
  For chaotic 3D Beltrami flows (such as ABC flows), the forward/backward flow has positive Lyapunov exponents, causing $\|D_s\| \sim e^{\sigma_L \tau}$ for large lookback $\tau$.
  However, in the high-intensity sequence $A_n \to \infty$, $M_n \sim \lambda A_n \to \infty$, so the intrinsic window shrinks to:
  \[
  L_n = \frac{a}{M_n} \sim \frac{a}{\lambda A_n} \longrightarrow 0.
  \]
  Over $[t_n - L_n, t_n]$, the accumulated deformation is:
  \[
  \|D_s - I\| \le \int_{t_n - L_n}^{t_n} \|\nabla u\| dr \le L_n (\lambda A_n) = a = \mathcal{O}(1).
  \]
  Deformation is bounded by $e^a$ independent of $A_n$.
- **Intrinsic Window Production $J_n(a)$:**
  Since $\Xi_r \le \operatorname{Cond}(D)^2 \kappa_\omega^2 \le e^{2a} \lambda^2$, we have:
  \[
  \boxed{ J_n(a) \le 2\nu e^{2a} \lambda^2 L_n = \frac{2\nu e^{2a} \lambda a}{A_n} \longrightarrow 0 \quad \text{as } A_n \to \infty }.
  \]
- **Covariance Tensor:**
  Because trajectories in 3D ABC flows disperse in all directions over long times, $C_s$ is full rank ($\operatorname{rank} C_s = 3$) for large horizons $T - s$. But over the shrinking window $L_n \to 0$, $C_s = \mathcal{O}(L_n) \to 0$.
- **Adversarial Assessment:** Beltrami flows **realize Branch R smoothly ($J_n(a) \to 0$)** as amplitude $A_n \to \infty$, but nonlinear vortex stretching is **depleted by pressure**.

---

### Family 3: 2D Invariant Subspace Flows
- **Velocity Field:** $u = (u_1(x, y, t), u_2(x, y, t), 0)$ with $\partial_z u = 0$.
- **Vorticity:** $\omega = (0, 0, \omega_3(x, y, t))$.
- **Vortex Stretching:** $\omega \cdot S \omega \equiv 0$ identically everywhere for all time.
- **Deformation:** $D_s = \begin{pmatrix} D_{2\times 2} & 0 \\ 0 & 1 \end{pmatrix}$.
- **Vorticity Martingale:** $Z_s = D_s \omega = (0, 0, \omega_3(A_s, s))$.
- **Covariance Tensor:**
  $J_\omega = \nabla \omega = \begin{pmatrix} 0 & 0 \\ 0 & 0 \\ \partial_x \omega_3 & \partial_y \omega_3 \end{pmatrix} = e_3 \otimes \nabla_{x,y} \omega_3$.
  Thus $(D_s J_\omega)(D_s J_\omega)^\top = |\nabla_{x,y} \omega_3|^2 (e_3 \otimes e_3)$, which is **strictly rank 1**:
  \[
  \boxed{ C_s = \operatorname{diag}\left(0, 0, 2\nu \int_s^T \mathbb{E}[|\nabla \omega_3|^2] dr\right), \quad \lambda_2(C_s) = \lambda_3(C_s) \equiv 0 }.
  \]
- **Adversarial Assessment:** 2D flows possess no stretching and cannot produce singularity. Covariance is strictly rank 1.

---

### Family 4: Kinematic Decoupling Matrix Configuration (`CLM-012`)
- **Ansatz:** $D_K = \operatorname{diag}(K, 1, 1/K) \in SL(3, \mathbb{R})$, $\omega = e_1$, $G = J_\omega = e_3 \otimes e_2$.
- **Stretching Metrics:**
  \[
  \mathcal{A}_\omega = \frac{|D_K \omega|^2}{|\omega|^2} = K^2, \quad \mathcal{A}_{\text{grad}} = \frac{\|D_K G\|_F^2}{\|G\|_F^2} = \frac{1}{K^2}.
  \]
  \[
  \Theta = \frac{\mathcal{A}_{\text{grad}}}{\mathcal{A}_\omega} = K^{-4} \longrightarrow 0 \quad \text{as } K \to \infty.
  \]
- **QV Density:** $\Xi = \kappa_\omega^2 \Theta = \kappa_\omega^2 K^{-4}$.
- **Navier–Stokes Compatibility Audit:**
  - *Kinematic Realizability:* $D_K$ is an exact matrix in $SL(3, \mathbb{R})$.
  - *Dynamic Navier–Stokes Realizability:* **UNREALIZED AS AN EXACT SMOOTH SOLUTION**.
    Generating $D_s = \operatorname{diag}(K, 1, 1/K)$ requires $\nabla u \approx \operatorname{diag}(-\gamma, 0, \gamma)$ with $\gamma > 0$ sustained over time $\tau = \ln K / \gamma$. But aligning $\omega$ permanently along the stretching axis while $J_\omega$ aligns along the contracting axis is dynamically unstable under Navier–Stokes: the vortex line rotation equation ($D_t \xi = (S - (\xi \cdot S \xi)I)\xi$) and the gradient transport equation ($(D_t - \nu \Delta)G = SG - GA + T$) rotate the axes dynamically.
- **Classification:** `KINEMATIC_ONLY_NOT_DYNAMICAL_NS` (Bridge Target $B_0$ unless dynamical realization is established).

---

## 3. Comparative Master Matrix

| Flow Family | NS Exact? | Nonlinear Stretching $\frac{\omega \cdot S \omega}{|\omega|^2}$ | $M_n \to \infty$ Possible? | Intrinsic $J_n(a)$ Limit | $\operatorname{rank}(C_s)$ | $\lambda_2, \lambda_3$ | Realizes Branch R? |
|---|---|---|---|---|---|---|---|
| **1. Periodic Shear** | **YES** | $\equiv 0$ | **YES** ($A_n \to \infty$) | $\to 0$ ($\mathcal{O}(A_n^{-1})$) | **1** | $\equiv 0$ | **YES** (Trivially: No stretching) |
| **2. 3D Beltrami** | **YES** | $\equiv 0$ | **YES** ($A_n \to \infty$) | $\to 0$ ($\mathcal{O}(A_n^{-1})$) | 3 | $> 0$ for large $\tau$ | **YES** (Trivially: Pressure cancels) |
| **3. 2D Flow** | **YES** | $\equiv 0$ | **YES** | $\to 0$ | **1** | $\equiv 0$ | **YES** (Trivially: 2D smooth) |
| **4. Kinematic Decoupling** | **NO** (Kinematic) | $> 0$ (Algebraic) | **YES** ($K \to \infty$) | $\Xi \to 0$ | N/A | N/A | **KINEMATIC ONLY** |
| **5. Dangerous Singular Target** | **UNKNOWN** | $> 0$ | **YES** ($M_n \to \infty$) | **?** | **?** | **?** | **THE CORE QUESTION** |

---

## 4. Key Mathematical Conclusions of WP2

1. **Branch R is Smoothly Realizable in the Absence of Stretching:**
   Smooth Navier–Stokes solutions can easily produce $M_n \to \infty$ and $J_n(a) \to 0$ simultaneously, provided nonlinear vortex stretching is identically zero (Shear, Beltrami).
2. **Covariance Trace Does Not Guarantee Tensor Non-Degeneracy:**
   Periodic shear and 2D flows provide exact smooth Navier–Stokes counterexamples where $\operatorname{tr}(C_s) > 0$ while $C_s$ is strictly rank 1 ($\lambda_2 = \lambda_3 = 0$). This establishes decisive negative evidence for Bridge $B_3$: **trace bounds cannot enforce multidirectional dispersion**.
3. **The Unresolved Core of Branch R:**
   Can Branch R ($J_n(a) \to 0$) be realized in a flow family with **active, non-zero nonlinear vortex stretching** $\omega \cdot S \omega > 0$? This question is investigated in WP3.
