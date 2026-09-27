# NS_NONLINEAR_SELF_FOCUS_001_R1_DYADIC_TRANSFER_DERIVATION

## Audit of the Dyadic Half-Dissipation Inequality, Explicit Commutator/Paraproduct Cross-Terms, and Partition Orthogonality (`NS-NONLINEAR-SELF-FOCUS-001-R1`, Sections 8, 9, 10 & 23)

| Field | Value |
| :--- | :--- |
| **Milestone ID** | `NS-NONLINEAR-SELF_FOCUS-001-R1` |
| **Parent Milestone** | `NS-NONLINEAR-SELF-FOCUS-001` |
| **Active Governance** | `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3` (`NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`) |
| **Mathematical Authority** | `Mathematical Research Constitution v1.0.1` |
| **Locked Target** | $\mathbb{T}^3_L = (\mathbb{R}/L\mathbb{Z})^3$, $\nu > 0$, $f \equiv 0$ |

---

## 1. Audit of the Dyadic Half-Dissipation Claim (Section 8)

### 1.1 Is $Q_*(t)$ a Median Definition or an Independent Length-Scale Threshold?
In `CLM-041` Part (3), the integer shell index $Q_*(t)$ was defined as:
$$Q_*(t) := \max\!\left(0,\; \left\lfloor \frac{1}{2}\log_2\!\left(\frac{1}{2\,\lambda_{\rm P}\,\bar{\ell}_\omega(t)^2}\right) \right\rfloor\right), \qquad \lambda_{\rm P} = \left(\frac{2\pi}{L}\right)^2.$$
Let us audit the logical structure of this definition:
- $Q_*(t)$ is **not** defined as the empirical median shell $\inf\{Q : \sum_{q \ge Q} D_q^\omega \ge \frac{1}{2}D(t)\}$. Instead, $Q_*(t)$ is defined explicitly as a function of the **global Foias–Temam length scale** $\bar{\ell}_\omega(t) = \|\omega(t)\|_{L^2}/\|\nabla\omega(t)\|_{L^2}$, choosing the largest dyadic shell wavenumber $k_{Q_*}(t) := \lambda_{\rm P}^{1/2}\,2^{Q_*(t)} = \frac{2\pi}{L}\,2^{Q_*(t)}$ satisfying:
  $$k_{Q_*}(t)^2 = \lambda_{\rm P}\,2^{2 Q_*(t)} \le \frac{1}{2\,\bar{\ell}_\omega(t)^2} = \frac{\|\nabla\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2}{2\,\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2}.$$
- **Why does this threshold imply the half-dissipation bound?** Because for any Fourier series $\omega(x) = \sum_{k \ne \mathbf{0}} \hat{\omega}(k)e^{ik\cdot x}$ on $\mathbb{T}^3_L$, the low-frequency sum over $|k| < k_{Q_*}(t)$ satisfies the **static Plancherel–Markov / Chebyshev inequality**:
  $$\sum_{0 < |k| < k_{Q_*}(t)} \nu |k|^2 |\hat{\omega}(k,t)|^2 \,L^3 \le \nu\,k_{Q_*}(t)^2 \sum_{0 < |k| < k_{Q_*}(t)} |\hat{\omega}(k,t)|^2 \,L^3 \le \frac{\nu}{2\,\bar{\ell}_\omega(t)^2}\,\|\omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 = \frac{1}{2}\,D(t).$$
- **Mandatory Epistemic Classification**:
  While $Q_*(t)$ is defined from $\bar{\ell}_\omega(t)$ rather than tautologically as the dissipation median, the resulting inequality $\sum_{|k| \ge k_{Q_*}(t)} \nu|k|^2|\hat{\omega}(k)|^2 L^3 \ge \frac{1}{2}D(t)$ is a **static harmonic-analysis / Markov-tail inequality valid for EVERY mean-zero function $\omega \in H^1(\mathbb{T}^3_L)$**. It does **not** use the Navier–Stokes equations at all!

---

### 1.2 Orthogonal Dyadic Projectors ($P_q$) vs. Smooth Overlapping Littlewood–Paley Blocks ($\dot{\Delta}_q$) (Sections 8 & 10)

A critical technical flaw in the original statement of `CLM-041` Part (3) is the conflation of **sharp $L^2$-orthogonal dyadic shell projectors $P_q$** with **smooth overlapping Littlewood–Paley multipliers $\dot{\Delta}_q$**:

#### Case A: Sharp $L^2$-Orthogonal Dyadic Shell Projectors $P_q$
Define the disjoint dyadic annuli $\mathcal{A}_q := \big\{k \in \frac{2\pi}{L}\mathbb{Z}^3 \setminus \{\mathbf{0}\} : \frac{2\pi}{L}2^q \le |k| < \frac{2\pi}{L}2^{q+1}\big\}$ for $q \ge 0$, and let $\widehat{P_q \omega}(k) := \mathbb{1}_{\mathcal{A}_q}(k)\,\hat{\omega}(k)$.
Because $\{\mathcal{A}_q\}_{q=0}^\infty$ partitions $\frac{2\pi}{L}\mathbb{Z}^3 \setminus \{\mathbf{0}\}$ into mutually disjoint sets, $P_q P_r = \delta_{qr} P_q$ is an **orthogonal projection** in $L^2(\mathbb{T}^3_L)$ and $\dot{H}^1(\mathbb{T}^3_L)$:
$$\sum_{q=0}^\infty \nu \|\nabla P_q \omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 = \nu \|\nabla \omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 = D(t) \qquad (\text{EXACT EQUALITY}).$$
Since every wavevector $k \in \bigcup_{q=0}^{Q_*(t)-1} \mathcal{A}_q$ satisfies $|k| < \frac{2\pi}{L}2^{Q_*(t)} = k_{Q_*}(t)$, we have:
$$\sum_{q=0}^{Q_*(t)-1} \nu \|\nabla P_q \omega(t)\|_{L^2}^2 \le \frac{1}{2}\,D(t) \implies \boxed{\sum_{q=Q_*(t)}^\infty \nu \|\nabla P_q \omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \ge \frac{1}{2}\,D(t)} \qquad (\text{EXACT FOR } P_q).$$

#### Case B: Smooth Overlapping Littlewood–Paley Projectors $\dot{\Delta}_q$
Now suppose $\dot{\Delta}_q \omega = \mathcal{F}^{-1}\big(\hat{\psi}(2^{-q}k/k_0)\hat{\omega}(k)\big)$ is a standard smooth partition of unity with $\hat{\psi}_q(k) \in [0, 1]$, $\operatorname{supp}\hat{\psi}_q \subset \big[\frac{3}{4}k_0 2^q, \frac{8}{3}k_0 2^q\big]$, and $\sum_{q=0}^\infty \hat{\psi}_q(k) \equiv 1$ for $|k| \ge k_0$.
Because at most two adjacent smooth shells $\hat{\psi}_q(k)$ and $\hat{\psi}_{q+1}(k)$ overlap at any wavevector $k$ with $\hat{\psi}_q(k) + \hat{\psi}_{q+1}(k) = 1$, the sum of squares satisfies:
$$\frac{1}{2} = \min_{a \in [0,1]} \big(a^2 + (1-a)^2\big) \le \sum_{q=0}^\infty \hat{\psi}_q(k)^2 \le 1,$$
with strict inequality $\sum_{q=0}^\infty \hat{\psi}_q(k)^2 < 1$ on every overlap zone where $\hat{\psi}_q(k) \in (0,1)$!
Consequently, for smooth Littlewood–Paley blocks $\dot{\Delta}_q \omega$:
1. **Non-Equality of Summed Shell Norms**:
   $$\frac{1}{2}\,D(t) \le \sum_{q=0}^\infty \nu \|\nabla \dot{\Delta}_q \omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \le D(t) \qquad (\text{EQUIVALENCE UP TO CONSTANTS } [1/2, 1],\text{ NOT EQUALITY!}).$$
2. **How to Restore Exactness for Smooth $\dot{\Delta}_q$**:
   Either:
   - Use the **linear partition-of-unity pairing** $\widetilde{D}_q^\omega(t) := \nu \langle \nabla \dot{\Delta}_q \omega, \nabla \omega \rangle_{L^2(\mathbb{T}^3_L)} = \nu L^3 \sum_{k \ne 0} \hat{\psi}_q(k)|k|^2|\hat{\omega}(k)|^2 \ge 0$, which satisfies **exact summation** $\sum_{q=0}^\infty \widetilde{D}_q^\omega(t) = D(t)$; OR
   - For squared blocks $\|\nabla \dot{\Delta}_q \omega\|_{L^2}^2$, choose the lowered threshold $\widetilde{Q}_*(t) := \max\big(0, \lfloor \frac{1}{2}\log_2(\frac{9}{64\,\lambda_{\rm P}\,\bar{\ell}_\omega(t)^2})\rfloor\big)$ so that $\frac{8}{3}k_0 2^{\widetilde{Q}_*-1} \le \frac{1}{2\sqrt{2}\bar{\ell}_\omega(t)}$, giving $\sum_{q < \widetilde{Q}_*} \nu\|\nabla \dot{\Delta}_q \omega\|_{L^2}^2 \le \frac{1}{8}D(t)$ and therefore:
     $$\boxed{\sum_{q \ge \widetilde{Q}_*(t)} \nu \|\nabla \dot{\Delta}_q \omega(t)\|_{L^2(\mathbb{T}^3_L)}^2 \ge \frac{1}{2}D(t) - \frac{1}{8}D(t) = \frac{3}{8}\,D(t)}.$$

### 1.3 Audit of Time-Differentiation Across Integer Steps of $Q_*(t)$
In `CLM-041` Part (3), writing $\frac{d}{dt}\sum_{q \ge Q_*(t)} E_q^\omega(t)$ treated $Q_*(t)$ as constant in time. Since $Q_*(t) \in \mathbb{N}_0$ is a piecewise-constant step function of $\bar{\ell}_\omega(t)$, the derivative $\frac{d}{dt}\sum_{q \ge Q_0} E_q^\omega(t)$ is valid **only for a fixed reference integer shell $Q_0 := Q_*(t_0)$ frozen at the evaluation instant $t = t_0$**:
$$\left.\frac{d}{dt}\sum_{q \ge Q_0} E_q^\omega(t)\right|_{t=t_0} + \sum_{q \ge Q_0} D_q^\omega(t_0) = \sum_{q \ge Q_0} \big(T_q^{\text{adv}}(t_0) + P_q^{\text{stretch}}(t_0)\big).$$
This frozen-shell formulation eliminates step-function jump artifacts completely.

---

## 2. Exact Dyadic Vorticity and Enstrophy Balance with Explicit Commutators and Cross-Terms (Section 9)

Starting from the exact vorticity PDE on $\mathbb{T}^3_L$:
$$\partial_t \omega + (u \cdot \nabla)\omega = S\omega + \nu \Delta\omega, \qquad \operatorname{div} u = \operatorname{div}\omega = 0,$$
apply a dyadic projection operator $\Delta_q$ (either orthogonal $P_q$ or smooth $\dot{\Delta}_q$, with low-frequency partial sum $S_{q-1} := \sum_{p=0}^{q-1} \Delta_p$ and $\omega_q := \Delta_q \omega$).

Using Bony's paraproduct decomposition on $\mathbb{T}^3_L$, any bilinear product $\Delta_q(A \cdot B)$ expands explicitly into **three distinct interscale mechanisms**:
$$\Delta_q(A \cdot B) = \underbrace{\Delta_q(S_{q-1}A \cdot \Delta_q B) + \dots}_{\text{Low-High Transport + Commutator}} + \underbrace{\Delta_q(\Delta_q A \cdot S_{q-1}B)}_{\text{High-Low Interaction}} + \underbrace{\sum_{|p - r| \le 2,\, \max(p,r) \ge q-1} \Delta_q(\Delta_p A \cdot \Delta_r B)}_{\text{Resonant High-High Triad Cascade}}.$$

Specifically, for the advective term $\Delta_q(u \cdot \nabla\omega)$ and the stretching term $\Delta_q(S\omega)$, we have the **Exact Unabbreviated Dyadic Vorticity Equation** (`EXACT_IDENTITY`):

$$\boxed{\begin{aligned}
\partial_t \omega_q + (S_{q-1}u \cdot \nabla)\omega_q - \nu \Delta\omega_q
&= -\underbrace{[\Delta_q,\, S_{q-1}u \cdot \nabla]\omega}_{\mathcal{C}_q^{\text{adv}} \text{ (advective commutator)}}
- \underbrace{\Delta_q\big((I - S_{q-1})u \cdot \nabla S_{q+1}\omega\big)}_{\mathcal{T}_q^{\text{HL,adv}} \text{ (local/high-low advection)}}
- \underbrace{\sum_{\substack{p \ge q-1,\, r \ge q+2 \\ |p-r| \le 2}} \Delta_q(u_p \cdot \nabla\omega_r)}_{\mathcal{R}_q^{\text{HH,adv}} \text{ (inverse ultraviolet backscatter)}}\\
&\quad + \underbrace{(S_{q-1}S)\omega_q}_{\mathcal{P}_q^{\text{LH,str}} \text{ (large-scale strain stretching)}}
+ \underbrace{[\Delta_q,\, S_{q-1}S]\omega}_{\mathcal{C}_q^{\text{str}} \text{ (strain commutator)}}
+ \underbrace{\Delta_q\big((I - S_{q-1})S \cdot \omega\big)}_{\mathcal{P}_q^{\text{local+HH,str}} \text{ (scale-local & high-high stretching)}}
\end{aligned}}$$

Taking the $L^2(\mathbb{T}^3_L)$ inner product with $\omega_q$ and using $\int_{\mathbb{T}^3_L} \omega_q \cdot (S_{q-1}u \cdot \nabla)\omega_q\,dx = -\frac{1}{2}\int_{\mathbb{T}^3_L} (\operatorname{div} S_{q-1}u)|\omega_q|^2\,dx = 0$ (exact cancellation of sweeping by large-scale velocity $S_{q-1}u$!), we obtain the **Exact Unsuppressed Shell Enstrophy Balance** (`EXACT_IDENTITY`):

$$\boxed{\frac{1}{2}\frac{d}{dt}\|\omega_q\|_{L^2(\mathbb{T}^3_L)}^2 + \nu \|\nabla\omega_q\|_{L^2(\mathbb{T}^3_L)}^2 = T_q^{\text{adv}}(t) + P_q^{\text{stretch}}(t)}$$

where every constituent term is displayed explicitly:
$$T_q^{\text{adv}}(t) = -\int_{\mathbb{T}^3_L} \omega_q \cdot [\Delta_q,\, S_{q-1}u \cdot \nabla]\omega\,dx - \int_{\mathbb{T}^3_L} \omega_q \cdot \Delta_q\big((I - S_{q-1})u \cdot \nabla S_{q+1}\omega\big)\,dx - \sum_{\substack{p \ge q-1,\, r \ge q+2 \\ |p-r| \le 2}} \int_{\mathbb{T}^3_L} \omega_q \cdot \Delta_q(u_p \cdot \nabla\omega_r)\,dx,$$
$$P_q^{\text{stretch}}(t) = \int_{\mathbb{T}^3_L} \omega_q \cdot (S_{q-1}S)\omega_q\,dx + \int_{\mathbb{T}^3_L} \omega_q \cdot [\Delta_q,\, S_{q-1}S]\omega\,dx + \sum_{p \ge q-1} \sum_{r \ge 0} \int_{\mathbb{T}^3_L} \omega_q \cdot \Delta_q(S_p \omega_r)\,dx.$$

---

## 3. Global Energy-Transfer and Production Reconstruction Consistency (Section 10)

How do $\sum_{q=0}^\infty T_q^{\text{adv}}(t)$ and $\sum_{q=0}^\infty P_q^{\text{stretch}}(t)$ relate to the global integrals $0$ and $P(t) = \int_{\mathbb{T}^3_L} \omega \cdot S\omega\,dx$? The answer depends crucially on whether $\Delta_q$ is orthogonal ($P_q$) or smooth overlapping ($\dot{\Delta}_q$):

### Proposition 3.1 (Exact Reconstruction for Orthogonal $P_q$ vs. Overlap Defect for Smooth $\dot{\Delta}_q$)
1. **Orthogonal Shell Projectors ($\Delta_q = P_q$, where $\sum_{q=0}^\infty P_q^2 = \sum_{q=0}^\infty P_q = I$)**:
   Since $P_q$ is self-adjoint and idempotent ($P_q^* P_q = P_q^2 = P_q$):
   $$\sum_{q=0}^\infty T_q^{\text{adv}}(t) = -\sum_{q=0}^\infty \langle P_q \omega,\, P_q(u \cdot \nabla\omega)\rangle_{L^2} = -\left\langle \Big(\sum_{q=0}^\infty P_q\Big)\omega,\, u \cdot \nabla\omega\right\rangle_{L^2} = -\int_{\mathbb{T}^3_L} \omega \cdot (u \cdot \nabla)\omega\,dx = \mathbf{0} \quad (\text{EXACT ZERO}),$$
   $$\sum_{q=0}^\infty P_q^{\text{stretch}}(t) = \sum_{q=0}^\infty \langle P_q \omega,\, P_q(S\omega)\rangle_{L^2} = \left\langle \Big(\sum_{q=0}^\infty P_q\Big)\omega,\, S\omega\right\rangle_{L^2} = \int_{\mathbb{T}^3_L} \omega \cdot S\omega\,dx = \mathbf{P(t)} \quad (\text{EXACT EQUALITY}).$$
2. **Smooth Overlapping Littlewood–Paley Multipliers ($\Delta_q = \dot{\Delta}_q$, where $\sum_{q=0}^\infty \dot{\Delta}_q = I$ but $\sum_{q=0}^\infty \dot{\Delta}_q^2 = \mathcal{M} \ne I$)**:
   Here $\dot{\Delta}_q^* \dot{\Delta}_q = \dot{\Delta}_q^2$ has Fourier multiplier $m(k) := \sum_{q=0}^\infty \hat{\psi}_q(k)^2 \in [1/2, 1]$. Since $m(k)$ is **not constant** across overlap annuli, the operator $\mathcal{M}\omega := \sum_{q=0}^\infty \dot{\Delta}_q^2 \omega$ does **not** equal $\omega$! Instead, using $\dot{\Delta}_q \dot{\Delta}_r = 0$ for $|q - r| \ge 2$ and $I = \big(\sum_q \dot{\Delta}_q\big)^2 = \sum_q \dot{\Delta}_q^2 + 2\sum_q \dot{\Delta}_q \dot{\Delta}_{q+1}$, we have the **Exact Overlap Defect Identities**:
   $$\boxed{\sum_{q=0}^\infty T_q^{\text{adv}}[\dot{\Delta}_q](t) = 2\sum_{q=0}^\infty \langle \dot{\Delta}_q \omega,\, \dot{\Delta}_{q+1}(u \cdot \nabla\omega)\rangle_{L^2} \ne 0 \quad (\text{non-zero adjacent-shell overlap residual!})}$$
   $$\boxed{\sum_{q=0}^\infty P_q^{\text{stretch}}[\dot{\Delta}_q](t) = P(t) - 2\sum_{q=0}^\infty \langle \dot{\Delta}_q \omega,\, \dot{\Delta}_{q+1}(S\omega)\rangle_{L^2} \ne P(t)}$$
   Whereas if one defines the **linear dual-paired shell quantities** $\widetilde{E}_q^\omega := \frac{1}{2}\langle \dot{\Delta}_q \omega, \omega \rangle_{L^2}$, $\widetilde{T}_q^{\text{adv}} := -\langle \dot{\Delta}_q \omega, u\cdot\nabla\omega \rangle_{L^2}$, and $\widetilde{P}_q^{\text{stretch}} := \langle \dot{\Delta}_q \omega, S\omega \rangle_{L^2}$, then $\sum_{q=0}^\infty \widetilde{T}_q^{\text{adv}} = 0$ and $\sum_{q=0}^\infty \widetilde{P}_q^{\text{stretch}} = P(t)$ hold with **exact equality**!

---

## 4. Blueprint for Next Genuine Dynamical Theorem Target (`SELF-FOCUS-002`, Section 23)

In accordance with Section 22 and Section 23, we do **not** open `SELF-FOCUS-002` during this R1 repair, and we record that the next theorem target must **not** be an algebraic ratio identity. Instead, the target for `SELF-FOCUS-002` is locked as the **Dynamical Inter-Shell Enstrophy Flux Lower Bound**:
- Given a multi-shell initial state on $\mathbb{T}^3_L$ with active transition shell $Q_0 = Q_*(t_0)$ and positive net stretching $P(t_0) > D(t_0)$, quantify the forward commutator-plus-paraproduct transfer rate:
  $$\Phi_{Q_0}^{\text{forward}}(t) := -\sum_{q \ge Q_0} \langle P_q \omega,\, [P_q, S_{q-1}u \cdot \nabla]\omega \rangle_{L^2} + \sum_{q \ge Q_0} \langle P_q \omega,\, P_q(S\omega) \rangle_{L^2}$$
  incorporating the nonlocal Riesz transform representation $S[\omega] = \mathcal{R}_{\text{BS}}\omega$ and the pressure-strain operator $\Xi[\omega_q]$, or prove a rigorous viscous/commutator obstruction showing that $\Phi_{Q_0}^{\text{forward}}(t) - \sum_{q \ge Q_0} \nu\|\nabla P_q \omega\|_{L^2}^2$ saturates before $Q_*(t) \to \infty$.
