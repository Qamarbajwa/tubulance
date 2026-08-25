# TP2-G4-A2-R1: SPECTRAL-DEGENERACY, ZERO-GRADIENT, AND STOCHASTIC-ORIENTATION CORRECTION REPORT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2-R1`  
**Governance Standard:** Autonomous Project Runtime Governance Kernel v2.10.0  
**Baseline State:** `TP2-G4-A2 = ACCEPTED_CANONICAL_WITH_REFORMULATION`  
**Date:** 2026-08-25T20:56:00Z  

---

## 1. Executive Summary & Purpose of A2-R1

Before allowing Milestone `TP2-G4-A3` to inherit the orientation-weight framework, this bounded repair gate resolves three critical mathematical subtleties identified in the accepted `TP2-G4-A2` formulation:

1. **Qualification of Spectral Projector Differentiability**: The assertion that resolvent projectors make $p_\alpha$ and $\eta$ "smooth across all degeneracies" is restricted to **isolated spectral clusters** separated from their complement by a positive spectral gap, in accordance with Kato/Riesz perturbation theory.
2. **Rigorous Handling of the Zero-Gradient Singular State ($G = 0$)**: When $G = J_\omega = 0$, $H = G G^T = 0$ and $h = \operatorname{tr}(H) = 0$, making $M = H/h$, $p_i$, and $\eta$ algebraically undefined. We introduce globally well-defined unnormalized energy weights $q_i := \operatorname{tr}(P_i H) = \|v_i^T G\|^2 \ge 0$ with $\sum q_i = h$, establishing a strict 2-state taxonomy: `ORIENTATION_DEFINED_G_NONZERO` ($h > 0$) versus `ORIENTATION_UNDEFINED_G_ZERO` ($h = 0$).
3. **Stochastic Semimartingale Formulation**: Evaluated along backward Brownian paths $A_s(x)$, $G_s$, $H_s$, $q_i(s)$, and $p_i(s)$ are stochastic semimartingales, not differentiable deterministic sample paths. We derive the exact backward Itô SDEs for $H_s, q_i(s), p_i(s)$ and forwardize with $\tau = T - s$ before defining occupation and exit persistence times.

---

## 2. Spectral Projector Differentiability & Kato/Riesz Perturbation Bounds

Let $\Gamma_s = D_s^T D_s \in SL(3, \mathbb{R})$ have spectrum $\sigma(\Gamma_s) = \{\mu_1(s), \mu_2(s), \mu_3(s)\}$.

### 2.1 The Riesz Projector for an Isolated Spectral Cluster
Let $\Lambda_\alpha(s) \subset \sigma(\Gamma_s)$ be a cluster of eigenvalues (e.g. an exact or near degeneracy $\mu_1 \approx \mu_2$). Suppose $\Lambda_\alpha(s)$ is enclosed by a closed contour $\mathcal{C}_\alpha \subset \mathbb{C}$ that does not intersect $\sigma(\Gamma_s)$ and encloses no eigenvalues outside $\Lambda_\alpha(s)$. The spectral cluster projector:
\[
\mathcal{P}_\alpha(s) = \frac{1}{2\pi i} \oint_{\mathcal{C}_\alpha} (z I - \Gamma_s)^{-1} dz
\]
is analytic/smooth with respect to $s$ **if and only if the spectral gap $\operatorname{dist}(\Lambda_\alpha(s), \sigma(\Gamma_s) \setminus \Lambda_\alpha(s)) \ge \delta > 0$ remains strictly positive**.

### 2.2 Domain of Validity for Projector Equations
1. **Distinct Simple Eigenspaces**: When $\mu_i$ is simple and separated ($\operatorname{dist}(\mu_i, \sigma(\Gamma) \setminus \{\mu_i\}) > 0$), the 1D projector $P_i = v_i v_i^T$ satisfies:
   \[
   \partial_s P_i = \sum_{j \neq i} \frac{P_j (\partial_s \Gamma_s) P_i + P_i (\partial_s \Gamma_s) P_j}{\mu_i - \mu_j}.
   \]
2. **Coalescing/Degenerate Clusters**: When $\mu_1(s) = \mu_2(s) = \mu_{12}(s) \neq \mu_3(s)$, individual eigenvectors $v_1, v_2$ lose differentiability and uniqueness, but the 2D cluster projector $\mathcal{P}_{12} = I - P_3$ satisfies:
   \[
   \partial_s \mathcal{P}_{12} = \frac{P_3 (\partial_s \Gamma_s) \mathcal{P}_{12} + \mathcal{P}_{12} (\partial_s \Gamma_s) P_3}{\mu_{12} - \mu_3}.
   \]
3. **Triple Degeneracy / Global Multiplicity Change**: If $\mu_1 = \mu_2 = \mu_3 = 1$ ($\Gamma_s = I$), $\mathcal{P} = I \implies \partial_s \mathcal{P} = 0$. However, at a bifurcation point where a single eigenvalue splits into multiple branches, differentiability must be evaluated via directional derivatives or the reduced resolvent.

$$\boxed{ \text{Ratified Scope: Gauge-invariant cluster projectors remain smooth while the cluster remains spectrally isolated from its complement.} }$$

---

## 3. Zero-Gradient State & Unnormalized Weight Dynamics

Let $G = J_\omega$, $H = G G^T$, and $h = \operatorname{tr}(H) = \|G\|_F^2 = \|\nabla \omega\|_F^2$.

### 3.1 Unnormalized Energy Weights $q_i$
We define the **globally well-defined unnormalized orientation weights**:
\[
\boxed{ q_i := \operatorname{tr}(P_i H) = \operatorname{tr}(v_i v_i^T G G^T) = \|v_i^T G\|_2^2 \ge 0 }.
\]
Properties:
- $q_i \ge 0$ is globally defined for all $(x, t)$, even when $G = 0$.
- $\sum_{i=1}^3 q_i = \operatorname{tr}\left( \left(\sum P_i\right) H \right) = \operatorname{tr}(H) = h$.
- $Q_s = 2\nu \mathbb{E}\left[ \operatorname{tr}(\Gamma_s H(A_s, s)) \right] = 2\nu \mathbb{E}\left[ \sum_{i=1}^3 \sigma_i^2 q_i(A_s, s) \right]$.

### 3.2 Canonical State Taxonomy
| State Code | Condition | $H, q_i$ Status | $M, p_i, \eta$ Status | Physical Interpretation |
|---|---|---|---|---|
| `ORIENTATION_DEFINED_G_NONZERO` | $h = \|G\|_F^2 > 0$ | Defined ($h > 0$) | $M = H/h$, $p_i = q_i/h$, $\eta = \frac{\operatorname{tr}(\Gamma H)}{\lambda_{\max}(\Gamma) h}$ well-defined | Nontrivial spatial vorticity gradient |
| `ORIENTATION_UNDEFINED_G_ZERO` | $h = \|G\|_F^2 = 0$ | $H = 0$, $q_i = 0$, $D J_\omega = 0$ | **UNDEFINED ($0/0$)** | Spatially uniform vorticity ($J_\omega = 0$) |

$$\boxed{ \text{Vital Distinction: } Q_s > 0 \text{ in expectation does NOT imply } G(A_s, s) \neq 0 \text{ pathwise on every Brownian trajectory.} }$$

---

## 4. Basis-Invariant Orientation Efficiency $\eta$

For any state with $h = \operatorname{tr}(H) > 0$, the orientation efficiency is given basis-independently by:
\[
\boxed{ \eta := \frac{\operatorname{tr}(\Gamma_s H)}{\lambda_{\max}(\Gamma_s) \operatorname{tr}(H)} \in (0, 1] }.
\]
- In simple spectrum ($\sigma_1 > \sigma_2 > \sigma_3$):
  \[
  \eta = \frac{\sum_{i=1}^3 \sigma_i^2 q_i}{\sigma_1^2 h} = \sum_{i=1}^3 p_i \left( \frac{\sigma_i}{\sigma_1} \right)^2 = p_1 + p_2 \left( \frac{\sigma_2}{\sigma_1} \right)^2 + p_3 \left( \frac{\sigma_3}{\sigma_1} \right)^2.
  \]
- In double degeneracy ($\sigma_1 = \sigma_2 = K > \sigma_3 = K^{-2}$):
  \[
  \eta = \frac{K^2 q_{12} + K^{-4} q_3}{K^2 h} = \frac{q_{12}}{h} + K^{-6} \frac{q_3}{h} = p_{12} + (1 - p_{12}) K^{-6},
  \]
  which depends strictly on the gauge-invariant cluster weight $p_{12} = \operatorname{tr}(\mathcal{P}_{12} M)$ without resolving $v_1$ vs $v_2$.

### 4.1 Differentiability Classification of $\eta$
- `ETA_VALUE_WELL_DEFINED`: Holds whenever $h > 0$.
- `ETA_CLASSICAL_DERIVATIVE_SIMPLE_TOP`: $\eta$ is classically differentiable when $\sigma_1 > \sigma_2$.
- `ETA_NONSIMPLE_TOP_REQUIRES_SUBDIFFERENTIAL`: When $\sigma_1 = \sigma_2$, $\lambda_{\max}(\Gamma)$ is Lipschitz but possesses non-differentiable directional derivatives at eigenvalue crossings.
- `ETA_UNDEFINED_G_ZERO`: Undefined when $h = 0$.

---

## 5. Backward Itô SDEs for Stochastic Orientation Dynamics

Let $A_s(x)$ be the backward Brownian trajectory $d A_s = -u(A_s, s) ds + \sqrt{2\nu} d\widetilde{B}_s$.
Recall the deterministic advection-diffusion operator:
\[
(D_t - \nu \Delta) G = K, \quad K := S G - G A + T,
\]
\[
(D_t - \nu \Delta) H = R_H, \quad R_H := K G^T + G K^T - 2\nu B_G, \quad B_G := \sum_{\ell=1}^3 (\partial_\ell G)(\partial_\ell G)^T.
\]

### 5.1 Backward Itô Tensor SDEs
Under the backward Itô differential $\widehat{d}$ (where $ds < 0$ lookback step):
\[
\boxed{ \widehat{d} G_s = K(A_s, s) ds + \sqrt{2\nu} \sum_{\ell=1}^3 \partial_\ell G(A_s, s) \widehat{d}W_s^\ell },
\]
\[
\boxed{ \widehat{d} H_s = R_H(A_s, s) ds + \sqrt{2\nu} \sum_{\ell=1}^3 \partial_\ell H(A_s, s) \widehat{d}W_s^\ell }.
\]

### 5.2 Unnormalized Weight SDE ($\widehat{d} q_i$)
Since $q_i(s) = \operatorname{tr}(P_i(s) H_s)$ and $P_i(s)$ is a deterministic/bounded-variation transport tensor while $H_s$ carries the Brownian martingale noise:
\[
\boxed{ \widehat{d} q_i = \left[ \operatorname{tr}(\dot{P}_i H_s) + \operatorname{tr}(P_i R_H) \right] ds + \sqrt{2\nu} \sum_{\ell=1}^3 \operatorname{tr}(P_i \partial_\ell H_s) \widehat{d}W_s^\ell }.
\]
This decomposes $\widehat{d} q_i$ into three distinct physical mechanisms:
1. $\operatorname{tr}(\dot{P}_i H_s)$: **Deformation-frame rotation** ($\dot{P}_i = \partial_s P_i$).
2. $\operatorname{tr}(P_i R_H)$: **Active vorticity-gradient stretching, advective mixing, and viscous dissipation**.
3. $\sqrt{2\nu} \sum_\ell \operatorname{tr}(P_i \partial_\ell H_s) \widehat{d}W_s^\ell$: **Stochastic spatial redistribution martingale noise**.

### 5.3 Normalized Orientation Weight SDE ($\widehat{d} p_i$ on $h > 0$)
On any interval where $h(A_s, s) \ge c > 0$, Itô's formula for $M = H / h$ gives $(D_t - \nu \Delta) M = R_M$, where:
\[
R_M := \frac{R_H - M \operatorname{tr}(R_H)}{h} + \frac{2\nu}{h} \sum_{\ell=1}^3 (\partial_\ell h)(\partial_\ell M).
\]
Then the normalized weights $p_i = \operatorname{tr}(P_i M)$ satisfy:
\[
\boxed{ \widehat{d} p_i = \left[ \operatorname{tr}(\dot{P}_i M) + \operatorname{tr}(P_i R_M) \right] ds + \sqrt{2\nu} \sum_{\ell=1}^3 \operatorname{tr}(P_i \partial_\ell M) \widehat{d}W_s^\ell }.
\]
$$\boxed{ \text{Crucial Finding: } p_i(s) \text{ contains an explicit non-vanishing stochastic martingale noise term. It does NOT follow an ordinary ODE.} }$$

---

## 6. Forwardization & Precise Definitions of Persistence

To investigate persistence statistics rigorously, we forwardize the time parameter:
\[
\tau := T - s \ge 0, \quad d\tau = -ds.
\]
Define the forwardized processes:
\[
\widetilde{\Gamma}_\tau := \Gamma_{T-\tau}, \quad \widetilde{H}_\tau := H(A_{T-\tau}, T-\tau), \quad \widetilde{\eta}_\tau := \eta(T-\tau).
\]
We formally freeze the mathematical definitions of persistence to prevent semantic conflation:

1. **Low-Orientation Set**: For $\varepsilon \in (0, 1)$, $\mathcal{L}_\varepsilon := \{ \eta \in [0, 1] : \eta \le \varepsilon \}$.
2. **Occupation Time on $[0, L]$**:
   \[
   \mathcal{O}_\varepsilon(L) := \int_0^L \mathbf{1}_{\{\widetilde{\eta}_\tau \le \varepsilon\}} d\tau \in [0, L].
   \]
3. **First Entrance Time**:
   \[
   \tau_{\text{enter}}(\varepsilon) := \inf \{ \tau \ge 0 : \widetilde{\eta}_\tau \le \varepsilon \}.
   \]
4. **First Exit Time**:
   \[
   \tau_{\text{exit}}(\varepsilon) := \inf \{ \tau > \tau_{\text{enter}}(\varepsilon) : \widetilde{\eta}_\tau > \varepsilon \}.
   \]
5. **Consecutive Residence Duration**:
   \[
   \Delta \tau_{\text{res}}(\varepsilon) := \tau_{\text{exit}}(\varepsilon) - \tau_{\text{enter}}(\varepsilon).
   \]
6. **Return Probability**:
   \[
   \mathbb{P}_{\text{return}}(\varepsilon, L) := \mathbb{P}\left( \exists \tau \in (\tau_{\text{exit}}, L] : \widetilde{\eta}_\tau \le \varepsilon \right).
   \]

---

## 7. Refined Target Question for Milestone TP2-G4-A3

With the stochastic SDE and stopping boundaries established, Milestone `TP2-G4-A3` is retitled:

### Task ID: `TP2-G4-A3`
**Title**: `TP2-G4-A3 — STOCHASTIC ORIENTATION-WEIGHT DYNAMICS AND LOW-ETA OCCUPATION / EXIT-TIME ANALYSIS`

**Governing Research Question**:
\[
\boxed{ \begin{aligned} &\text{Given the coupled stochastic tensor process } (\widetilde{\Gamma}_\tau, \widetilde{H}_\tau), \\ &\text{can Navier–Stokes dynamics provide an a-priori, non-circular upper bound} \\ &\text{on the expected occupation time } \mathbb{E}[\mathcal{O}_\varepsilon(L)] \text{ or consecutive residence time } \Delta \tau_{\text{res}}(\varepsilon) \\ &\text{spent in the low-efficiency regime } \mathcal{L}_\varepsilon = \{\widetilde{\eta}_\tau \le \varepsilon\} \text{ during extreme backward deformation?} \end{aligned} }
\]
