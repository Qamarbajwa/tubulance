# TP2-G4-A3: STOCHASTIC ORIENTATION PERSISTENCE NO-GO, VORTICITY-RELEVANT DEFORMATION, AND RELATIVE QV EFFICIENCY

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A3`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.1  
**Date:** 2026-08-25T22:11:00Z  

---

## 1. Executive Summary

Milestone `TP2-G4-A3` delivers three fundamental mathematical results for the stochastic Cauchy Navier–Stokes program:

1. **Analytical Persistence No-Go (`NS-OBS-010`)**: For the exact smooth periodic shear Navier–Stokes family on $\mathbb{T}^3$, we prove that the low-orientation occupation time $\mathcal{O}_\varepsilon^A(L) \to L$ almost surely as amplitude $A \to \infty$, and that consecutive low-$\eta$ residence times $\Delta \tau_{\text{res}}(\varepsilon)$ can be arbitrarily long with positive Brownian probability. This rigorously rules out any universal, data-independent upper bound on low-$\eta$ persistence.
2. **Physical Meaning of Low $\eta$**: The exact periodic shear flow is globally smooth and non-singular for all time, yet exhibits arbitrarily large deformation ($\sigma_1 \to \infty$), arbitrarily small orientation efficiency ($\eta \to 0$), and long low-$\eta$ occupation. This proves that generic deformation magnitude includes non-stretching directions that do not amplify vorticity:
   $$\boxed{ \text{LOW\_ETA\_PLUS\_LARGE\_GENERIC\_DEFORMATION\_NOT\_BLOWUP\_SPECIFIC} }$$
3. **Vorticity-Relevant Deformation & Exact Rate Decomposition**: We introduce the **Relative Orientation Efficiency** $\Theta := \mathcal{A}_{\text{grad}} / \mathcal{A}_\omega$, where $\mathcal{A}_\omega = |D\omega|^2/|\omega|^2$ is the vorticity-stretching factor and $\mathcal{A}_{\text{grad}} = \|D J_\omega\|_F^2 / \|J_\omega\|_F^2$. We prove the exact, scale-critical quadratic variation rate decomposition:
   \[
   \boxed{ R_Q(s) := \frac{Q_s}{S_s} \equiv \partial_s \ln \chi_s = 2\nu \mathbb{E}_{\mu_s}\left[ \kappa_\omega^2 \Theta \right] },
   \]
   where $d\mu_s = \frac{|Z_s|^2}{S_s} d\mathbb{P}$ is the Cauchy-energy weighted probability measure and $\kappa_\omega^2 = \frac{\|J_\omega\|_F^2}{|\omega|^2}$ scales precisely as $\lambda^2$.

---

## 2. Phase 1: Inherited Riesz Projector Scope Correction

We formally qualify the Riesz projector differentiability condition inherited from `TP2-G4-A2-R1`:
- **Corrected Scope**: An isolated spectral cluster $\Lambda_\alpha \subset \sigma(\Gamma)$ admits the canonical Riesz contour projector $\mathcal{P}_\alpha = \frac{1}{2\pi i} \oint_{\mathcal{C}_\alpha} (z I - \Gamma)^{-1} dz$, which is analytic/smooth under $C^\infty$ matrix perturbations while isolation from the rest of the spectrum persists.
- **Boundaries**: Loss of spectral isolation destroys the canonical contour separation. However, certain special analytic matrix families with eigenvalue crossings can still admit smooth subspace selections through a crossing.
- **Ratification**: We do **not** claim "No spectral gap $\implies$ no smooth projector can exist". We claim only that the canonical Riesz contour integral requires isolation.

---

## 3. Phase 2: Exact Periodic Shear Solution Family Analysis

Consider the unforced 3D Navier–Stokes solution on $\mathbb{T}^3 = [0, 2\pi)^3$:
\[
u_A(x, y, z, t) = \left( A e^{-\nu k^2 t} \sin(k y), 0, 0 \right), \quad p \equiv 0.
\]
Because $(u \cdot \nabla)u = 0$, this is an exact smooth solution for all $t \ge 0$.

### 3.1 Exact Stochastic Backward Flow and Deformation
The backward stochastic trajectory $A_{s, T}(x) = (A_s^x, A_s^y, A_s^z)$ satisfies $d A_s = -u(A_s, s) ds + \sqrt{2\nu} d\widetilde{B}_s$.
Under forwardized lookback time $\tau = T - s \in [0, T]$:
\[
A_{T-\tau}^y = y + \sqrt{2\nu} \widetilde{B}_\tau^y,
\]
which is a pure 1D Brownian motion on $\mathbb{T}$ completely independent of the $x$-shear amplitude $A$.

The backward deformation tensor $D_\tau = [J_{A_{T-\tau}}]^{-1}$ satisfies:
\[
D_\tau = I + \alpha_A(\tau) E_{12}, \quad E_{12} = e_1 \otimes e_2,
\]
where the shear deformation factor factorizes cleanly as $\alpha_A(\tau) = A \beta(\tau)$, with:
\[
\beta(\tau) := \int_0^\tau e^{-\nu k^2 (T - r)} k \cos\left( k (y + \sqrt{2\nu} \widetilde{B}_r^y) \right) dr.
\]
Crucially, **$\beta(\tau)$ is a random process completely independent of $A$**.

### 3.2 Metric Tensor and Singular Spectrum
The right Cauchy–Green tensor is:
\[
\Gamma_\tau = D_\tau^T D_\tau = \begin{pmatrix} 1 & \alpha \\ \alpha & 1 + \alpha^2 & 0 \\ 0 & 0 & 1 \end{pmatrix}.
\]
The eigenvalues of $\Gamma_\tau$ (squared singular values of $D_\tau$) are:
\[
\sigma_1^2 = \left( \frac{\sqrt{\alpha^2 + 4} + |\alpha|}{2} \right)^2, \quad \sigma_2^2 = 1, \quad \sigma_3^2 = \sigma_1^{-2} = \left( \frac{\sqrt{\alpha^2 + 4} - |\alpha|}{2} \right)^2.
\]

### 3.3 Vorticity Gradient & Orientation Efficiency $\eta_A$
The vorticity vector is $\omega = (0, 0, -k A e^{-\nu k^2 t} \cos(k y))$.
The vorticity gradient tensor is:
\[
G = J_\omega = k^2 A e^{-\nu k^2 t} \sin(k y) E_{32}, \quad E_{32} = e_3 \otimes e_2.
\]
Because $E_{12} E_{32} = (e_1 \otimes e_2)(e_3 \otimes e_2) = (e_2 \cdot e_3) E_{12} = 0$, we have:
\[
D_\tau J_\omega = (I + \alpha E_{12}) J_\omega \equiv J_\omega \implies \|D_\tau J_\omega\|_F^2 = \|J_\omega\|_F^2.
\]
Thus the gradient orientation factor is identically $\mathcal{A}_{\text{grad}} = 1$.
The orientation efficiency $\eta_A(\tau)$ is:
\[
\boxed{ \eta_A(\tau) = \frac{\mathcal{A}_{\text{grad}}}{\sigma_1^2} = \sigma_1^{-2} = \exp\left[ -2 \operatorname{asinh}\left( \frac{|A \beta(\tau)|}{2} \right) \right] }.
\]
Solving $\eta_A(\tau) \le \varepsilon$ for $\varepsilon \in (0, 1)$:
\[
\sigma_1 \ge \frac{1}{\sqrt{\varepsilon}} \iff \frac{\sqrt{(A\beta)^2 + 4} + |A\beta|}{2} \ge \frac{1}{\sqrt{\varepsilon}} \iff \boxed{ |A \beta(\tau)| \ge \frac{1 - \varepsilon}{\sqrt{\varepsilon}} }.
\]

---

## 4. Phase 3: Analytical Occupation-Time Limit Proof

Let $h_\tau = \|G(A_{T-\tau}, T-\tau)\|_F^2 = k^4 A^2 e^{-2\nu k^2 (T-\tau)} \sin^2(k A_{T-\tau}^y)$.
Define the low-$\eta$ occupation time on $[0, L]$:
\[
\mathcal{O}_\varepsilon^A(L) := \int_0^L \mathbf{1}_{\{h_\tau > 0 \text{ and } \eta_A(\tau) \le \varepsilon\}} d\tau.
\]

### Theorem 1 (Occupation Limit Theorem)
For any fixed $\varepsilon \in (0, 1)$ and finite lookback horizon $L > 0$:
\[
\lim_{A \to \infty} \mathcal{O}_\varepsilon^A(L) = L \quad \text{almost surely},
\]
and consequently:
\[
\lim_{A \to \infty} \mathbb{E}[\mathcal{O}_\varepsilon^A(L)] = L.
\]

### Proof (Itemized Step-by-Step):
1. **Zero-Gradient Set has Measure Zero**: For each $\tau \in (0, L]$, $A_{T-\tau}^y$ has a non-degenerate Gaussian distribution on $\mathbb{T}$. The set of zeros of $\sin(k A_{T-\tau}^y)$ is a discrete lattice $\frac{\pi}{k} \mathbb{Z}$. Thus $\mathbb{P}(h_\tau = 0) = 0$. By Fubini's theorem:
   \[
   \mathbb{E}\left[ \int_0^L \mathbf{1}_{\{h_\tau = 0\}} d\tau \right] = \int_0^L \mathbb{P}(h_\tau = 0) d\tau = 0 \implies \operatorname{Leb}(\{ \tau \in [0, L] : h_\tau = 0 \}) = 0 \quad \text{a.s.}
   \]
2. **Absolute Continuity of $\beta(\tau)$**: The sample path $r \mapsto A_{T-r}^y$ is continuous almost surely. Hence $r \mapsto \cos(k A_{T-r}^y)$ is continuous. Thus $\beta(\tau) = \int_0^\tau k e^{-\nu k^2 (T-r)} \cos(k A_{T-r}^y) dr$ is $C^1$ (hence absolutely continuous) on $[0, L]$ with derivative:
   \[
   \beta'(\tau) = k e^{-\nu k^2 (T-\tau)} \cos(k A_{T-\tau}^y).
   \]
3. **Zeros of Derivative have Measure Zero**: By the same Gaussian argument, $\mathbb{P}(\beta'(\tau) = 0) = \mathbb{P}(\cos(k A_{T-\tau}^y) = 0) = 0$. Thus $\operatorname{Leb}(\{ \tau \in [0, L] : \beta'(\tau) = 0 \}) = 0$ almost surely.
4. **Level Set of Absolutely Continuous Functions**: A foundational theorem of real analysis states that if $f: [0, L] \to \mathbb{R}$ is absolutely continuous, then $f'(\tau) = 0$ for Lebesgue-almost-every $\tau$ on the level set $E_0 = \{ \tau \in [0, L] : f(\tau) = 0 \}$.
5. **Zero Set of $\beta$ has Measure Zero**: Since $E_0 \subset \{ \tau : \beta'(\tau) = 0 \} \cup N$ where $\operatorname{Leb}(N) = 0$, and $\operatorname{Leb}(\{ \tau : \beta'(\tau) = 0 \}) = 0$ a.s., we conclude:
   \[
   \operatorname{Leb}(\{ \tau \in [0, L] : \beta(\tau) = 0 \}) = 0 \quad \text{almost surely}.
   \]
6. **Pointwise Convergence**: For almost every $\tau \in [0, L]$, both $h_\tau > 0$ and $|\beta(\tau)| > 0$. Therefore:
   \[
   \lim_{A \to \infty} |A \beta(\tau)| = \infty > \frac{1 - \varepsilon}{\sqrt{\varepsilon}} \implies \lim_{A \to \infty} \eta_A(\tau) = 0 < \varepsilon.
   \]
   Thus $\lim_{A \to \infty} \mathbf{1}_{\{h_\tau > 0 \text{ and } \eta_A(\tau) \le \varepsilon\}} = 1$ for almost every $\tau \in [0, L]$.
7. **Dominated Convergence**: Since the integrand is bounded by 1 on the finite interval $[0, L]$, the Dominated Convergence Theorem implies $\mathcal{O}_\varepsilon^A(L) \to L$ almost surely and $\mathbb{E}[\mathcal{O}_\varepsilon^A(L)] \to L$. $\blacksquare$

---

## 5. Phase 4: Exit-Time Persistence No-Go

Let $\tau_{\text{enter}}(\varepsilon) := \inf\{\tau \ge 0 : \eta_A(\tau) \le \varepsilon\}$ and $\tau_{\text{exit}}(\varepsilon) := \inf\{\tau > \tau_{\text{enter}} : \eta_A(\tau) > \varepsilon\}$.
The consecutive residence duration in $\mathcal{L}_\varepsilon$ is $\Delta \tau_{\text{res}}(\varepsilon) := \tau_{\text{exit}}(\varepsilon) - \tau_{\text{enter}}(\varepsilon)$.

### Theorem 2 (Exit-Time No-Go)
For any finite target duration $L > 0$, any tolerance $\delta \in (0, L)$, and any $\varepsilon \in (0, 1)$, there exists a finite amplitude $A < \infty$ such that:
\[
\boxed{ \mathbb{P}\left( \Delta \tau_{\text{res}}(\varepsilon) \ge L - \delta \right) > 0 }.
\]

### Proof:
Choose a compact spatial interval $I = [-\frac{\pi}{4k}, \frac{\pi}{4k}] \subset \mathbb{T}$ where $\cos(k y) \ge \frac{\sqrt{2}}{2} =: c_2 > 0$ and $|\sin(k y)| \le \frac{\sqrt{2}}{2}$.
Let $\mathcal{E}_{\text{surv}}$ be the Brownian tube event:
\[
\mathcal{E}_{\text{surv}} := \left\{ A_{T-r}^y \in I \quad \forall r \in [0, L] \right\}.
\]
By the non-degeneracy of Brownian motion on a finite time horizon, $\mathbb{P}(\mathcal{E}_{\text{surv}}) =: p_{\text{surv}} > 0$.
Conditioned on $\mathcal{E}_{\text{surv}}$, for all $\tau \in [0, L]$:
\[
\beta'(\tau) = k e^{-\nu k^2 (T-\tau)} \cos(k A_{T-\tau}^y) \ge k e^{-\nu k^2 T} c_2 =: c_3 > 0.
\]
Integrating from $\tau = 0$:
\[
\beta(\tau) \ge c_3 \tau \quad \forall \tau \in [0, L].
\]
For any $\tau \ge \delta > 0$, we have $\beta(\tau) \ge c_3 \delta > 0$.
Choose $A \ge \frac{1 - \varepsilon}{c_3 \delta \sqrt{\varepsilon}}$. Then for all $\tau \in [\delta, L]$:
\[
|A \beta(\tau)| \ge A c_3 \delta \ge \frac{1 - \varepsilon}{\sqrt{\varepsilon}} \implies \eta_A(\tau) \le \varepsilon.
\]
Thus on the event $\mathcal{E}_{\text{surv}}$, the trajectory enters $\mathcal{L}_\varepsilon$ before $\tau = \delta$ and does not exit before $\tau = L$, guaranteeing $\Delta \tau_{\text{res}}(\varepsilon) \ge L - \delta$.
Since $\mathbb{P}(\mathcal{E}_{\text{surv}}) > 0$, the probability is strictly positive. $\blacksquare$

$$\boxed{ \text{Negative Evidence: Rules out any universal deterministic upper bound } \Delta \tau_{\text{res}} \le T_* \text{ independent of initial data/amplitude.} }$$

---

## 6. Phase 5 & 6: Vorticity-Relevant Deformation & Relative Efficiency $\Theta$

### 6.1 Vorticity-Stretching Factor $\mathcal{A}_\omega$
For $\omega \neq 0$, decompose $\omega$ along the right singular vectors $v_i$ of $D$:
\[
r_i := \frac{|v_i \cdot \omega|^2}{|\omega|^2} \ge 0, \quad \sum_{i=1}^3 r_i = 1.
\]
The direct Cauchy stretching amplification of the vorticity vector is:
\[
\boxed{ \mathcal{A}_\omega := \frac{|D \omega|^2}{|\omega|^2} = \sum_{i=1}^3 r_i \sigma_i^2 }.
\]

### 6.2 Relative Orientation Efficiency $\Theta$
Define the **Relative Orientation Efficiency**:
\[
\boxed{ \Theta := \frac{\mathcal{A}_{\text{grad}}}{\mathcal{A}_\omega} = \frac{\|D J_\omega\|_F^2 / \|J_\omega\|_F^2}{|D \omega|^2 / |\omega|^2} = \frac{\sum_{i=1}^3 p_i \sigma_i^2}{\sum_{i=1}^3 r_i \sigma_i^2} }.
\]

### Properties of $\Theta$:
1. **Periodic Shear Calibration**: For periodic shear flows, $\omega \propto e_3$ (neutral direction $v_2$), so $r_2 = 1, r_1 = r_3 = 0 \implies \mathcal{A}_\omega = 1$. Since $\mathcal{A}_{\text{grad}} = 1$, we have $\boxed{\Theta = 1}$ identically.
2. **Domain of $\Theta$**: $\Theta \in (0, \infty)$.
   - $\Theta < 1$: Vorticity is stretched more strongly than its gradient ($|D\omega|^2 \gg \|D J_\omega\|^2$).
   - $\Theta = 1$: Exact balanced stretching between vorticity and its gradient.
   - $\Theta > 1$: Gradient is stretched more strongly than vorticity ($\|D J_\omega\|^2 \gg |D\omega|^2$).

---

## 7. Phase 7: Exact G3/G4 Rate Decomposition

Define the local spatial enstrophy density gradient ratio:
\[
\kappa_\omega^2 := \frac{\|J_\omega\|_F^2}{|\omega|^2} = \frac{\|\nabla \omega\|_F^2}{|\omega|^2}.
\]
Pathwise identity:
\[
\boxed{ \frac{\|D_s J_\omega\|_F^2}{|D_s \omega|^2} \equiv \kappa_\omega^2 \Theta }.
\]
Recall the Cauchy invariant $Z_s = D_s \omega(A_s, s)$ and the variance budget $S_s = \mathbb{E}[|Z_s|^2]$.
Define the **Cauchy-energy weighted probability measure**:
\[
d\mu_s := \frac{|Z_s|^2}{S_s} d\mathbb{P}.
\]
Then the stochastic quadratic variation rate $R_Q(s) := \frac{Q_s}{S_s}$ evaluates exactly to:
\[
R_Q(s) = \frac{2\nu \mathbb{E}[\|D_s J_\omega\|_F^2]}{\mathbb{E}[|Z_s|^2]} = 2\nu \int \frac{\|D_s J_\omega\|_F^2}{|Z_s|^2} \frac{|Z_s|^2}{S_s} d\mathbb{P} = 2\nu \mathbb{E}_{\mu_s}\left[ \frac{\|D_s J_\omega\|_F^2}{|D_s \omega|^2} \right].
\]
Using the accepted Gate `TP2-G3` identity $R_Q(s) \equiv \partial_s \ln \chi_s$:
\[
\boxed{ \partial_s \ln \chi_s = 2\nu \mathbb{E}_{\mu_s}\left[ \kappa_\omega^2 \Theta \right] }.
\]

### Parabolic Scaling Balance:
- $[\kappa_\omega^2] = \frac{[J_\omega]^2}{[\omega]^2} = \frac{\lambda^6}{\lambda^4} = \lambda^2$ (velocity gradient / stretching rate dimension).
- $[\Theta] = \frac{[\mathcal{A}_{\text{grad}}]}{[\mathcal{A}_\omega]} = \frac{\lambda^0}{\lambda^0} = \lambda^0$ (dimensionless geometric ratio).
- $[R_Q] = [\partial_s \ln \chi_s] = \lambda^2$.
- **Theorem**: The energy-weighted decomposition $\partial_s \ln \chi_s = 2\nu \mathbb{E}_{\mu_s}[\kappa_\omega^2 \Theta]$ is **dimensionally exact and scale-critical**.

---

## 8. Phase 9: Markov Generator & Hitting-Time Closure Audit

The pair $(\Gamma_s, H_s)$ does not form an autonomous Markov process because its drift and diffusion coefficients depend on the Eulerian velocity gradient $A(x, t)$ and strain gradient $\nabla S(x, t)$.

To formulate a well-posed generator, we must augment the state to $(Y_\tau, D_\tau)$, where $Y_\tau = A_{T-\tau}(x) \in \mathbb{T}^3$ and $D_\tau \in SL(3, \mathbb{R})$:
\[
d Y_\tau = u(Y_\tau, T-\tau) d\tau + \sqrt{2\nu} dW_\tau, \quad \frac{d D_\tau}{d\tau} = D_\tau A(Y_\tau, T-\tau).
\]
The time-inhomogeneous generator $\mathcal{L}_\tau$ acting on test functions $\Phi(y, D)$ is:
\[
\mathcal{L}_\tau \Phi = \nu \Delta_y \Phi + u(y, T-\tau) \cdot \nabla_y \Phi + \operatorname{tr}\left( [D A(y, T-\tau)]^T \nabla_D \Phi \right).
\]
- **Dykin/Feynman-Kac Representation**: Expected occupation times satisfy $w(y, D, \tau) = \mathbb{E}[\int_\tau^L \mathbf{1}_{\{\eta \le \varepsilon\}} dr]$ via the PDE $(\partial_\tau + \mathcal{L}_\tau) w = -\mathbf{1}_{\{\eta \le \varepsilon\}}$.
- **Closure Barrier**: The generator $\mathcal{L}_\tau$ contains the unknown Eulerian field $u(y, t)$ and its gradients. Thus, the hitting-time PDE is a **formal representation, not an a-priori regularity proof**.
- **Drift Falsification**: The hypothesis that Navier–Stokes provides an outward drift $\mathcal{L} \eta \ge c > 0$ is falsified by the periodic shear family, where $\mathcal{L} \eta_A(\tau) < 0$ during the entire initial transient as $|A\beta| \to \infty$.

---

## 9. Phase 10: Research Memory Update (`NS-OBS-010`)

We record a new structural obstruction:

- **Obstruction ID**: `NS-OBS-010`
- **Name**: `LOW_ETA_PERSISTENCE_NOT_UNIVERSALLY_EXCLUDED_BY_NAVIER_STOKES`
- **Description**: Exact smooth periodic shear flows on $\mathbb{T}^3$ prove that Navier–Stokes dynamics permit arbitrarily long occupation times ($\mathcal{O}_\varepsilon \to L$) and residence durations in low-$\eta$ states ($\eta \sim \sigma_1^{-2} \to 0$) without singularity formation.
- **Status of A3**: `REFORMULATED` (from blind persistence bounds to relative efficiency $\Theta$ and Cauchy energy-weighted rate decomposition).
