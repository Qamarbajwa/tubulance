# TP2-G4-A3-R1: EXIT-TUBE AND RELATIVE-QV-DENSITY CORRECTION REPORT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A3-R1`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.1  
**Baseline State:** `TP2-G4-A3 = ACCEPTED_CANONICAL_WITH_REFORMULATION`  
**Date:** 2026-08-25T22:24:00Z  

---

## 1. Executive Summary & Purpose of A3-R1

This bounded correction gate resolves three mathematical refinements in the accepted `TP2-G4-A3` framework before Milestone `TP2-G4-A4` is executed:

1. **Brownian Exit-Tube Boundary Correction**: The interval $[-\frac{\pi}{4k}, \frac{\pi}{4k}]$ contained the zero-gradient point $y = 0$ ($G = J_\omega = 0$), where $\eta$ is undefined. We replace it with the strictly positive quadrant interval $I = [\frac{\pi}{8k}, \frac{3\pi}{8k}]$, where $|\sin(ky)| \ge \sin(\frac{\pi}{8}) > 0$ and $\cos(ky) \ge \cos(\frac{3\pi}{8}) > 0$ simultaneously. This rigorously establishes positive Brownian tube survival $\mathbb{P}(\mathcal{E}_{\text{surv}}) > 0$ with $h_\tau \ge c_h A^2 > 0$ on the entire duration $[0, L]$.
2. **Conservative Riesz Wording Qualification**: Replaced all remaining absolute "iff" assertions with the canonical sufficient condition: Persistent spectral isolation supplies the canonical sufficient Riesz-contour condition for smoothly tracking a spectral cluster. Loss of isolation destroys the canonical contour separation, but special crossing systems may still admit smooth selections.
3. **Fundamental Relative QV Density $\Xi$ and Domain Taxonomy for $\Theta$**:
   - $\Theta = \frac{\mathcal{A}_{\text{grad}}}{\mathcal{A}_\omega} = \frac{\|D J_\omega\|_F^2 / \|J_\omega\|_F^2}{|D\omega|^2 / |\omega|^2}$ is undefined when $J_\omega = 0$.
   - We define the **Primary Relative QV Density**:
     \[
     \boxed{ \Xi := \frac{\|D J_\omega\|_F^2}{|D \omega|^2} } \quad \text{whenever } \omega \neq 0.
     \]
     If $\omega \neq 0$ and $J_\omega = 0$, then $\Xi = 0$ without ambiguity.
   - On the regular domain ($\omega \neq 0, J_\omega \neq 0$), $\Xi \equiv \kappa_\omega^2 \Theta$, where $\kappa_\omega^2 = \frac{\|J_\omega\|_F^2}{|\omega|^2}$.
   - The fundamental stochastic Cauchy rate identity is formulated directly as:
     \[
     \boxed{ \partial_s \ln \chi_s = \frac{Q_s}{S_s} = 2\nu \mathbb{E}_{\mu_s}\left[ \Xi \right] }, \quad d\mu_s = \frac{|Z_s|^2}{S_s} d\mathbb{P}.
     \]

---

## 2. Rigorous Exit-Tube Proof Repair

Let $u_A(x, y, z, t) = (A e^{-\nu k^2 t} \sin(ky), 0, 0)$.
Let $I := [\frac{\pi}{8k}, \frac{3\pi}{8k}] \subset \mathbb{T}$.
On this compact interval:
\[
\sin(ky) \ge \sin\left(\frac{\pi}{8}\right) =: c_1 > 0, \quad \cos(ky) \ge \cos\left(\frac{3\pi}{8}\right) =: c_2 > 0.
\]
Choose the terminal label $y_0 = \frac{\pi}{4k} \in \operatorname{int}(I)$.

### 2.1 Brownian Tube Survival Event
Define the Brownian tube survival event:
\[
\mathcal{E}_{\text{tube}} := \left\{ A_{T-\tau}^y \in I \quad \forall \tau \in [0, L] \right\} = \left\{ y_0 + \sqrt{2\nu} \widetilde{B}_\tau^y \in \left[\frac{\pi}{8k}, \frac{3\pi}{8k}\right] \quad \forall \tau \in [0, L] \right\}.
\]
By standard 1D Brownian exit-time theory on a bounded interval, $\mathbb{P}(\mathcal{E}_{\text{tube}}) =: p_{\text{tube}} > 0$.

### 2.2 Strict Positivity of $h_\tau$ and Monotonicity of $\beta(\tau)$
Conditioned on $\mathcal{E}_{\text{tube}}$, for all $\tau \in [0, L]$:
1. **Zero-Gradient Exclusion**:
   \[
   h_\tau = \|J_\omega(A_{T-\tau}, T-\tau)\|_F^2 = k^4 A^2 e^{-2\nu k^2 (T-\tau)} \sin^2(k A_{T-\tau}^y) \ge k^4 A^2 e^{-2\nu k^2 T} c_1^2 =: c_h A^2 > 0.
   \]
   Thus $h_\tau > 0$ holds strictly on $[0, L]$, and $\eta_A(\tau)$ is everywhere well-defined.
2. **Strictly Positive Drift**:
   \[
   \beta'(\tau) = k e^{-\nu k^2 (T-\tau)} \cos(k A_{T-\tau}^y) \ge k e^{-\nu k^2 T} c_2 =: c_\beta > 0.
   \]
   Integrating from $\tau = 0$:
   \[
   \beta(\tau) \ge c_\beta \tau \quad \forall \tau \in [0, L].
   \]

### 2.3 Exact Residence Duration Bound
Let $a_\varepsilon := \frac{1 - \varepsilon}{\sqrt{\varepsilon}}$.
The condition $\eta_A(\tau) \le \varepsilon$ is equivalent to $|A \beta(\tau)| \ge a_\varepsilon$.
Since $\beta(\tau) \ge c_\beta \tau$, this is satisfied whenever $\tau \ge \tau_A := \frac{a_\varepsilon}{A c_\beta}$.
For any target duration $L > 0$ and any tolerance $\delta \in (0, L)$, choose:
\[
A \ge \frac{a_\varepsilon}{c_\beta \delta}.
\]
Then $\tau_A \le \delta$, and $\eta_A(\tau) \le \varepsilon$ for all $\tau \in [\delta, L]$.
Thus on the event $\mathcal{E}_{\text{tube}}$:
\[
\Delta \tau_{\text{res}}(\varepsilon) \ge L - \delta.
\]
Since $\mathbb{P}(\mathcal{E}_{\text{tube}}) > 0$:
\[
\boxed{ \mathbb{P}\left( \Delta \tau_{\text{res}}(\varepsilon) \ge L - \delta \right) > 0 }.
\]
$$\boxed{ \text{Ratified Scope: Rules out any universal, data-independent deterministic upper bound on low-}\eta \text{ persistence.} }$$

---

## 3. Rigorous Domain Taxonomy for Orientation Ratios

We establish a strict 3-state domain taxonomy to avoid $0/0$ or $0 \times \text{undefined}$ algebraic errors:

| State Taxonomy Code | Mathematical Condition | Status of $\Xi$ | Status of $\Theta$ | Status of $\kappa_\omega^2 \Theta$ |
|---|---|---|---|---|
| `REGULAR_ORIENTATION_STATE` | $\omega \neq 0$ and $J_\omega \neq 0$ | $\Xi = \frac{\|D J_\omega\|^2}{|D\omega|^2} > 0$ | $\Theta = \frac{\mathcal{A}_{\text{grad}}}{\mathcal{A}_\omega} > 0$ | $\Xi \equiv \kappa_\omega^2 \Theta$ |
| `ZERO_GRADIENT_STATE` | $\omega \neq 0$ and $J_\omega = 0$ | $\Xi \equiv 0$ | **UNDEFINED** ($0/0$) | **UNDEFINED** ($0 \times \text{undef}$) |
| `ZERO_VORTICITY_STATE` | $\omega = 0$ ($|Z_s|^2 = 0$) | Zero Cauchy measure ($d\mu_s = 0$) | Irrelevant to rate | Irrelevant to rate |

---

## 4. Fundamental Relative QV Density $\Xi$ and Exact Rate Identity

The **Primary Relative QV Density** is defined everywhere on $\{\omega \neq 0\}$ as:
\[
\boxed{ \Xi := \frac{\|D_s J_\omega(A_s, s)\|_F^2}{|D_s \omega(A_s, s)|^2} }.
\]
Because $D_s \in SL(3, \mathbb{R})$ is strictly invertible, $|D_s \omega| > 0$ whenever $\omega \neq 0$.

### 4.1 Direct Stochastic Rate Identity
Let $Z_s = D_s \omega(A_s, s)$, $S_s = \mathbb{E}[|Z_s|^2]$, $Q_s = 2\nu \mathbb{E}[\|D_s J_\omega\|_F^2]$.
Under the Cauchy-energy weighted probability measure $d\mu_s := \frac{|Z_s|^2}{S_s} d\mathbb{P}$:
\[
\frac{Q_s}{S_s} = \frac{2\nu \mathbb{E}[\|D_s J_\omega\|_F^2]}{S_s} = 2\nu \int_{\{|Z_s| > 0\}} \frac{\|D_s J_\omega\|_F^2}{|Z_s|^2} \frac{|Z_s|^2}{S_s} d\mathbb{P} = 2\nu \mathbb{E}_{\mu_s}\left[ \Xi \right].
\]
Combined with the accepted Gate `TP2-G3` identity $\frac{Q_s}{S_s} \equiv \partial_s \ln \chi_s$:
\[
\boxed{ \partial_s \ln \chi_s = 2\nu \mathbb{E}_{\mu_s}\left[ \Xi \right] }.
\]
On the regular sub-domain ($\omega \neq 0, J_\omega \neq 0$), this factors as:
\[
\Xi = \kappa_\omega^2 \Theta, \quad \kappa_\omega^2 = \frac{\|J_\omega\|_F^2}{|\omega|^2}, \quad \Theta = \frac{\|D J_\omega\|_F^2 / \|J_\omega\|_F^2}{|D\omega|^2 / |\omega|^2}.
\]

### 4.2 Dimensional Scaling Verification
- $[\Xi] = \frac{[J_\omega]^2}{[\omega]^2} = \frac{\lambda^6}{\lambda^4} = \lambda^2$ (velocity gradient / stretching rate dimension).
- $[\kappa_\omega^2] = \lambda^2$.
- $[\Theta] = \lambda^0$ (dimensionless orientation factor).
- $[\partial_s \ln \chi_s] = \lambda^2$.
- The identity is **unconditionally scale-critical and dimensionally exact**.
