# TP2-G6-C1: PAIR COVARIANCE TENSOR AND SPECTRAL AUDIT

## Work Package WP10: Multidirectional Dispersion, Rank Analysis, and the Shear Barrier

---

### 1. Purpose and Target Bridge B3

Bridge **`B3 — Covariance Spectrum / Multidirectional Dispersion`** was identified in TP2-G5-A4 and formalized in TP2-G6-B-R1 as the requirement to establish that stochastic Lagrangian fluctuations span all three spatial dimensions, ruling out planar, unidirectional, or rank-deficient blowup scenarios.

In Claim `CLM-029`, the programme proved that in periodic 1D shear flows, the single-particle covariance tensor $C_s$ satisfies $\operatorname{tr}(C_s) > 0$ while its rank is strictly 1 ($\lambda_2 = \lambda_3 = 0$), establishing `NS-OBS-016` (Covariance Trace Spectral Underdetermination).

This work package formulates the **Two-Particle Covariance Tensor**:
$$
C_s^{\text{pair}}(x, h) = \mathbb{E}\left[ \delta A_s(x, h) \otimes \delta A_s(x, h) \right] \in \mathbb{R}^{3 \times 3},
$$
and evaluates whether two-particle relative transport can unconditionally generate full-rank multidirectional dispersion ($\lambda_3 > 0$) without circularity.

---

### 2. Formulations of Pair Covariance

Let $\delta A_s = A_s(x+h) - A_s(x)$ with lookback time $s \in [0, t]$.

#### 2.1 Uncentered Pair Second-Moment Tensor
$$
\boxed{
C_s^{\text{pair}}(x, h) = \mathbb{E}\left[ \delta A_s(x, h) \otimes \delta A_s(x, h) \right].
}
$$
- Trace: $\operatorname{tr}(C_s^{\text{pair}}) = \mathbb{E}[|\delta A_s|^2] = \mathbb{E}[R_s]$.
- Initial condition: $C_t^{\text{pair}} = h \otimes h$ (rank 1 at lookback $s = t$).

#### 2.2 Centered Pair Covariance Tensor
$$
\boxed{
\tilde{C}_s^{\text{pair}}(x, h) = \mathbb{E}\left[ (\delta A_s - \mathbb{E}[\delta A_s]) \otimes (\delta A_s - \mathbb{E}[\delta A_s]) \right] = C_s^{\text{pair}} - \mathbb{E}[\delta A_s] \otimes \mathbb{E}[\delta A_s].
}
$$
- Captures pure stochastic fluctuations around the mean relative trajectory.
- Initial condition: $\tilde{C}_t^{\text{pair}} = 0$.

---

### 3. Spectral Decomposition and Rank Audit

Let $\lambda_1(s) \ge \lambda_2(s) \ge \lambda_3(s) \ge 0$ be the eigenvalues of $C_s^{\text{pair}}$.

#### 3.1 Behavior under Coupling C-SYNC in Periodic Shear Flow
Consider the exact periodic shear flow on $\mathbb{T}^3$:
$$
u(x, y, z) = (U(y), 0, 0)^T, \qquad \omega = (0, 0, -U'(y))^T.
$$
Under Coupling C-SYNC (WP1):
$$
d(\delta A_s) = - \left( U(A_s^y(x+h)) - U(A_s^y(x)),\ 0,\ 0 \right)^T ds.
$$
Notice that:
$$
\frac{d}{ds} \delta A_s^y = 0 \implies \delta A_s^y(s) \equiv h_y, \qquad \frac{d}{ds} \delta A_s^z = 0 \implies \delta A_s^z(s) \equiv h_z.
$$
The $y$ and $z$ coordinates of relative separation are **strictly constant** across all paths $\omega \in \Omega$!
Therefore:
$$
\delta A_s - \mathbb{E}[\delta A_s] = \left( \delta A_s^x - \mathbb{E}[\delta A_s^x],\ 0,\ 0 \right)^T.
$$
Computing the centered covariance:
$$
\tilde{C}_s^{\text{pair}} = \operatorname{diag}\left( \operatorname{Var}(\delta A_s^x),\ 0,\ 0 \right).
$$
**Rigorous Finding 1**: Under Coupling C-SYNC, the fluctuating pair covariance $\tilde{C}_s^{\text{pair}}$ in periodic shear is **strictly rank 1**:
$$
\lambda_1(s) = \operatorname{Var}(\delta A_s^x) > 0, \qquad \lambda_2(s) \equiv 0, \qquad \lambda_3(s) \equiv 0.
$$
C-SYNC **cannot overcome the rank-one obstruction** of CLM-029 in shear geometry.

#### 3.2 Behavior under Coupling C-IND in Periodic Shear Flow
Under Coupling C-IND:
$$
d(\delta A_s) = - \left( U(A_s^y(x+h)) - U(A_s^y(x)),\ 0,\ 0 \right)^T ds + \sqrt{4\nu}\, dB_s.
$$
Here $B_s = (B_s^x, B_s^y, B_s^z)^T$ has independent components.
Integrating the $y$ and $z$ components:
$$
\delta A_s^y = h_y + \sqrt{4\nu} (B_t^y - B_s^y), \qquad \delta A_s^z = h_z + \sqrt{4\nu} (B_t^z - B_s^z).
$$
The variances in the transverse directions are:
$$
\operatorname{Var}(\delta A_s^y) = 4\nu (t - s), \qquad \operatorname{Var}(\delta A_s^z) = 4\nu (t - s).
$$
Therefore:
$$
\lambda_3(s) \ge 4\nu (t - s) > 0 \quad \text{for all } s < t.
$$
**Rigorous Finding 2**: Under Coupling C-IND, the pair covariance tensor has **full rank 3** ($\lambda_3 > 0$).
**Crucial Epistemic Caveat**: The transverse eigenvalues $\lambda_2, \lambda_3$ are generated **entirely by molecular Brownian diffusion** ($4\nu \Delta t$), NOT by advective stretching or turbulent mixing. The fluid velocity contribution remains strictly 1D.

---

### 4. Anisotropy Ratio and the Turbulent Stretching Signature

To distinguish trivial molecular diffusion from genuine fluid-driven multidirectional dispersion, we define the **Stochastic Dispersion Anisotropy Ratio**:
$$
\mathcal{A}_s = \frac{\lambda_1(s) - \lambda_3(s)}{\operatorname{tr}(C_s^{\text{pair}})}.
$$
- **Isotropic 3D Diffusion**: $\lambda_1 = \lambda_2 = \lambda_3 \implies \mathcal{A}_s = 0$.
- **Pure 1D Stretching**: $\lambda_1 \gg \lambda_2, \lambda_3 \implies \mathcal{A}_s \to 1$.

In high-Reynolds-number candidate blowup regimes ($M_n \to \infty$):
- Along the principal strain axis, $\lambda_1 \sim e^{2 M_n \tau_n} |h|^2 \sim e^2 |h|^2$.
- In the transverse directions, independent Brownian diffusion gives $\lambda_3 \sim 4\nu \tau_n = 4\nu M_n^{-1} \to 0$.
- Consequently:
  $$
  \frac{\lambda_3}{\lambda_1} \sim \frac{4\nu M_n^{-1}}{|h|^2} \to 0 \quad \text{as } M_n \to \infty \text{ for fixed } |h|.
  $$
**Conclusion**: In intense vortex stretching, the pair covariance tensor is **asymptotically rank-deficient**, collapsing onto the dominant stretching eigenvector of the strain tensor.

---

### 5. Constitutional Firewall on Covariance Rank

$$\boxed{\mathbf{RULE\ B3\text{-}1:\ NO\ BROWNIAN\ TRIVIALITY}}$$
A proof claiming resolution of Bridge $B_3$ (Multidirectional Dispersion) via Coupling C-IND by pointing to $\lambda_3 \ge 4\nu \Delta t > 0$ is **categorically rejected as kinematically trivial**.
Resolution of Bridge $B_3$ requires proving that the **fluid advective contribution** to $\tilde{C}_s^{\text{pair}}$ satisfies $\lambda_3^{\text{fluid}} > 0$ independently of $\nu$, which remains obstructed in 1D/2D symmetric flows.
