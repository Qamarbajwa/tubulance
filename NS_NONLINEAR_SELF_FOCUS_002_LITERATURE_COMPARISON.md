# NS-NONLINEAR-SELF-FOCUS-002: Primary-Source Literature Comparison with Cheskidov–Shvydkoy and Constantin–Fefferman

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Direct Comparison with the Cheskidov–Shvydkoy Dissipation-Wavenumber Programme (Section 17)

### 1.1 Primary-Source Statement of Cheskidov–Shvydkoy (2010, 2014) (`KNOWN_THEOREM`)
In Cheskidov & Shvydkoy (*Arch. Ration. Mech. Anal.* **195**, 159–181, 2010; *Comm. Pure Appl. Math.* **67**, 621–646, 2014), the 3D Navier–Stokes velocity/vorticity field is decomposed into dyadic Littlewood–Paley blocks $u_q = \Delta_q u$, $\omega_q = \Delta_q \omega$ ($\lambda_q = 2^q$). They define the **time-dependent dissipation wavenumber** $\Lambda(t) = \lambda_{q_d(t)}$ by comparing the inviscid local straining rate $2^q \|u_q\|_{L^\infty} \asymp \|\omega_q\|_{L^\infty}$ (or $2^{-q}\|\omega_q\|_{L^\infty}$) against the kinematic viscosity $\nu$:
$$\Lambda_{\rm CS}(t) := \min\left\{ \lambda_q = 2^q : \,\, \lambda_p^{-1} \|u_p(t)\|_{L^\infty} \le c_0 \nu \quad \forall p \ge q \right\}.$$
Using Bony's paraproduct decomposition ($T_u v + T_v u + R(u,v)$) and commutator estimates, Cheskidov and Shvydkoy bound the dyadic energy/enstrophy flux $\Pi_Q(t)$ **from above in absolute value**:
$$|\Pi_Q(t)| \le C \sum_{p \le Q} \lambda_p \|u_p\|_{L^\infty} \sum_{q > Q} \lambda_{p-q}^{\delta} \|\omega_q\|_{L^2}^2 + C \sum_{q > Q} \lambda_q \|u_q\|_{L^\infty} \|\omega_q\|_{L^2}^2.$$
When $Q \ge q_d(t)$ ($\lambda_Q \ge \Lambda_{\rm CS}(t)$), the high-frequency tail is absorbed by $\frac{1}{2}\nu \sum_{q > Q} \lambda_q^2 \|\omega_q\|_{L^2}^2 = \frac{1}{2}D_{>Q}(t)$, yielding their landmark regularity criteria:
$$\int_0^T \|P_{\le \Lambda_{\rm CS}(t)} \omega(t)\|_{B^0_{\infty,\infty}}\,dt < \infty \implies u \in C^\infty((0,T] \times \mathbb{T}^3).$$

### 1.2 Direct Answer to the Controlling Comparison Question (Section 17)
$$\boxed{\text{How is our proposed transfer mechanism mathematically different from an existing dissipation-wavenumber regularity criterion?}}$$

We classify the relationship into **three exact mathematical axes**:

| Comparison Axis | Cheskidov–Shvydkoy (2010, 2014) Dissipation-Wavenumber Theory | `NS-NONLINEAR-SELF-FOCUS-002` (`CLM-042` & Operator Split) | Overlap / Novelty Classification |
| :--- | :--- | :--- | :--- |
| **1. Commutator & Bony Triad Structure** | Uses $\Pi_Q = -\langle [P_{\le Q}, u\cdot\nabla]u, P_{\le Q}u\rangle$ (or vorticity analogue) and splits triads into local/nonlocal Bony paraproducts. | Uses exact sharp orthogonal projector commutator $\mathcal{T}_q = -\langle [P_q, u\cdot\nabla]\omega, \omega_q\rangle$ and skew-adjoint $\mathcal{T}_q$ vs. self-adjoint $\mathcal{S}_q$ split. | **`KNOWN` / `PROJECT_REFORMULATION`** (`N0`/`N1`): No novelty claimed for the commutator identity or viscous cutoff scale $\nu 2^{2Q}$. |
| **2. Direction of Inequality (Upper Bound vs. Signed Forward Lower Bound)** | Proves an **unsigned upper bound** $|\Pi_Q(t)| \le \Phi_{\rm CS}(\{\|u_p\|_{L^\infty}, \|\omega_p\|_{L^2}\})$ to show viscosity dominates for $2^Q \ge \Lambda_{\rm CS}(t)$. Because it uses only shell norms $\|u_p\|_{L^\infty}, \|\omega_p\|_{L^2}$, it evaluates to the **same positive upper bound** on a Beltrami/ABC flow and a Taylor–Green flow with identical shell norms. | Proves a **signed forward-in-time lower bound** on $\int_{t_0}^{t_1} \Pi_Q^{\rm nonlin}(t)\,dt$ and $E_{>Q}(t_1)$ driven by $\|P_{Q+1}\nabla\times(u_0\times\omega_0)\|_{L^2}^2$ via Duhamel's Stokes resolvent. This bound is **identically zero** on Beltrami/ABC flows ($u_0 \times \omega_0 = 0$) and **strictly positive** on Taylor–Green / opposite-helicity triads with the exact same shell norms and $\Lambda_{\rm CS}(t_0)$. | **`CONDITIONAL_NEW_LEMMA`** (`CLM-042`): Complementary direction of inequality (forward lower bound via Duhamel shell-step vs. regularity upper bound). |
| **3. Cutoff Selection Rule** | $\Lambda_{\rm CS}(t)$ is a **time-dependent state-selected cutoff** defined at each instant $t$ by the level set $\lambda_p^{-1}\|u_p(t)\|_{L^\infty} = c_0\nu$. | $Q = Q_0$ in `CLM-042` is fixed **a priori at $t = t_0$ from the initial data $\omega_0$** (independent of future dissipation $D(t)$), avoiding the tautological selection criticized in `R1`. | **Distinct mathematical object** (fixed initial-data shell step vs. moving viscous threshold). |

**Honest Verdict on Overlap**:
Any attempt to define a time-dependent cutoff $Q_{\rm visc}(t)$ by setting $\mathfrak{G}_Q(t) \approx 1$ or $\mathfrak{F}_Q^{\rm tot}(t) \approx 1$ is a **`KNOWN_DISSIPATION_WAVENUMBER_REFORMULATION`** (`N1_PROJECT_REFORMULATION`) of Cheskidov–Shvydkoy's $\Lambda_{\rm CS}(t)$. Therefore, we **do not** register a moving cutoff $Q_{\rm visc}(t)$ as a novel regularity criterion; we restrict our new claim `CLM-042` exclusively to the **forward-in-time Duhamel lower bound across an initial-data-fixed cutoff $Q_0$**.

---

## 2. Direct Comparison with the Constantin–Fefferman Vorticity-Direction Coherence Theory (Section 18)

### 2.1 Exact Statement of the Constantin–Fefferman (1993) and Beirão da Veiga–Berselli (2002) Theorems (`KNOWN_THEOREM`)
Let $\xi(x,t) := \frac{\omega(x,t)}{|\omega(x,t)|} \in \mathbb{S}^2$ be the unit vorticity direction on the non-vanishing set $\Omega_+(t) = \{x \in \mathbb{T}_L^3 : |\omega(x,t)| > 0\}$, and for a threshold $\Omega > 0$ define the high-vorticity superlevel set:
$$\Omega_{>\Omega}(t) := \left\{ x \in \mathbb{T}_L^3 : |\omega(x,t)| > \Omega \right\}.$$
By Constantin (1994), the local stretching rate $\alpha_\omega(x,t) := \frac{\omega(x,t)\cdot S(x,t)\omega(x,t)}{|\omega(x,t)|^2} = \xi_i(x,t) S_{ij}[\omega](x,t)\xi_j(x,t)$ admits the exact singular-integral representation:
$$\alpha_\omega(x,t) = \frac{3}{4\pi} \operatorname{P.V.} \int_{\mathbb{R}^3} D(\widehat{y}, \xi(x+y,t), \xi(x,t)) \, |\omega(x+y,t)| \, \frac{dy}{|y|^3},$$
where the geometric kernel $D(\widehat{y}, \xi_1, \xi_2) := (\widehat{y} \cdot \xi_1)(\widehat{y} \times \xi_1) \cdot \xi_2$ satisfies the exact pointwise depletion bound:
$$\boxed{|D(\widehat{y}, \xi(x+y,t), \xi(x,t))| \le |\xi(x+y,t) \times \xi(x,t)| = |\sin \theta(x+y, x, t)|.}$$
- **Constantin–Fefferman Theorem (1993)** ($\alpha = 1$) & **Beirão da Veiga–Berselli Improvement (2002)** ($\alpha = 1/2$):
  If there exist $\Omega > 0$, $r_0 > 0$, $\rho > 0$, and $\alpha \in [1/2, 1]$ such that for almost every $t \in [0, T]$ and all $x, y \in \Omega_{>\Omega}(t)$ with $|x - y| \le r_0$,
  $$\boxed{|\xi(x,t) \times \xi(y,t)| \le \frac{|x - y|^\alpha}{\rho},}$$
  then the solution $u$ remains smooth on $[0, T]$ ($\sup_{t \in [0,T]} \|\omega(t)\|_{L^2} < \infty$ and $\sup_{t \in [0,T]} \|\omega(t)\|_{L^\infty} < \infty$).

### 2.2 Rigorous Compatibility and Violation Analysis (Section 18)
1. **No Naive Assertion "$\text{Blowup Requires } |\nabla \xi| \to \infty$"**:
   Consistent with Section 18 and `NS-OBS-021-R1`, we **do not** write "blowup requires $|\nabla\xi| \to \infty$". The Constantin–Fefferman / Beirão da Veiga–Berselli theorem requires only $\frac{1}{2}$-Hölder coherence of $\xi$ **restricted to pairs of points $x, y$ that simultaneously belong to the high-vorticity set $\Omega_{>\Omega}(t)$** within distance $r_0$. Rapid variation of $\xi$ in low-vorticity regions $\{|\omega| \le \Omega\}$ (including vorticity nulls where $\xi$ is discontinuous) has no impact on regularity.
2. **Does Single-Step Forward Transfer (`CLM-042`) Violate Constantin–Fefferman Coherence?**
   - **On a finite time interval $[t_0, t_1]$ (Single-Step Transfer $Q_0 \to Q_0 + 1$): NO.**
     Any smooth non-Beltrami initial datum $\omega_0 \in C^\infty(\mathbb{T}_L^3)$ (such as the Taylor–Green vortex or an opposite-helicity triad with $\|P_{Q_0+1}\nabla\times(u_0\times\omega_0)\|_{L^2} > 0$) has bounded vorticity $\sup_{[t_0,t_1]\times\mathbb{T}_L^3}|\omega(x,t)| = M_\infty < \infty$. Choosing $\Omega > M_\infty$ makes $\Omega_{>\Omega}(t) = \emptyset$, so Constantin–Fefferman coherence holds vacuously while `CLM-042` still produces strictly positive forward enstrophy transfer $E_{>Q_0}(t_1) > 0$.
   - **In a Hypothetical Asymptotic Cascade ($Q \to \infty$ with $\sup_t \|\omega(t)\|_{L^\infty} = \infty$): YES.**
     Suppose a flow were to sustain $P_{>Q}^{\rm stretch}(t) = \int_{\mathbb{T}_L^3} S[\omega]\omega \cdot \omega_{>Q}\,dx > D_{>Q}(t)$ across arbitrarily high shells $Q \to \infty$ as $t \uparrow T_*$. By the Beirão da Veiga–Berselli theorem, if $|\xi(x,t) \times \xi(y,t)| \le \rho^{-1}|x-y|^{1/2}$ held uniformly on $\Omega_{>\Omega}(t)$ for some fixed $\rho > 0, \Omega > 0$, then $|P(t)| \le C(\Omega, \rho)\|\omega(t)\|_{L^2}^2 + \frac{1}{2}D(t)$, which bounds $\|\omega(t)\|_{L^2}^2$ uniformly on $[0, T_*]$ and forces $D_{>Q}(t)$ to dominate $P_{>Q}^{\rm stretch}(t)$ for all sufficiently large $Q$. Therefore, **any sustained asymptotic regime where $\mathfrak{F}_Q^{\rm tot}(t) \ge 1$ as $Q \to \infty$ with $\|\omega(t)\|_{L^2} \to \infty$ must necessarily violate the $\frac{1}{2}$-Hölder direction coherence $|\xi(x,t)\times\xi(y,t)| \le \rho^{-1}|x-y|^{1/2}$ on $\Omega_{>\Omega}(t)$ at scales $|x - y| \lesssim 2^{-Q}$**.
   - However, as proven in `NS_NONLINEAR_SELF_FOCUS_001_R1_GEOMETRIC_DEPLETION_AUDIT.md`, violating $\frac{1}{2}$-Hölder coherence of $\xi$ on $\Omega_{>\Omega}(t)$ increases the directional palinstrophy term $\nu \int_{\Omega_+(t)} |\omega(x,t)|^2 |\nabla \xi(x,t)|^2\,dx \le D(t)$, creating the unresolved two-way competition (`NS-OBS-021-R1`: `HEURISTIC_TENSION`).
