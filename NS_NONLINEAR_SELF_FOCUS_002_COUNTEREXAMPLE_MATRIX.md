# NS-NONLINEAR-SELF-FOCUS-002: Adversarial Counterexample Matrix for Dyadic Flux and Competition Diagnostics

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Purpose (Section 20)

Section 20 mandates testing the proposed forward flux and viscous competition quantities ($\Pi_Q^{\rm adv}$, $\Pi_Q^{\omega,\rm tot}$, $\mathfrak{F}_Q^{\rm tot}$, and $\mathfrak{G}_Q$) against **nine exact test flows**:
1. 2D embedded flow in $\mathbb{T}^3$;
2. Parallel shear flow;
3. Beltrami / Arnold–Beltrami–Childress (ABC) flow;
4. Taylor–Green vortex;
5. Single Fourier mode;
6. Two-mode interaction (same-helicity resonant vs. opposite-helicity non-Beltrami);
7. One exact resonant triad ($|k| = |\ell|, s_k = s_\ell$);
8. One nonresonant / opposite-helicity triad ($k + \ell = m \in \mathcal{C}_{Q+1}, s_k |k| \ne s_\ell |\ell|$);
9. Localized vortex tube (axisymmetric parallel vortex column vs. 3D perturbed tube).

A valid 3D forward focusing diagnostic **must not** diagnose a forward singular 3D vortex-stretching cascade on known globally benign flows merely because high gradients or large instantaneous enstrophy exist.

---

## 2. Complete Nine-Flow Adversarial Counterexample Matrix

| # | Test Flow on $\mathbb{T}_{2\pi}^3$ | Exact Velocity / Vorticity Structure | Stretching $P_Q^{\rm cross}$ & $P_{>Q}^{\rm intra}$ | Advective Flux $\Pi_Q^{\rm adv}(t)$ | Total Flux $\Pi_Q^{\omega,\rm tot}(t)$ | Duhamel Ratio $\mathfrak{G}_Q(t_0)$ | Verdict / Diagnostic Filter |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **2D Embedded Flow in $\mathbb{T}^3$** | $u = (u_1(x_1,x_2,t), u_2(x_1,x_2,t), 0)$, $\omega = (0, 0, \omega_3(x_1,x_2,t))$ | $(\omega\cdot\nabla)u \equiv 0 \implies$ **$P_Q^{\rm cross} \equiv 0$**, **$P_{>Q}^{\rm intra} \equiv 0$** ($\forall Q$) | Can be $> 0$ (2D direct enstrophy cascade, Kraichnan 1967), bounded by $\frac{d}{dt}\|\omega\|_{L^2}^2 = -2\nu\|\nabla\omega\|_{L^2}^2 \le 0$ | Equals $\Pi_Q^{\rm adv}(t)$ with **zero stretching** ($\mathcal{S}_q \equiv 0 \,\, \forall q$) | Non-zero only in 2D advection; **3D stretching component $\mathcal{S}_{Q+1} \equiv 0$** | **PASS**: Joint requirement $(\Pi_Q^{\omega,\rm tot} > 0 \text{ AND } \mathcal{S}_{>Q} > 0)$ filters all 2D flows since $\mathcal{S}_q \equiv 0 \,\, \forall q$. |
| **2** | **Parallel Shear Flow** | $u = (U(x_2,t), 0, 0)$, $\omega = (0, 0, -\partial_2 U(x_2,t))$ | $(\omega\cdot\nabla)u \equiv 0 \implies$ **$P_Q^{\rm cross} \equiv 0$**, **$P_{>Q}^{\rm intra} \equiv 0$** | $(u\cdot\nabla)\omega = U(x_2)\partial_1\omega \equiv 0 \implies$ **$\Pi_Q^{\rm adv}(t) \equiv 0$** | **$\Pi_Q^{\omega,\rm tot}(t) \equiv 0$** | **$\mathfrak{G}_Q(t_0) \equiv 0$** | **PASS**: All nonlinear transfer and competition diagnostics vanish identically even when $\|\nabla\omega\|_{L^2} \gg 1$. |
| **3** | **Beltrami / ABC Flow** | $\omega = \lambda u$ ($\lambda = |k| \in \mathcal{C}_Q$), $u \times \omega \equiv 0$ pointwise | $(u\cdot\nabla)\omega = (\omega\cdot\nabla)u = \lambda\nabla(|u|^2/2) \perp \omega_q \implies$ **$\mathcal{S}_q \equiv 0$** | **$\Pi_Q^{\rm adv}(t) \equiv 0$** ($\forall Q, t$) | **$\Pi_Q^{\omega,\rm tot}(t) \equiv 0$** ($\forall Q, t$) | **$\mathfrak{G}_Q(t_0) \equiv 0$** | **PASS**: Exact annihilation ($0$ to machine precision) despite 3D streamline chaos and pointwise $\omega\cdot S\omega \ne 0$. |
| **4** | **Taylor–Green Vortex** | $u_0 = (\sin x \cos y \cos z, -\cos x \sin y \cos z, 0)$, $\|k\| = \sqrt{3} \in \mathcal{C}_0$ | At $t_0=0$, $P(0) = 0$; for $t \in (0, \Delta t]$, $\mathcal{S}_1(t) > 0$ | $\Pi_0^{\rm adv}(0) = 0$, $\dot{\Pi}_0^{\rm adv}(0) > 0 \implies$ **$\Pi_0^{\rm adv}(t) > 0$** on $(0, \Delta t]$ | $\dot{\Pi}_0^{\omega,\rm tot}(0) = \|F_1(0)\|_{L^2}^2 > 0 \implies$ **$\Pi_0^{\omega,\rm tot}(t) > 0$** | **$\mathfrak{G}_0(0) > 0$** (drives shell $Q=0 \to Q+1=1$) | **PASS**: Correctly detects genuine 3D forward enstrophy transfer & stretching starting from $P(0)=0$. |
| **5** | **Single Fourier Mode** | $u(x,t) = e^{-\nu |k|^2 t}(a e^{ik\cdot x} + \bar{a}e^{-ik\cdot x})$ ($k \cdot a = 0$) | $(u\cdot\nabla)u = 0, (\omega\cdot\nabla)u = 0 \implies$ **$\mathcal{S}_q \equiv 0$** | **$\Pi_Q^{\rm adv}(t) \equiv 0$** | **$\Pi_Q^{\omega,\rm tot}(t) \equiv 0$** | **$\mathfrak{G}_Q(t_0) \equiv 0$** | **PASS**: Self-interaction of any single divergence-free mode is identically zero. |
| **6** | **Two-Mode Interaction** | $u_0 = u_k + u_\ell$ with $k, \ell \in \mathcal{C}_Q$ and $k + \ell = m \in \mathcal{C}_{Q+1}$ | Zero if $s_k |k| = s_\ell |\ell|$; non-zero into $\mathcal{C}_{Q+1}$ if $s_k |k| \ne s_\ell |\ell|$ | Zero at $t_0=0$; positive on $(0,\Delta t]$ iff $s_k |k| \ne s_\ell |\ell|$ | $\left.\frac{d}{dt}\Pi_Q^{\omega,\rm tot}\right|_{t_0} = \|F_{Q+1}(t_0)\|_{L^2}^2 > 0$ iff $s_k |k| \ne s_\ell |\ell|$ | **$\mathfrak{G}_Q(t_0) > 0$** iff $s_k |k| \ne s_\ell |\ell|$ | **PASS**: Distinguishes non-interacting Beltrami pairs ($s_k|k|=s_\ell|\ell|$) from active triadic transfer pairs. |
| **7** | **Exact Resonant Triad (Beltrami Sphere)** | $k + \ell = m$ with $|k| = |\ell| = \lambda \in \mathcal{C}_Q$ and $s_k = s_\ell = +1$ | $s_k |k| - s_\ell |\ell| = \lambda - \lambda = 0 \implies \Gamma_m = 0 \implies$ **$\mathcal{S}_m \equiv 0$** | **$\Pi_Q^{\rm adv}(t) \equiv 0$** (if $\omega_m(t_0) = 0$) | **$\Pi_Q^{\omega,\rm tot}(t) \equiv 0$** | **$\mathfrak{G}_Q(t_0) \equiv 0$** | **PASS**: Same-helicity resonant modes on a sphere form a Beltrami state and produce zero forward transfer. |
| **8** | **Nonresonant / Opposite-Helicity Triad** | $k + \ell = m \in \mathcal{C}_{Q+1}$ with $k, \ell \in \mathcal{C}_Q$, $s_k = +1, s_\ell = -1$ | $\Gamma_m = |m|^2(|k| + |\ell|) > 0$; $\mathcal{S}_m(t) > 0$ on $[t_0, t_0 + \Delta t]$ | $\Pi_Q^{\rm adv}(t) > 0$ for favorable triad phase $C_{k\ell m}(t) > 0$ | $\Pi_Q^{\omega,\rm tot}(t) = |m|^2(|k|+|\ell|)C_{k\ell m}(t) > 0$ | **$\mathfrak{G}_Q(t_0) > 0$** | **PASS**: Captures microscopic forward transfer while showing phase reversal at $t = t_0 + T_{\rm half}$. |
| **9** | **Localized Vortex Tube** | Straight axisymmetric column $\omega = f(r)e_z$ vs. 3D sinusoidally perturbed tube | Straight column: $(\omega\cdot\nabla)u = 0, (u\cdot\nabla)\omega = 0 \implies$ **zero flux**; 3D perturbed tube: $\Pi_Q^{\omega,\rm tot} > 0$ | Straight column: **$\Pi_Q^{\rm adv} \equiv 0$**; 3D perturbed tube: $\Pi_Q^{\rm adv} \ne 0$ | Straight column: **$\Pi_Q^{\omega,\rm tot} \equiv 0$**; 3D perturbed tube: $\Pi_Q^{\omega,\rm tot} > 0$ | Straight column: **$\mathfrak{G}_Q \equiv 0$**; 3D perturbed: $\mathfrak{G}_Q > 0$ | **PASS**: Does not trigger on a 1D/axisymmetric high-gradient vortex core ($r \ll 1$) unless genuine 3D axial perturbation exists. |

---

## 3. Structural Lesson from the Counterexample Matrix (`PROVED_LEMMA` / `NEGATIVE_EVIDENCE`)

1. **Why Pointwise Gradient/Strain Diagnostics Failed in `SELF-FOCUS-001`, and Why $\Pi_Q^{\omega,\rm tot}$ & $\mathfrak{G}_Q$ Succeed**:
   In `SELF-FOCUS-001`, pointwise unsubtracted stretching $\lambda_\omega(x,t) = \frac{\omega \cdot S \omega}{|\omega|^2}$ was positive on ABC flows (`NEG-EV-047`) because $\omega \cdot S \omega = \frac{1}{2}(u \cdot \nabla)|\omega|^2 \ne 0$ locally. By contrast, $\Pi_Q^{\rm adv}(t)$, $\Pi_Q^{\omega,\rm tot}(t)$, and $\mathfrak{G}_Q(t)$ project onto divergence-free Fourier shells $\omega_q$, where every gradient $\nabla(|u|^2/2)$ is **identically orthogonal to $\omega_q$**. Thus all single-eigenvalue Beltrami/ABC flows, parallel shears, single Fourier modes, and unperturbed vortex columns produce **identically zero** flux ($\Pi_Q^{\rm adv} = \Pi_Q^{\omega,\rm tot} = \mathfrak{G}_Q = 0$).
2. **Why 2D Embedded Flows Require the Stretching Split ($\mathcal{T}_q$ vs. $\mathcal{S}_q$)**:
   In a 2D embedded flow $u = (u_1(x_1,x_2), u_2(x_1,x_2), 0)$, $(\omega \cdot \nabla)u \equiv 0$ so $\mathcal{S}_q \equiv 0$ for all $q$, whereas advective transport $\Pi_Q^{\rm adv}(t) = -\langle (u \cdot \nabla)\omega_{\le Q}, \omega_{>Q}\rangle$ can be positive (the classical 2D Kraichnan enstrophy cascade, under which total enstrophy still decays monotonically: $\frac{1}{2}\frac{d}{dt}\|\omega\|_{L^2}^2 = -D(t) \le 0$). Separating $\Pi_Q^{\rm adv}$ (conservative redistribution, $\sum_q \mathcal{T}_q = 0$) from $P_{\le Q}^{\rm stretch}, P_{>Q}^{\rm stretch}$ (3D vortex stretching, $\sum_q \mathcal{S}_q = P(t)$) completely distinguishes benign 2D enstrophy rearrangement ($\mathcal{S}_q \equiv 0$) from 3D stretching-assisted scale transfer ($\mathcal{S}_{>Q} > 0$).
