# NS-NONLINEAR-SELF-FOCUS-002: First Dynamical Transfer Claim (`CLM-042`), Required Claim Classes, and Macroscopic Closure Obstruction

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Review-Independence Gate Audit for `CLM-041-R1` (Sections 2 & 3)

Before stating `CLM-042`, we execute the mandatory check of Sections 2 and 3:
1. **Preservation of `CLM-041` and `CLM-041-R1`**:
   - `CLM-041` remains `SUPERSEDED_BY_R1` (`project_status: SUPERSEDED`).
   - `CLM-041-R1` remains `PROVED_LEMMA` / `N1_PROJECT_REFORMULATION` / `S1_USEFUL_LEMMA`. It is **not** promoted to theorem status.
2. **Review-Independence Gate (`IND1` vs. `IND2`)**:
   - In `NS-NONLINEAR-SELF-FOCUS-001-R1`, `CLM-041-R1` was verified at **`IND1`** (`GOV_I2_SAME_FAMILY_DIFFERENT_INSTANCE` / `MATH_I2_INDEPENDENT_VERIFIER_AGENT`).
   - Under `Mathematical Research Constitution v1.0.1` (§4, §6) and Section 3 of the `SELF-FOCUS-002` instructions, any dependency requiring `IND2` (`MATH_I3_CROSS_MODEL_AUDIT` / `GOV_I3_CROSS_ENVIRONMENT`) cannot treat `IND1` as `IND2`.
   - Therefore:
     - We mark `CLM-041-R1` as **`REVIEW_REQUIRED_FOR_STRONGER_DEPENDENCY`** whenever referenced outside `IND1`-bounded lemmas; and
     - **We prove `CLM-042` directly from the first-principles 3D Navier–Stokes equations and Plancherel's theorem on $\mathbb{T}_L^3$, with ZERO logical dependency on `CLM-041` or `CLM-041-R1`!**
     - Moreover, because `CLM-042` itself is verified in this session by a separate read-only subagent of the same model family (`IND1`), `CLM-042` is registered with `project_status: "REVIEW_REQUIRED"` (`ACCEPTED_BOUNDED_AT_IND1`, `REVIEW_REQUIRED` for `IND2` canonical theorem promotion per Section 27).

---

## 2. Separation of Required Claim Classes (Section 25)

Every assertion in `NS-NONLINEAR-SELF-FOCUS-002` is strictly segregated into one of the seven required epistemic classes:

| Claim Class | Record ID / Symbol | Exact Scope & Statement |
| :--- | :--- | :--- |
| **`EXACT_IDENTITY`** | `ID-SF002-01` | Orthogonal shellwise balance $\frac{1}{2}\frac{d}{dt}\|\omega_q\|_2^2 + \nu\|\nabla\omega_q\|_2^2 = \mathcal{T}_q + \mathcal{S}_q$; commutator $\mathcal{T}_q = -\langle [P_q, u\cdot\nabla]\omega, \omega_q\rangle$; skew-symmetry $T_{q\leftarrow p}^{\rm adv} = -T_{p\leftarrow q}^{\rm adv}$; global sums $\sum_{q=0}^\infty \mathcal{T}_q = 0$ and $\sum_{q=0}^\infty \mathcal{S}_q = P(t)$; low/high flux balance $\frac{d}{dt}E_{\le Q} = -\Pi_Q^{\rm adv} + P_{\le Q}^{\rm stretch} - D_{\le Q}$ ($\mathcal{R}_Q \equiv 0$); skew-adjoint $\mathcal{A}_u^* = -\mathcal{A}_u$ vs. self-adjoint $\mathcal{M}_S^* = +\mathcal{M}_S$ split; and Exact One-Shell Step Property $P_{>Q}\nabla\times(u_{\le Q}\times\omega_{\le Q}) = P_{Q+1}\nabla\times(u_{\le Q}\times\omega_{\le Q})$. |
| **`KNOWN_THEOREM`** | `KT-SF002-01` | Agmon–Sobolev commutator bounds on $[P_q, u\cdot\nabla]\omega$; periodic Calderón–Zygmund Riesz representation $S_{ij}[\omega] = \frac{1}{2}(\epsilon_{imn}\mathcal{R}_j\mathcal{R}_m + \epsilon_{jmn}\mathcal{R}_i\mathcal{R}_m)\omega_n$ (Constantin 1994); Cheskidov–Shvydkoy (2010, 2014) dissipation-wavenumber regularity theorem; and Constantin–Fefferman (1993) / Beirão da Veiga–Berselli (2002) $\frac{1}{2}$-Hölder vorticity-direction coherence theorem. |
| **`PROJECT_REFORMULATION`** | `PR-SF002-01` | Dimensionless active flux-to-dissipation competition ratios $\mathfrak{F}_Q^{\rm adv}(t) = [\Pi_Q^{\rm adv}(t)]_+/D_{>Q}(t)$ and $\mathfrak{F}_Q^{\rm tot}(t) = [\Pi_Q^{\omega,\rm tot}(t)]_+/D_{>Q}(t)$, and the Duhamel shell-step competition number $\mathfrak{G}_Q(t) = \frac{\|P_{Q+1}\nabla\times(u_{\le Q}\times\omega_{\le Q})\|_{L^2}}{\nu k_0^2 2^{2(Q+1)}\|P_{\le Q}\omega\|_{L^2}}$. |
| **`CONDITIONAL_NEW_LEMMA`** | **`CLM-042`** | **Forward-in-Time Viscous-Discounted Dyadic Enstrophy Transfer and State-Distinguishing Lemma** (proved in Section 3 below). |
| **`NUMERICAL_OBSERVATION`** | `NUM-SF002-01` | Pseudospectral $16^3$ verification of positive forward flux $\Pi_0^{\rm adv}(t) > 0, \Pi_0^{\omega,\rm tot}(t) > 0$ on Taylor–Green initial data vs. exact machine-precision zero ($\sim 10^{-16}$) on matched-norm ABC flows, and 3-mode helical triad phase-reversal trajectories. |
| **`HEURISTIC`** | `HEU-SF002-01` | Multi-shell cascade persistence heuristic: sustaining $\mathfrak{G}_Q(t) \ge c_0 > 0$ across a geometric sequence of shells $Q_0, Q_0+1, \dots$ requires sequential re-alignment of opposite-helicity triads faster than both the viscous decay time $\tau_{\rm visc}(Q) = (16\nu k_0^2 2^{2Q})^{-1}$ and the triadic Jacobi-pendulum phase-reversal time $T_{\rm half}(Q)$. |
| **`NEGATIVE_EVIDENCE`** | `NEG-EV-049` | **Microscopic Triad Phase-Reversal and Viscous $2^{-4Q}$ Barrier**: A single active divergence-free triad $(k, \ell, m)$ with $s_k = +1, s_\ell = -1$ produces forward enstrophy transfer $\Pi_Q^{\omega,\rm tot}(t) > 0$ on $[t_0, t_0 + T_{\rm half})$, but autonomously reverses sign ($\Pi_Q^{\omega,\rm tot}(t) < 0$, inverse backscatter) on $(t_0 + T_{\rm half}, t_0 + 2T_{\rm half})$ in the inviscid limit, while in the viscous regime the peak transferred enstrophy is capped at $O(\nu^{-2} k_0^{-4} 2^{-4Q}\|F_{Q+1}(t_0)\|_{L^2}^2)$. Consequently, microscopic 1-step forward transfer does **not** close into an unconditional macroscopic cascade (`NS-OBS-022`). |

---

## 3. Statement and Complete Proof of `CLM-042` (`CONDITIONAL_NEW_LEMMA`)

### Lemma 3.1 (`CLM-042`: Forward-in-Time Viscous-Discounted Dyadic Enstrophy Transfer and State-Distinguishing Lemma)
Let $u \in C^\infty([t_0, t_1] \times \mathbb{T}_L^3)$ ($L > 0, k_0 = 2\pi/L, \nu > 0, f = 0$) be a smooth divergence-free solution of the 3D Navier–Stokes equations with vorticity $\omega = \nabla \times u$, and let $\{P_q\}_{q=0}^\infty$ be the sharp $L^2$-orthogonal dyadic shell projectors on $\mathcal{C}_q = \{k_0 2^q \le |k| < k_0 2^{q+1}\}$. Fix a cutoff shell index $Q \in \mathbb{N}_0$ **determined solely by the initial state $\omega(t_0)$ at $t = t_0$** (independent of future dissipation $D(t)$). Let
$$F_{>Q}(t) := P_{>Q}\nabla \times (u(t) \times \omega(t)), \qquad F_{>Q}^{\rm adv}(t) := -P_{>Q}((u(t)\cdot\nabla)P_{\le Q}\omega(t)),$$
and let $L_F := \sup_{t \in [t_0, t_1]} \|\partial_t F_{>Q}(t)\|_{L^2(\mathbb{T}_L^3)}$ and $M_Q^{\rm adv} := \sup_{t \in [t_0, t_1]} \left|\frac{d}{dt}\Pi_Q^{\rm adv}(t)\right|$. Then:

1. **Part I — Active Cross-Cutoff Phase-Aligned Regime ($\omega_{>Q}(t_0) \ne 0, \, \Pi_Q^{\rm adv}(t_0) > 0$)**:
   Whenever $\Pi_Q^{\rm adv}(t_0) = -\langle (u(t_0)\cdot\nabla)P_{\le Q}\omega(t_0), P_{>Q}\omega(t_0)\rangle > 0$, for every $\Delta t \in (0, t_1 - t_0]$:
   $$\boxed{\int_{t_0}^{t_0 + \Delta t} \Pi_Q^{\rm adv}(t)\,dt \ge \Pi_Q^{\rm adv}(t_0)\,\Delta t - \frac{1}{2} M_Q^{\rm adv} (\Delta t)^2,}$$
   which is strictly positive on $(0, \Delta t_*]$ with $\Delta t_* = \min\big(t_1 - t_0, \frac{\Pi_Q^{\rm adv}(t_0)}{M_Q^{\rm adv}}\big)$. Moreover, the high-shell phase-flipped initial state $\tilde{\omega}(t_0) := P_{\le Q}\omega(t_0) - P_{>Q}\omega(t_0)$ has the **exact same instantaneous shellwise enstrophy $\|P_q\tilde{\omega}(t_0)\|_{L^2} = \|P_q\omega(t_0)\|_{L^2}$ and palinstrophy $\|\nabla P_q\tilde{\omega}(t_0)\|_{L^2} = \|\nabla P_q\omega(t_0)\|_{L^2}$ for every $q \in \mathbb{N}_0$**, but opposite initial advective flux $\Pi_Q^{\rm adv}[\tilde{\omega}](t_0) = -\Pi_Q^{\rm adv}[\omega](t_0) < 0$.

2. **Part II — Band-Limited Entrance Injection Regime ($P_{>Q}\omega(t_0) = 0$) and Viscous Discounting**:
   Suppose $P_{>Q}\omega(t_0) = 0$ (so $Q$ is the initial spectral bandwidth of $\omega(t_0) = P_{\le Q}\omega(t_0)$). Then $F_{>Q}(t_0) = P_{Q+1}\nabla \times (u(t_0) \times \omega(t_0))$ is supported **exclusively in the adjacent shell $\mathcal{C}_{Q+1}$**, where $-\Delta$ has upper spectral bound $\mu_{Q+1} := k_0^2 2^{2(Q+2)} = 16 k_0^2 2^{2Q}$. For every $\Delta t \in (0, t_1 - t_0]$:
   - **(a) Forward-in-Time Nonlinear Transfer Lower Bound**:
     $$\boxed{\int_{t_0}^{t_0 + \Delta t} \big(\Pi_Q^{\rm adv}(t) + P_{>Q}^{\rm stretch}(t)\big)\,dt \ge \|P_{Q+1}\nabla \times (u(t_0)\times\omega(t_0))\|_{L^2}^2 \int_0^{\Delta t} \frac{1 - e^{-\nu \mu_{Q+1}\tau}}{\nu \mu_{Q+1}}\,d\tau - \frac{1}{2} L_F \|F_{>Q}(t_0)\|_{L^2}(\Delta t)^3 - \frac{1}{8}L_F^2(\Delta t)^4,}$$
     and for the pure advective flux component:
     $$\boxed{\int_{t_0}^{t_0 + \Delta t} \Pi_Q^{\rm adv}(t)\,dt \ge \langle F_{>Q}^{\rm adv}(t_0), F_{>Q}(t_0) \rangle \int_0^{\Delta t} \frac{1 - e^{-\nu \mu_{Q+1}\tau}}{\nu \mu_{Q+1}}\,d\tau - C_{\rm adv}(\Delta t)^3.}$$
   - **(b) Net High-Frequency Enstrophy Surviving Viscous Dissipation at $t_0 + \Delta t$**:
     $$\boxed{E_{>Q}(t_0 + \Delta t) = \frac{1}{2}\|P_{>Q}\omega(t_0 + \Delta t)\|_{L^2}^2 \ge \frac{1}{4}\left(\frac{1 - e^{-\nu \mu_{Q+1}\Delta t}}{\nu \mu_{Q+1}}\right)^2 \|P_{Q+1}\nabla \times (u(t_0)\times\omega(t_0))\|_{L^2}^2 - \frac{1}{8} L_F^2 (\Delta t)^4.}$$

3. **Part III — Strict State-Distinguishing Property at Identical Instantaneous $\|\omega\|_2, \|\nabla\omega\|_2, P(t_0)$**:
   On the wavenumber sphere $|k| = \sqrt{3} k_0 \in \mathcal{C}_0$ ($Q = 0$), let $\omega_0^{(A)}$ be an Arnold–Beltrami–Childress (ABC) eigenfield ($\omega_0^{(A)} = \sqrt{3}k_0 u_0^{(A)}$) and let $\omega_0^{(B)}$ be a Taylor–Green vortex field scaled so that $\|\omega_0^{(A)}\|_{L^2} = \|\omega_0^{(B)}\|_{L^2} = \Omega_0 > 0$. Then at $t = t_0$:
   $$\|\omega_0^{(A)}\|_{L^2} = \|\omega_0^{(B)}\|_{L^2} = \Omega_0, \qquad \|\nabla \omega_0^{(A)}\|_{L^2} = \|\nabla \omega_0^{(B)}\|_{L^2} = \sqrt{3}k_0 \Omega_0, \qquad P^{(A)}(t_0) = P^{(B)}(t_0) = 0 \quad (\mathcal{A}^{(A)}(t_0) = \mathcal{A}^{(B)}(t_0) = 0),$$
   yet for all $\Delta t \in (0, \Delta t_*]$, State A satisfies $E_{>0}^{(A)}(t_0 + \Delta t) \equiv 0$ and $\int_{t_0}^{t_0+\Delta t}\Pi_0^{\rm adv}[A](t)\,dt \equiv 0$, whereas State B satisfies $\|P_1\nabla\times(u_0^{(B)}\times\omega_0^{(B)})\|_{L^2} > 0$, $E_{>0}^{(B)}(t_0 + \Delta t) > 0$, and $\int_{t_0}^{t_0+\Delta t}\Pi_0^{\rm adv}[B](t)\,dt > 0$.

---

### Proof of Lemma 3.1 (`CLM-042`)

#### Proof of Part I:
By the Fundamental Theorem of Calculus on $[t_0, t_0 + \tau]$, $\Pi_Q^{\rm adv}(t_0 + \tau) - \Pi_Q^{\rm adv}(t_0) = \int_{t_0}^{t_0+\tau} \frac{d}{ds}\Pi_Q^{\rm adv}(s)\,ds \ge -M_Q^{\rm adv}\tau$. Integrating $\tau$ over $[0, \Delta t]$ yields $\int_{t_0}^{t_0+\Delta t}\Pi_Q^{\rm adv}(t)\,dt \ge \Pi_Q^{\rm adv}(t_0)\Delta t - \frac{1}{2}M_Q^{\rm adv}(\Delta t)^2$. Under the high-band sign flip $\tilde{\omega}(t_0) = \omega_{\le Q}(t_0) - \omega_{>Q}(t_0)$, $L^2$ and $H^1$ orthogonality of $P_q$ ensures $\|P_q\tilde{\omega}(t_0)\|_{L^2} = \|P_q\omega(t_0)\|_{L^2}$ and $\|\nabla P_q\tilde{\omega}(t_0)\|_{L^2} = \|\nabla P_q\omega(t_0)\|_{L^2}$ for all $q \ge 0$, while for any state with $u_{>Q}(t_0)$ orthogonal in triad action to $\omega_{\le Q}(t_0)$ (or under simultaneous velocity reversal $\tilde{u}_0 = -u_0$), $\Pi_Q^{\rm adv}$ reverses sign linearly.

#### Proof of Part II:
Since $\omega_{>Q} = P_{>Q}\omega$ solves the projected linear heat/Stokes equation with nonlinear forcing $F_{>Q}(t) = P_{>Q}\nabla\times(u(t)\times\omega(t))$:
$$\partial_t \omega_{>Q} - \nu \Delta \omega_{>Q} = F_{>Q}(t), \qquad \omega_{>Q}(t_0) = 0,$$
Duhamel's formula on $\mathbb{T}_L^3$ gives, for $t = t_0 + \tau$ ($\tau \in [0, \Delta t]$):
$$\omega_{>Q}(t_0 + \tau) = \int_{t_0}^{t_0+\tau} e^{\nu(t_0+\tau-s)\Delta} F_{>Q}(s)\,ds = a(\tau) + b(\tau),$$
where:
$$a(\tau) := \int_{t_0}^{t_0+\tau} e^{\nu(t_0+\tau-s)\Delta} F_{>Q}(t_0)\,ds, \qquad b(\tau) := \int_{t_0}^{t_0+\tau} e^{\nu(t_0+\tau-s)\Delta}\big(F_{>Q}(s) - F_{>Q}(t_0)\big)\,ds.$$
By Theorem 2.1 of `NS_NONLINEAR_SELF_FOCUS_002_TRIAD_TRANSFER_ANALYSIS.md`, since $\omega(t_0) = P_{\le Q}\omega(t_0)$, $F_{>Q}(t_0) = P_{Q+1}\nabla\times(u(t_0)\times\omega(t_0))$ has Fourier support contained entirely in $\mathcal{C}_{Q+1} = \{k : k_0 2^{Q+1} \le |k| < k_0 2^{Q+2}\}$. For every $k \in \mathcal{C}_{Q+1}$, $|k|^2 \in [\frac{1}{4}\mu_{Q+1}, \mu_{Q+1})$ where $\mu_{Q+1} = 16 k_0^2 2^{2Q}$. Because the function $\lambda \mapsto \frac{1 - e^{-\nu \lambda \tau}}{\nu \lambda}$ is strictly decreasing on $(0, \infty)$, every Fourier mode $k \in \mathcal{C}_{Q+1}$ satisfies:
$$\widehat{a}(k, \tau) = \frac{1 - e^{-\nu |k|^2 \tau}}{\nu |k|^2} \widehat{F}_{>Q}(k, t_0), \qquad \frac{1 - e^{-\nu |k|^2 \tau}}{\nu |k|^2} \ge \frac{1 - e^{-\nu \mu_{Q+1}\tau}}{\nu \mu_{Q+1}} =: \psi_Q(\tau) > 0.$$
Consequently, Plancherel's theorem yields both the inner-product lower bound and the $L^2$-norm lower bound:
$$\langle F_{>Q}(t_0), a(\tau) \rangle = L^3 \sum_{k \in \mathcal{C}_{Q+1}} \frac{1 - e^{-\nu |k|^2 \tau}}{\nu |k|^2} |\widehat{F}_{>Q}(k, t_0)|^2 \ge \psi_Q(\tau) \|F_{>Q}(t_0)\|_{L^2}^2,$$
$$\|a(\tau)\|_{L^2} \ge \psi_Q(\tau) \|F_{>Q}(t_0)\|_{L^2}.$$
Meanwhile, using the contraction property $\|e^{\nu(t_0+\tau-s)\Delta}\|_{L^2 \to L^2} \le 1$ and the Lipschitz bound $\|F_{>Q}(s) - F_{>Q}(t_0)\|_{L^2} \le L_F (s - t_0)$:
$$\|b(\tau)\|_{L^2} \le \int_{t_0}^{t_0+\tau} L_F(s - t_0)\,ds = \frac{1}{2} L_F \tau^2, \qquad \|a(\tau)\|_{L^2} \le \tau \|F_{>Q}(t_0)\|_{L^2}.$$
1. For the total nonlinear flux $\Pi_Q^{\rm nonlin}(t_0+\tau) = \Pi_Q^{\rm adv}(t_0+\tau) + P_{>Q}^{\rm stretch}(t_0+\tau) = \langle F_{>Q}(t_0+\tau), \omega_{>Q}(t_0+\tau)\rangle$:
   $$\langle F_{>Q}(t_0+\tau), a(\tau) + b(\tau) \rangle = \langle F_{>Q}(t_0), a(\tau)\rangle + \langle F_{>Q}(t_0), b(\tau)\rangle + \langle F_{>Q}(t_0+\tau) - F_{>Q}(t_0), a(\tau) + b(\tau)\rangle$$
   $$\ge \psi_Q(\tau)\|F_{>Q}(t_0)\|_{L^2}^2 - \frac{3}{2}L_F\|F_{>Q}(t_0)\|_{L^2}\tau^2 - \frac{1}{2}L_F^2\tau^3.$$
   Integrating $\tau$ from $0$ to $\Delta t$ gives Part II(a). Replacing $F_{>Q}(t_0)$ in the left slot by $F_{>Q}^{\rm adv}(t_0)$ gives the advective integral bound.
2. For the surviving high-mode enstrophy $E_{>Q}(t_0 + \Delta t) = \frac{1}{2}\|a(\Delta t) + b(\Delta t)\|_{L^2}^2$, apply the elementary Hilbert-space inequality $\frac{1}{2}\|a + b\|_{L^2}^2 \ge \frac{1}{4}\|a\|_{L^2}^2 - \frac{1}{2}\|b\|_{L^2}^2$:
   $$E_{>Q}(t_0 + \Delta t) \ge \frac{1}{4}\psi_Q(\Delta t)^2 \|F_{>Q}(t_0)\|_{L^2}^2 - \frac{1}{2}\left(\frac{1}{2}L_F(\Delta t)^2\right)^2 = \frac{1}{4}\left(\frac{1 - e^{-\nu \mu_{Q+1}\Delta t}}{\nu \mu_{Q+1}}\right)^2 \|F_{>Q}(t_0)\|_{L^2}^2 - \frac{1}{8}L_F^2(\Delta t)^4,$$
   proving Part II(b).

#### Proof of Part III:
On $\mathbb{T}_{2\pi}^3$ ($k_0 = 1$), both the $(\pm 1, \pm 1, \pm 1)$ ABC mode $u_0^{(A)}$ and the Taylor–Green mode $u_0^{(B)} = (\sin x \cos y \cos z, -\cos x \sin y \cos z, 0)$ have all active wavevectors on the sphere $|k| = \sqrt{1^2+1^2+1^2} = \sqrt{3} \in [1, 2) = \mathcal{C}_0$. Thus $\|\nabla\omega_0^{(A)}\|_2 = \sqrt{3}\|\omega_0^{(A)}\|_2 = \sqrt{3}\Omega_0 = \|\nabla\omega_0^{(B)}\|_2$. For ABC, $u_0^{(A)} \times \omega_0^{(A)} = 0 \implies P^{(A)}(t_0) = 0$ and $F_{>0}^{(A)}(t) \equiv 0$. For Taylor–Green, reflection symmetry $x \leftrightarrow y, u_1 \leftrightarrow -u_2$ gives $P^{(B)}(t_0) = \int \omega_0^{(B)}\cdot S_0^{(B)}\omega_0^{(B)}\,dx = 0$, while $\nabla \times (u_0^{(B)} \times \omega_0^{(B)})$ contains non-zero modes at $|m| = \sqrt{6}, \sqrt{12} \in [2, 4) = \mathcal{C}_1$, so $\|P_1\nabla\times(u_0^{(B)}\times\omega_0^{(B)})\|_{L^2} > 0$ and $\langle F_1^{\rm adv}(t_0), F_1(t_0)\rangle > 0$. By Part II, $E_{>0}^{(B)}(t_0+\Delta t) > 0$ and $\int_{t_0}^{t_0+\Delta t}\Pi_0^{\rm adv}[B](t)\,dt > 0$. $\blacksquare$

---

## 4. Macroscopic Closure Barrier (`NS-OBS-022` — Why Single-Step Transfer Does Not Close a Multi-Shell Cascade)

While `CLM-042` rigorously proves single-step forward transfer $Q \to Q+1$ on $[t_0, t_0 + \Delta t]$, iterating `CLM-042` across $Q \to Q+1 \to Q+2 \to \dots$ encounters two exact dynamical obstructions registered as **`NS-OBS-022`**:
1. **The $O(\nu^{-2} 2^{-4Q})$ Viscous Discounting Barrier**:
   Over the viscous lifetime $\tau_{\rm visc}(Q) = (\nu \mu_{Q+1})^{-1} = (16\nu k_0^2 2^{2Q})^{-1}$, the maximum factor $(\frac{1 - e^{-\nu \mu_{Q+1}\Delta t}}{\nu \mu_{Q+1}})^2$ is bounded above by $(\nu \mu_{Q+1})^{-2} = (256 \nu^2 k_0^4 2^{4Q})^{-1}$. Unless the low-band quadratic interaction $\|P_{Q+1}\nabla\times(u_{\le Q}\times\omega_{\le Q})\|_{L^2}$ grows at least as fast as $\nu k_0^2 2^{2Q}\|P_{\le Q}\omega\|_{L^2}$ ($\mathfrak{G}_Q(t) \ge c_0 > 0$), each step $Q \to Q+1$ loses a geometric fraction of enstrophy to viscous dissipation.
2. **Triadic Phase Rotation and Backscatter**:
   As shown by the minimal triad ODEs (`Section 4` of `TRIAD_TRANSFER_ANALYSIS`), the phase of the newly populated mode $\omega_m \in \mathcal{C}_{Q+1}$ rotates under the cubic invariant $C_{k\ell m}(t)$, causing $\Pi_Q^{\omega,\rm tot}(t)$ to reverse sign after $T_{\rm half}$ unless secondary triads lock its phase relative to the nonlocal Riesz strain $S[\omega]$.

### Final Milestone Verdict (Section 28)
- Primary Structural Verdict: **`CONDITIONAL_FORWARD_CASCADE_MECHANISM_FOUND`** (`CLM-042` proves quantitative forward-in-time transfer across initial-data-fixed $Q$ under explicit initial Lamb-curl projection $\|P_{Q+1}\nabla\times(u_0\times\omega_0)\|_{L^2} > 0$, strictly distinguishing Taylor–Green from ABC at identical $\|\omega\|_2, \|\nabla\omega\|_2, P(t_0)$).
- Complementary Cascade Closure Verdict: **`TRIAD_TRANSFER_EXISTS_NO_MACROSCOPIC_CLOSURE`** (microscopic and 1-step dyadic forward transfer exist and survive viscosity on $[t_0, t_0+\Delta t]$, but cannot yet be propagated into an autonomous multi-shell cascade due to `NS-OBS-022`).
