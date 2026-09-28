# NS-NONLINEAR-SELF-FOCUS-002: Forward-Transfer Hypotheses, Viscous Competition Ratios, and Parabolic Scaling Audit

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Explicit Forward-Transfer Conditions (Section 11)

Recall from `NS_NONLINEAR_SELF_FOCUS_002_EXACT_DYADIC_FLUX.md` that for any cutoff shell $Q \in \mathbb{N}_0$, the high-frequency enstrophy $E_{>Q}(t) = \frac{1}{2}\|P_{>Q}\omega(t)\|_{L^2}^2$ obeys:
$$\frac{d}{dt} E_{>Q}(t) + D_{>Q}(t) = \Pi_Q^{\rm adv}(t) + P_Q^{\rm cross}(t) + P_{>Q}^{\rm intra}(t) = \Pi_Q^{\omega,\rm tot}(t) + P_{>Q}^{\rm intra}(t),$$
where:
- $\Pi_Q^{\rm adv}(t) = -\langle (u \cdot \nabla)\omega_{\le Q}, \omega_{>Q} \rangle = \langle [P_{\le Q}, u \cdot \nabla]\omega, \omega_{\le Q} \rangle$ is the conservative advective enstrophy flux across $2^Q$,
- $\Pi_Q^{\omega,\rm tot}(t) = \langle \nabla \times (u \times \omega_{\le Q}), \omega_{>Q} \rangle$ is the total cross-cutoff nonlinear enstrophy input from low modes $\le Q$ into high modes $> Q$.

We distinguish two explicit, falsifiable sufficient regimes for positive forward scale transfer over $[t_0, t_1]$:

### Regime H1 (First-Order Active Cross-Cutoff Phase Alignment — $\omega_{>Q}(t_0) \ne 0$)
At $t = t_0$, both $\omega_{\le Q}(t_0) \ne 0$ and $\omega_{>Q}(t_0) \ne 0$ are active, and the triadic phases satisfy the alignment condition:
$$\Pi_Q^{\rm adv}(t_0) = -\langle (u(t_0) \cdot \nabla)\omega_{\le Q}(t_0), \omega_{>Q}(t_0) \rangle > 0 \qquad \big(\text{or } \Pi_Q^{\omega,\rm tot}(t_0) > 0\big).$$
By temporal smoothness of the $H^2(\mathbb{T}_L^3)$ trajectory on $[t_0, t_1]$, $\left|\frac{d}{dt}\Pi_Q^{\rm adv}(t)\right| \le M_Q^{\rm adv}$ implies $\Pi_Q^{\rm adv}(t) \ge \frac{1}{2}\Pi_Q^{\rm adv}(t_0) > 0$ for all $t \in [t_0, t_0 + \Delta t_*]$ with $\Delta t_* = \min\big(t_1 - t_0, \frac{\Pi_Q^{\rm adv}(t_0)}{2 M_Q^{\rm adv}}\big)$.

### Regime H2 (Second-Order Entrance Injection from Band-Limited Data — $\omega_{>Q}(t_0) = 0$)
At $t = t_0$, the vorticity is supported entirely in low shells $\le Q$ ($\omega_{>Q}(t_0) = 0$, so $\Pi_Q^{\rm adv}(t_0) = \Pi_Q^{\omega,\rm tot}(t_0) = 0$), and the initial low-frequency Lamb curl has non-zero projection onto the adjacent dyadic shell $\mathcal{C}_{Q+1}$:
$$F_{Q+1}(t_0) := P_{Q+1}\nabla \times (u_{\le Q}(t_0) \times \omega_{\le Q}(t_0)) \neq 0, \qquad \|F_{Q+1}(t_0)\|_{L^2} > 0.$$
Then at $t = t_0$, $\partial_t \omega_{>Q}(t_0) = F_{Q+1}(t_0)$ and:
$$\left.\frac{d}{dt}\Pi_Q^{\omega,\rm tot}(t)\right|_{t=t_0} = \|F_{Q+1}(t_0)\|_{L^2}^2 > 0, \qquad \left.\frac{d^2}{dt^2} E_{>Q}(t)\right|_{t=t_0} = \|F_{Q+1}(t_0)\|_{L^2}^2 > 0.$$
When the advective component $F_{Q+1}^{\rm adv}(t_0) := -P_{Q+1}((u_{\le Q}(t_0)\cdot\nabla)\omega_{\le Q}(t_0))$ satisfies $\langle F_{Q+1}^{\rm adv}(t_0), F_{Q+1}(t_0) \rangle > 0$, $\Pi_Q^{\rm adv}(t)$ also becomes strictly positive for $t \in (t_0, t_0 + \Delta t]$.

---

## 2. Viscous Competition Ratios and Pathological Edge-Case Audit (Section 12)

Unlike the algebraic ratio $\mathcal{A}(t) = P(t)/D(t)$ from `CLM-041`, Section 12 requires a dimensionless competition quantity constructed from **actual interscale transfer** across $2^Q$ versus viscous dissipation at scales $> Q$.

### 2.1 Candidate Ratios and Edge-Case Audit
We audit three dimensionless candidates:

1. **Active High-Band Advective Competition Ratio ($\mathfrak{F}_Q^{\rm adv}$)**:
   $$\mathfrak{F}_Q^{\rm adv}(t) := \begin{cases} \dfrac{[\Pi_Q^{\rm adv}(t)]_+}{\nu \|\nabla P_{>Q}\omega(t)\|_{L^2}^2} = \dfrac{[\Pi_Q^{\rm adv}(t)]_+}{D_{>Q}(t)}, & \text{if } \|P_{>Q}\omega(t)\|_{L^2} > 0, \\[8pt] 0, & \text{if } \|P_{>Q}\omega(t)\|_{L^2} = 0. \end{cases}$$
2. **Active High-Band Total Cross-Cutoff Competition Ratio ($\mathfrak{F}_Q^{\rm tot}$)**:
   $$\mathfrak{F}_Q^{\rm tot}(t) := \begin{cases} \dfrac{[\Pi_Q^{\omega,\rm tot}(t)]_+}{\nu \|\nabla P_{>Q}\omega(t)\|_{L^2}^2} = \dfrac{[\Pi_Q^{\omega,\rm tot}(t)]_+}{D_{>Q}(t)}, & \text{if } \|P_{>Q}\omega(t)\|_{L^2} > 0, \\[8pt] 0, & \text{if } \|P_{>Q}\omega(t)\|_{L^2} = 0. \end{cases}$$
   - **Audit of Pathological Case for $\mathfrak{F}_Q^{\rm adv}$ and $\mathfrak{F}_Q^{\rm tot}$**:
     Notice that $\Pi_Q^{\rm adv}(t)$ is **linear** in $\omega_{>Q}$ while $D_{>Q}(t) = \nu \|\nabla \omega_{>Q}\|_{L^2}^2$ is **quadratic** in $\omega_{>Q}$. Consequently:
     - If $\|\omega_{>Q}(t)\|_{L^2} = \varepsilon \ll \|\omega_{\le Q}(t)\|_{L^2}$ with favorable phase alignment, $\Pi_Q^{\rm adv}(t) \sim \varepsilon$ while $D_{>Q}(t) \sim \varepsilon^2$, making $\mathfrak{F}_Q^{\rm adv}(t) \sim \varepsilon^{-1} \to +\infty$ as $\varepsilon \to 0^+$ even for an arbitrarily weak flow!
     - Conversely, at the exact entrance instant $\varepsilon = 0$ ($\omega_{>Q}(t_0) = 0$), the unregularized quotient is $0/0$.
     - **Conclusion**: $\mathfrak{F}_Q^{\rm adv}(t) > 1$ (or $\mathfrak{F}_Q^{\rm tot}(t) + \frac{P_{>Q}^{\rm intra}(t)}{D_{>Q}(t)} > 1$) is the **exact necessary and sufficient condition for $\frac{d}{dt} E_{>Q}(t) > 0$ when $E_{>Q}(t) > 0$**, but $\mathfrak{F}_Q \gg 1$ near $E_{>Q} \approx 0$ reflects smallness of existing high-mode enstrophy rather than large nonlinear amplitude.

3. **Well-Posed Duhamel Shell-Step Competition Number ($\mathfrak{G}_Q$ — Pathological-Free Definition)**:
   To eliminate the $\varepsilon^{-1}$ small-denominator blowup and the $0/0$ indeterminacy at $\omega_{>Q}(t_0) = 0$, we normalize the exact shell-step nonlinear injection rate $\|P_{Q+1}\nabla \times (u_{\le Q} \times \omega_{\le Q})\|_{L^2}$ by the viscous damping rate $\mu_{Q+1}\nu = 16 \nu k_0^2 2^{2Q}$ of the target shell $\mathcal{C}_{Q+1}$ and the active low-band vorticity norm $\|P_{\le Q}\omega\|_{L^2}$:
   $$\boxed{\mathfrak{G}_Q(t) := \begin{cases} \dfrac{\|P_{Q+1}\nabla \times (u_{\le Q}(t) \times \omega_{\le Q}(t))\|_{L^2}}{\nu k_0^2 2^{2(Q+1)} \|P_{\le Q}\omega(t)\|_{L^2}}, & \text{if } \|P_{\le Q}\omega(t)\|_{L^2} > 0, \\[8pt] 0, & \text{if } \|P_{\le Q}\omega(t)\|_{L^2} = 0. \end{cases}}$$
   - **Why $\mathfrak{G}_Q(t)$ Survives All Edge-Case Audits**:
     1. **No $0/0$ or $\varepsilon^{-1}$ blowup when $\omega_{>Q} = 0$**: $\mathfrak{G}_Q(t)$ depends only on the occupied band $\le Q$ and is homogeneous of degree $+1$ in the flow amplitude ($\mathfrak{G}_Q[\alpha u] = |\alpha|\mathfrak{G}_Q[u]$), acting as a **genuine scale-local Lamb–Reynolds number across cutoff $2^Q$**.
     2. **Exact vanishing on all benign counterexamples**: Because the numerator is $\|P_{Q+1}\nabla \times (u_{\le Q} \times \omega_{\le Q})\|_{L^2}$, $\mathfrak{G}_Q(t) \equiv 0$ identically on every single Fourier mode, every parallel shear flow, and every Beltrami/ABC flow ($u_{\le Q} \times \omega_{\le Q} = 0$).
     3. **Direct dynamical control of `CLM-042`**: When $\omega_{>Q}(t_0) = 0$, after one viscous time step $\tau_{\rm visc}(Q) = (\nu k_0^2 2^{2(Q+2)})^{-1}$, the fraction of low-band enstrophy transferred into and retained by shell $Q+1$ is directly proportional to $\mathfrak{G}_Q(t_0)^2$:
        $$\frac{E_{>Q}(t_0 + \tau_{\rm visc}(Q))}{E_{\le Q}(t_0)} \ge \frac{1 - e^{-1}}{64} \mathfrak{G}_Q(t_0)^2 - O(\tau_{\rm visc}^4).$$

---

## 3. Exact Parabolic Scaling Audit (Section 13)

Under the natural 3D Navier–Stokes parabolic rescaling:
$$u_\lambda(x,t) := \lambda u(\lambda x, \lambda^2 t), \qquad \omega_\lambda(x,t) = \lambda^2 \omega(\lambda x, \lambda^2 t), \qquad S_\lambda(x,t) = \lambda^2 S(\lambda x, \lambda^2 t)$$
on $\mathbb{T}_{L/\lambda}^3$ (where the rescaled fundamental wavenumber is $k_0(\lambda) = \lambda k_0$ so shell $Q$ maps bijectively to physical wavenumbers $\lambda \mathcal{C}_Q$ and the Spatial Jacobian contributes $dx_\lambda = \lambda^{-3} dx$), every dyadic quantity transforms with an exact power $\lambda^\alpha$ (`EXACT_IDENTITY`):

| Quantity | Formula | Spatial + Amplitude Power | Total Weight $\lambda^\alpha$ on $\mathbb{T}_{L/\lambda}^3$ | Scale-Invariant ($\alpha = 0$)? |
| :--- | :--- | :--- | :--- | :--- |
| Low/High Enstrophy $E_{\le Q}, E_{>Q}$ | $\frac{1}{2}\|P_{\le Q}\omega\|_{L^2}^2$ | $\lambda^{-3} \cdot (\lambda^2)^2$ | **$\lambda^1$** | No (subcritical by $\lambda^1$) |
| Time Derivative $\frac{d}{dt} E_{\le Q}$ | $\partial_t (\frac{1}{2}\|P_{\le Q}\omega\|_{L^2}^2)$ | $\lambda^2 \cdot \lambda^1$ | **$\lambda^3$** | No |
| Advective Flux $\Pi_Q^{\rm adv}$ | $-\langle (u \cdot \nabla)\omega_{\le Q}, \omega_{>Q} \rangle$ | $\lambda^{-3} \cdot (\lambda^1 \cdot \lambda^1 \cdot \lambda^2 \cdot \lambda^2)$ | **$\lambda^3$** | No |
| Total Cross-Cutoff Flux $\Pi_Q^{\omega,\rm tot}$ | $\langle \nabla \times (u \times \omega_{\le Q}), \omega_{>Q} \rangle$ | $\lambda^{-3} \cdot (\lambda^1 \cdot \lambda^1 \cdot \lambda^2 \cdot \lambda^2)$ | **$\lambda^3$** | No |
| Shell Stretching $\mathcal{S}_q, P_{\le Q}^{\rm stretch}$ | $\langle S\omega, \omega_{\le Q} \rangle$ | $\lambda^{-3} \cdot (\lambda^2 \cdot \lambda^2 \cdot \lambda^2)$ | **$\lambda^3$** | No |
| Viscous Shell Loss $D_q, D_{>Q}$ | $\nu \|\nabla P_{>Q}\omega\|_{L^2}^2$ | $\lambda^{-3} \cdot (\lambda^0 \cdot \lambda^1 \cdot \lambda^2)^2$ | **$\lambda^3$** | No |
| Time-Integrated Flux $\int_{t_0}^{t_1} \Pi_Q^{\rm adv}\,dt$ | $\int \Pi_Q^{\rm adv}(t)\,dt$ | $\lambda^{-2} \cdot \lambda^3$ | **$\lambda^1$** | No (matches $E_{>Q} \sim \lambda^1$) |
| NormalizedIntegrated Flux $\frac{\int_{t_0}^{t_1} \Pi_Q^{\rm adv}\,dt}{E_{\le Q}(t_0)}$ | $\frac{\int_{t_0}^{t_1} \Pi_Q^{\rm adv}\,dt}{\frac{1}{2}\|P_{\le Q}\omega(t_0)\|_{L^2}^2}$ | $\lambda^1 / \lambda^1$ | **$\lambda^0$** | **YES (Scale-Invariant)** |
| Active Competition Ratios $\mathfrak{F}_Q^{\rm adv}, \mathfrak{F}_Q^{\rm tot}$ | $[\Pi_Q^{\rm adv}]_+ / D_{>Q}$ | $\lambda^3 / \lambda^3$ | **$\lambda^0$** | **YES (Scale-Invariant)** |
| Duhamel Shell-Step Ratio $\mathfrak{G}_Q$ | $\frac{\|P_{Q+1}\nabla \times (u_{\le Q}\times\omega_{\le Q})\|_{L^2}}{\nu k_0^2 2^{2(Q+1)}\|P_{\le Q}\omega\|_{L^2}}$ | $\frac{\lambda^{-3/2}(\lambda^1 \cdot \lambda^1 \cdot \lambda^2)}{\lambda^0 \cdot \lambda^2 \cdot \lambda^{1/2}}$ | **$\lambda^0$** | **YES (Scale-Invariant)** |

> **Constitutional Caveat (Section 13)**: As enforced by `Mathematical Research Constitution v1.0.1`, **$\text{scale invariance} \neq \text{regularity criterion}$**. The $\lambda^0$ invariance of $\mathfrak{F}_Q^{\rm adv}$, $\mathfrak{F}_Q^{\rm tot}$, and $\mathfrak{G}_Q$ ensures dimensional consistency across parabolic blowup rescalings, but does not by itself close the regularity problem.

---

## 4. Numerical Exploration Summary (Section 23 — `NUMERICAL_OBSERVATION`)

In `tests/test_ns_nonlinear_self_focus_002_suite.py`, deterministic pseudospectral Fourier–Galerkin experiments on $\mathbb{T}_{2\pi}^3$ ($N^3 = 16^3$) and exact 3-mode triad integrations confirm:
1. **Direction and Persistence of $\Pi_Q^{\rm adv}$ and $\Pi_Q^{\omega,\rm tot}$**: Starting from the Taylor–Green vortex in shell $Q=0$ ($|k| = \sqrt{3} \in [1, 2)$, where $E_{>0}(0) = 0$ and $P(0) = 0$), nonlinear triad interaction immediately populates shell $Q+1 = 1$ ($|m| \in [2, 4)$, specifically $|m| = \sqrt{6}, \sqrt{12}$), with $\Pi_0^{\omega,\rm tot}(t) > 0$ and $\Pi_0^{\rm adv}(t) > 0$ persisting across $[0, \Delta t]$ exactly as bounded below by `CLM-042`.
2. **State-Distinguishing Contrast at Identical Instantaneous Global Invariants**: An Arnold–Beltrami–Childress (ABC) flow constructed on the **exact same wavenumber sphere** $|k| = \sqrt{3} \in \mathcal{C}_0$ with **identical initial enstrophy $\|\omega_0\|_{L^2}^2$**, **identical initial palinstrophy $\|\nabla \omega_0\|_{L^2}^2 = 3\|\omega_0\|_{L^2}^2$**, and **identical initial global stretching $P(0) = 0$** satisfies $\Pi_0^{\rm adv}(t) \equiv 0$, $\Pi_0^{\omega,\rm tot}(t) \equiv 0$, and $E_{>0}(t) \equiv 0$ to machine precision ($< 10^{-15}$).
3. **Microscopic Phase Reversal vs. Viscous Damping**: In the minimal 3-mode helical triad ODEs (`Section 4` of `TRIAD_TRANSFER_ANALYSIS`), $\Pi_Q^{\omega,\rm tot}(t)$ is positive during the initial build-up of $\omega_m$, reaches a peak, and in the inviscid/low-viscosity limit reverses sign ($\Pi_Q^{\omega,\rm tot}(t) < 0$, backscatter) as the triad phase rotates past $\pi/2$.
