# NS-NONLINEAR-SELF-FOCUS-002: Triadic Enstrophy Transfer, Nonlocal Strain, Minimal Triad ODEs, and Helicity

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  

---

## 1. Exact Fourier Triadic Enstrophy Transfer Kernel (Section 7)

On $\mathbb{T}_L^3$ with fundamental wavenumber $k_0 = 2\pi/L$, expand velocity and vorticity in Fourier modes ($k \in k_0\mathbb{Z}^3 \setminus \{0\}$):
$$\widehat{\omega}(k) = i k \times \widehat{u}(k), \qquad \widehat{u}(k) = \frac{i k \times \widehat{\omega}(k)}{|k|^2}, \qquad k \cdot \widehat{u}(k) = k \cdot \widehat{\omega}(k) = 0.$$
Using $\partial_t \omega = \nabla \times (u \times \omega) + \nu \Delta \omega = -(u \cdot \nabla)\omega + (\omega \cdot \nabla)u + \nu \Delta \omega$, the Fourier mode $m \in k_0\mathbb{Z}^3 \setminus \{0\}$ evolves according to (`EXACT_IDENTITY`):
$$\partial_t \widehat{\omega}(m) + \nu |m|^2 \widehat{\omega}(m) = \sum_{\substack{k + \ell = m \\ k, \ell \ne 0}} i m \times \big(\widehat{u}(k) \times \widehat{\omega}(\ell)\big) = \sum_{\substack{k + \ell = m \\ k, \ell \ne 0}} \Big[ -i (m \cdot \widehat{u}(k))\widehat{\omega}(\ell) + i (\ell \cdot \widehat{\omega}(\ell))_{\text{stretch}} \Big],$$
where the exact decomposition into advective and stretching triads is:
$$\widehat{\mathcal{N}}_{\rm adv}(m; k, \ell) := -i (\ell \cdot \widehat{u}(k))\widehat{\omega}(\ell) = \frac{(\ell \cdot (k \times \widehat{\omega}(k)))}{|k|^2} \widehat{\omega}(\ell),$$
$$\widehat{\mathcal{N}}_{\rm stretch}(m; k, \ell) := i (k \cdot \widehat{\omega}(\ell))\widehat{u}(k) = -\frac{(k \cdot \widehat{\omega}(\ell))}{|k|^2} (k \times \widehat{\omega}(k)),$$
with total symmetrized triad kernel (using $m \times (a \times b) = (m \cdot b)a - (m \cdot a)b$ and $m = k + \ell$):
$$i m \times \big(\widehat{u}(k) \times \widehat{\omega}(\ell)\big) = \widehat{\mathcal{N}}_{\rm adv}(m; k, \ell) + \widehat{\mathcal{N}}_{\rm stretch}(m; k, \ell).$$

### 1.1 Mode-to-Mode Triadic Enstrophy Transfer Rate
Pairing $\partial_t \widehat{\omega}(m)$ with $\overline{\widehat{\omega}(m)} = \widehat{\omega}(-m)$ gives the exact triadic enstrophy input into mode $m$ from pair $(k, \ell)$ with $k + \ell = m$:
$$K^{\rm adv}(m \mid k, \ell) := L^3 \operatorname{Re}\left[ \frac{\ell \cdot (k \times \widehat{\omega}(k))}{|k|^2} \big(\widehat{\omega}(\ell) \cdot \overline{\widehat{\omega}(m)}\big) \right],$$
$$K^{\rm stretch}(m \mid k, \ell) := -L^3 \operatorname{Re}\left[ \frac{k \cdot \widehat{\omega}(\ell)}{|k|^2} \big((k \times \widehat{\omega}(k)) \cdot \overline{\widehat{\omega}(m)}\big) \right],$$
$$K^{\rm tot}(m \mid k, \ell) := K^{\rm adv}(m \mid k, \ell) + K^{\rm stretch}(m \mid k, \ell) = L^3 \operatorname{Re}\Big[ i \big(m \times (\widehat{u}(k) \times \widehat{\omega}(\ell))\big) \cdot \overline{\widehat{\omega}(m)} \Big].$$
Notice the **Exact Triadic Detail Balance for Advection** (`EXACT_IDENTITY`):
Because $\ell \cdot (k \times \widehat{\omega}(k)) = (k + \ell)\cdot (k \times \widehat{\omega}(k)) = m \cdot (k \times \widehat{\omega}(k))$, swapping $\ell \leftrightarrow -m$ (with fixed velocity mode $k$) reverses the sign of the scalar triple product:
$$\boxed{K^{\rm adv}(m \mid k, \ell) + K^{\rm adv}(\ell \mid -k, m) = 0 \qquad (\forall k + \ell = m).}$$
Thus, in every triad $(k, \ell, m)$, the velocity mode $k$ acts as an incompressible carrier that **conservatively redistributes enstrophy between vorticity modes $\ell$ and $m$** without creating or destroying enstrophy! By contrast, $K^{\rm stretch}(m \mid k, \ell)$ does not cancel pairwise between $\ell$ and $m$: it represents genuine vortex-stretching amplification/depletion driven by the velocity gradient of mode $k$.

---

## 2. Classification of Interaction Classes and the Exact Dyadic One-Shell Step Theorem (Section 7)

Fix a cutoff $Q \in \mathbb{N}_0$ ($\mathcal{C}_{\le Q} = \{0 < |k| < k_0 2^{Q+1}\}$, $\mathcal{C}_{>Q} = \{|k| \ge k_0 2^{Q+1}\}$). For any mode $m \in \mathcal{C}_{>Q}$, every triad $k + \ell = m$ falls into one of four classes $(I_u, I_\omega) \in \{\text{Low} (\le Q), \text{High} (> Q)\}^2$:

| Triad Class $(k \text{ in } u, \, \ell \text{ in } \omega \to m \in \mathcal{C}_{>Q})$ | Frequency Regime | Role in $\Pi_Q^{\rm adv}$ and $\Pi_Q^{\omega,\rm tot}$ | Can Transfer Enstrophy from $\le Q$ to $> Q$? |
| :--- | :--- | :--- | :--- |
| **1. Low–Low $\to$ High** ($k \in \mathcal{C}_{\le Q}, \ell \in \mathcal{C}_{\le Q}$) | Local near cutoff: $|k| + |\ell| \ge |m| \ge k_0 2^{Q+1} \implies \max(|k|,|\ell|) \ge k_0 2^Q$ (shells $Q-1, Q$) | Enters **both** $\Pi_Q^{\rm adv}$ (via $-\langle (u_{\le Q}\cdot\nabla)\omega_{\le Q}, \omega_{>Q}\rangle$) and $P_Q^{\rm cross}$ (via $\langle (\omega_{\le Q}\cdot\nabla)u_{\le Q}, \omega_{>Q}\rangle$) | **YES (Primary Forward Injection Class)**: Only class active when $\omega_{>Q}(t_0) = 0$; exclusively populates shell $q = Q+1$. |
| **2. High–Low $\to$ High** ($k \in \mathcal{C}_{>Q}, \ell \in \mathcal{C}_{\le Q}$) | Nonlocal or local high-velocity straining of low vorticity | Enters $\Pi_Q^{\rm adv}$ ($-\langle (u_{>Q}\cdot\nabla)\omega_{\le Q}, \omega_{>Q}\rangle$) and $P_Q^{\rm cross}$ ($\langle (\omega_{\le Q}\cdot\nabla)u_{>Q}, \omega_{>Q}\rangle$) | **YES (Secondary Feedback Class)**: Requires pre-existing high-frequency velocity $u_{>Q} \ne 0$; suppressed by Biot–Savart factor $|k|^{-2} \le k_0^{-2} 2^{-2(Q+1)}$. |
| **3. Low–High $\to$ High** ($k \in \mathcal{C}_{\le Q}, \ell \in \mathcal{C}_{>Q}$) | Nonlocal sweeping/straining of high vorticity by large-scale velocity $u_{\le Q}$ | Advective part cancels inside $\mathcal{C}_{>Q}$ ($\langle (u_{\le Q}\cdot\nabla)\omega_{>Q}, \omega_{>Q}\rangle = 0$); stretching part $\langle S_{\le Q}\omega_{>Q}, \omega_{>Q}\rangle$ is **intra-high-band stretching** $P_{>Q}^{\rm intra}$ | **NO across cutoff $Q$** (advective part only redistributes *within* $>Q$; stretching part amplifies pre-existing $\omega_{>Q}$ in place). |
| **4. High–High $\to$ High** ($k \in \mathcal{C}_{>Q}, \ell \in \mathcal{C}_{>Q}$) | Fully high-frequency interaction inside $\mathcal{C}_{>Q}$ | Advective part cancels inside $\mathcal{C}_{>Q}$ ($\langle (u_{>Q}\cdot\nabla)\omega_{>Q}, \omega_{>Q}\rangle = 0$); stretching part $\langle S_{>Q}\omega_{>Q}, \omega_{>Q}\rangle$ is in $P_{>Q}^{\rm intra}$ | **NO across cutoff $Q$** (purely internal to $>Q$). |

### Theorem 2.1 (Exact Dyadic One-Shell Step Property for Low–Low Injection — `EXACT_IDENTITY` / `PROVED_LEMMA`)
For any divergence-free pair $u_{\le Q}, \omega_{\le Q}$ supported in $\mathcal{C}_{\le Q} = \{0 < |k| < k_0 2^{Q+1}\}$, the high-frequency projection of their nonlinear interaction is supported **exclusively in the single adjacent dyadic shell $\mathcal{C}_{Q+1}$**:
$$\boxed{P_{>Q}\nabla \times (u_{\le Q} \times \omega_{\le Q}) = P_{Q+1}\nabla \times (u_{\le Q} \times \omega_{\le Q}), \qquad P_q \nabla \times (u_{\le Q} \times \omega_{\le Q}) \equiv 0 \quad (\forall q \ge Q+2).}$$
Similarly, $P_{>Q}((u_{\le Q}\cdot\nabla)\omega_{\le Q}) = P_{Q+1}((u_{\le Q}\cdot\nabla)\omega_{\le Q})$ and $P_{>Q}((\omega_{\le Q}\cdot\nabla)u_{\le Q}) = P_{Q+1}((\omega_{\le Q}\cdot\nabla)u_{\le Q})$.

*Proof:* Every Fourier mode $m$ in the support of $u_{\le Q} \times \omega_{\le Q}$ satisfies $m = k + \ell$ with $k, \ell \in \mathcal{C}_{\le Q}$, so $|k| < k_0 2^{Q+1}$ and $|\ell| < k_0 2^{Q+1}$. By the triangle inequality,
$$|m| \le |k| + |\ell| < k_0 2^{Q+1} + k_0 2^{Q+1} = k_0 2^{Q+2}.$$
Since $\bigcup_{q \ge Q+2} \mathcal{C}_q = \{m \in k_0\mathbb{Z}^3 : |m| \ge k_0 2^{Q+2}\}$, every Fourier coefficient of $u_{\le Q} \times \omega_{\le Q}$ with $m \in \mathcal{C}_q$ ($q \ge Q+2$) vanishes identically. $\blacksquare$

---

## 3. Nonlocal Pressure/Strain Operator and Singular-Integral Representation (Section 19)

The symmetric strain tensor $S_{ij} = \frac{1}{2}(\partial_j u_i + \partial_i u_j)$ is **not** an independent local field: it is uniquely and nonlocally determined by $\omega$ via the periodic Biot–Savart law $u = -\Delta^{-1}(\nabla \times \omega)$.

### 3.1 Exact Riesz Transform and Principal-Value Representation (`KNOWN_THEOREM` / `EXACT_IDENTITY`)
Let $\mathcal{R}_j := \partial_j (-\Delta)^{-1/2}$ ($\widehat{\mathcal{R}_j f}(k) = i \frac{k_j}{|k|}\widehat{f}(k)$ for $k \ne 0$) be the periodic Calderón–Zygmund Riesz transforms on $\mathbb{T}_L^3$. Then $\partial_j u_i = \epsilon_{imn} \mathcal{R}_j \mathcal{R}_m \omega_n$, and therefore:
$$\boxed{S_{ij}[\omega] = \frac{1}{2}\big(\epsilon_{imn}\mathcal{R}_j \mathcal{R}_m + \epsilon_{jmn}\mathcal{R}_i \mathcal{R}_m\big)\omega_n, \qquad \widehat{S}_{ij}(k) = \frac{i}{2|k|^2}\Big(k_i (\widehat{\omega}(k) \times k)_j + k_j (\widehat{\omega}(k) \times k)_i\Big).}$$
In physical space on $\mathbb{T}_L^3$, $S_{ij}[\omega](x)$ is the periodic principal-value singular integral (Constantin 1994):
$$S_{ij}[\omega](x) = \frac{3}{8\pi} \operatorname{P.V.} \int_{\mathbb{T}_L^3} \sum_{n \in \mathbb{Z}^3} \frac{(y_i - n_i L)\epsilon_{jkl}(y_k - n_k L) + (y_j - n_j L)\epsilon_{ikl}(y_k - n_k L)}{|y - nL|^5} \omega_l(x - y)\,dy.$$

### 3.2 Consequences of Nonlocal Strain for Forward Flux Stability
1. **Exact Norm Isometric Identity on Shells**:
   For every Fourier mode $k \ne 0$, since $k \cdot \widehat{\omega}(k) = 0$, $|k \times \widehat{\omega}(k)| = |k||\widehat{\omega}(k)|$, and:
   $$\sum_{i,j=1}^3 |\widehat{S}_{ij}(k)|^2 = \frac{1}{2}|k|^2 |\widehat{u}(k)|^2 = \frac{1}{2}|\widehat{\omega}(k)|^2 \implies \|S[\omega_q]\|_{L^2(\mathbb{T}_L^3)} = \frac{1}{\sqrt{2}}\|\omega_q\|_{L^2(\mathbb{T}_L^3)} \quad (\forall q \in \mathbb{N}_0).$$
   Thus $S$ is an **order-zero nonlocal operator on $\omega$** ($\|S\|_{L^2} = 2^{-1/2}\|\omega\|_{L^2}$), whereas the advective velocity $u = -\Delta^{-1}\nabla\times\omega$ is an **order-$(-1)$ smoothing operator on $\omega$** ($\|u_q\|_{L^2} \asymp 2^{-q}\|\omega_q\|_{L^2}$).
2. **High-Wavenumber Velocity Depletion vs. Strain Locality**:
   In the cross-cutoff flux $\Pi_Q^{\rm adv}(t) = -\langle (u_{\le Q}\cdot\nabla)\omega_{\le Q}, \omega_{>Q}\rangle - \langle (u_{>Q}\cdot\nabla)\omega_{\le Q}, \omega_{>Q}\rangle$, the high-frequency velocity contribution $u_{>Q}$ carries the Biot–Savart damping factor $|k|^{-1} \le k_0^{-1} 2^{-(Q+1)}$. Consequently, low-to-high advective flux across $2^Q$ is dominated by **large-scale/cutoff velocity modes $u_{\le Q}$** sweeping and shearing cutoff vorticity modes $\omega_{\le Q}$ into $\omega_{Q+1}$.

---

## 4. Minimal Divergence-Free Triad Model (Section 21)

To analyze the microscopic dynamics of scale transfer, construct the exact minimal divergence-free Fourier triad $k + \ell + p = 0$ (or $k + \ell = m$ with $p = -m$) on $\mathbb{T}_{2\pi}^3$ ($k_0 = 1$) using the **Craya–Herring / Waleffe (1992) helical eigenbasis**.

### 4.1 Helical Basis Construction
For each wavevector $q \in \{k, \ell, m\}$ with $|k| < |\ell| < |m|$ and $k + \ell = m$, let $\mathbf{h}_{s_q}(q)$ ($s_q \in \{+1, -1\}$) be the complex helical unit vector perpendicular to $q$ satisfying:
$$i q \times \mathbf{h}_{s_q}(q) = s_q |q| \mathbf{h}_{s_q}(q), \qquad \mathbf{h}_{s_q}(-q) = \overline{\mathbf{h}_{s_q}(q)}, \qquad |\mathbf{h}_{s_q}(q)|^2 = 1.$$
Consider a single helical triad with amplitudes $u_k(t), u_\ell(t), u_m(t) \in \mathbb{C}$ and vorticity amplitudes $\omega_k(t) = s_k |k| u_k(t)$, $\omega_\ell(t) = s_\ell |\ell| u_\ell(t)$, $\omega_m(t) = s_m |m| u_m(t)$:
$$u(x,t) = \sum_{q \in \{k, \ell, -m\}} u_q(t)\mathbf{h}_{s_q}(q) e^{i q \cdot x} + \text{c.c.}$$
Projected onto the triad $(k, \ell, -m)$ (with $u_p = \overline{u_m}$ for $p = -m$, $s_p = s_m$), the exact viscous Navier–Stokes equations reduce to the **Minimal 3-Mode Triad ODE System** (`EXACT_IDENTITY`):
$$\boxed{
\begin{aligned}
\dot{\omega}_k + \nu |k|^2 \omega_k &= g_{k\ell m} \frac{s_k |k|}{s_\ell |\ell| s_m |m|} (s_\ell |\ell| - s_m |m|) \, \overline{\omega_\ell} \, \omega_m, \\
\dot{\omega}_\ell + \nu |\ell|^2 \omega_\ell &= g_{k\ell m} \frac{s_\ell |\ell|}{s_m |m| s_k |k|} (s_m |m| - s_k |k|) \, \omega_m \, \overline{\omega_k}, \\
\dot{\omega}_m + \nu |m|^2 \omega_m &= g_{k\ell m} \frac{s_m |m|}{s_k |k| s_\ell |\ell|} (s_k |k| - s_\ell |\ell|) \, \omega_k \, \omega_\ell,
\end{aligned}
}$$
where $g_{k\ell m} := \frac{1}{2}\operatorname{Re}\big[(\mathbf{h}_{s_k}(k) \times \mathbf{h}_{s_\ell}(\ell)) \cdot \overline{\mathbf{h}_{s_m}(m)}\big]$ is the geometric triad coupling coefficient (choosing the relative static phase such that the interaction coefficient is real).

### 4.2 Exact Conservation Laws and Enstrophy Production in the Minimal Triad (`EXACT_IDENTITY`)
Define the modal kinetic energies $E_q := \frac{1}{2}|u_q|^2 = \frac{|\omega_q|^2}{2|q|^2}$, modal enstrophies $\Omega_q := \frac{1}{2}|\omega_q|^2 = |q|^2 E_q$, and modal helicities $H_q := s_q |q| |u_q|^2 = 2 s_q |q| E_q$ for $q \in \{k, \ell, m\}$, and define the cubic triad correlation:
$$C_{k\ell m}(t) := g_{k\ell m} \operatorname{Re}\big(u_k(t) u_\ell(t) \overline{u_m(t)}\big) = \frac{g_{k\ell m}}{s_k s_\ell s_m |k||\ell||m|} \operatorname{Re}\big(\omega_k(t) \omega_\ell(t) \overline{\omega_m(t)}\big).$$
Then the modal energy, helicity, and enstrophy rates satisfy:
$$\dot{E}_k + 2\nu |k|^2 E_k = (s_\ell |\ell| - s_m |m|) C_{k\ell m}, \qquad \dot{E}_\ell + 2\nu |\ell|^2 E_\ell = (s_m |m| - s_k |k|) C_{k\ell m}, \qquad \dot{E}_m + 2\nu |m|^2 E_m = (s_k |k| - s_\ell |\ell|) C_{k\ell m}.$$
From these equations, three exact structural laws follow immediately:
1. **Exact Inviscid Energy Conservation**:
   $$(s_\ell |\ell| - s_m |m|) + (s_m |m| - s_k |k|) + (s_k |k| - s_\ell |\ell|) = 0 \implies \frac{d}{dt}(E_k + E_\ell + E_m)\Big|_{\nu=0} = 0.$$
2. **Exact Inviscid Helicity Conservation**:
   $$s_k |k|(s_\ell |\ell| - s_m |m|) + s_\ell |\ell|(s_m |m| - s_k |k|) + s_m |m|(s_k |k| - s_\ell |\ell|) = 0 \implies \frac{d}{dt}(H_k + H_\ell + H_m)\Big|_{\nu=0} = 0.$$
3. **Non-Zero Enstrophy Creation Rate ($P_{\rm triad}$) and Forward Flux $\Pi_Q^{\omega,\rm tot}$**:
   Multiplying the energy rates by $|q|^2$ gives the modal enstrophy rates $\dot{\Omega}_q + 2\nu |q|^2 \Omega_q = \Gamma_q C_{k\ell m}$ with:
   $$\Gamma_k = |k|^2(s_\ell |\ell| - s_m |m|), \qquad \Gamma_\ell = |\ell|^2(s_m |m| - s_k |k|), \qquad \Gamma_m = |m|^2(s_k |k| - s_\ell |\ell|).$$
   Summing over $\{k, \ell, m\}$ yields the **Exact Triad Vortex-Stretching Enstrophy Production** (`EXACT_IDENTITY`):
   $$\boxed{P_{\rm triad}(t) = \Gamma_k + \Gamma_\ell + \Gamma_m = \Big(|k|^2(s_\ell |\ell| - s_m |m|) + |\ell|^2(s_m |m| - s_k |k|) + |m|^2(s_k |k| - s_\ell |\ell|)\Big) C_{k\ell m}(t) \neq 0,}$$
   and when $k, \ell \in \mathcal{C}_{\le Q}$ and $m \in \mathcal{C}_{>Q}$, the exact forward nonlinear enstrophy transfer across $2^Q$ into the high mode $m$ is:
   $$\boxed{\Pi_Q^{\omega,\rm tot}(t) = \Gamma_m C_{k\ell m}(t) = |m|^2(s_k |k| - s_\ell |\ell|) C_{k\ell m}(t).}$$

---

## 5. Helicity Alignment and Beltrami Suppression (Section 22)

The minimal triad formula $\Pi_Q^{\omega,\rm tot}(t) = |m|^2(s_k |k| - s_\ell |\ell|) C_{k\ell m}(t)$ exposes the exact role of helicity $H(t) = \int_{\mathbb{T}_L^3} u \cdot \omega\,dx$:
1. **Resonant Same-Helicity Suppression on Spheres ($s_k = s_\ell = s, \, |k| = |\ell|$)**:
   When two interacting modes have the **same helicity sign** ($s_k = s_\ell = s$) and lie on the **same wavenumber sphere** ($|k| = |\ell| = \lambda$), the flow $u_k + u_\ell$ is an exact Beltrami eigenfield ($\omega = s\lambda u$, $u \times \omega = 0$). Accordingly, the coupling factor $s_k |k| - s_\ell |\ell| = s\lambda - s\lambda = 0$ vanishes identically, so $\dot{\omega}_m = 0$ and $\Pi_Q^{\omega,\rm tot}(t) \equiv 0$.
2. **Opposite-Helicity Enhancement ($s_k = +1, \, s_\ell = -1$ — Waleffe Class B / Forward Cascade Triads)**:
   When the two low-frequency modes have **opposite helicity signs** ($s_k = +1, s_\ell = -1$), the prefactor reaches its maximum magnitude:
   $$s_k |k| - s_\ell |\ell| = |k| + |\ell| > 0 \implies \Gamma_m = |m|^2(|k| + |\ell|) > 0!$$
   Even when $|k| = |\ell| = \lambda$ (where $H(t_0) = 2\lambda(E_k - E_\ell) = 0$ for equal amplitudes $E_k = E_\ell$, as in the Taylor–Green vortex!), opposite-helicity modes interact maximally ($\Gamma_m = 2\lambda |m|^2 > 0$), driving immediate forward enstrophy transfer into $|m| = |k + \ell| \in \mathcal{C}_{Q+1}$ while having $H(t_0) = 0$ and $P(t_0) = 0$!
3. **Why Microscopic Triad Transfer Oscillates (Phase Reversal Barrier)**:
   In the inviscid 3-mode triad with $s_k = +1, s_\ell = -1, s_m = +1$, $E_m(t)$ obeys the Jacobi elliptic pendulum equation $\ddot{E}_m = -A E_m^2 + B E_m + C$. Thus $C_{k\ell m}(t)$ is positive on $[t_0, t_0 + T_{\rm half})$ (forward transfer $\Pi_Q^{\omega,\rm tot} > 0$) and then reverses sign on $(t_0 + T_{\rm half}, t_0 + 2T_{\rm half})$ (inverse backscatter $\Pi_Q^{\omega,\rm tot} < 0$). Viscosity $\nu |m|^2$ damps the high mode during its positive half-cycle, making single-step transfer irreversible in energy loss, but **preventing a single triad from autonomously sustaining unbounded enstrophy growth**.
