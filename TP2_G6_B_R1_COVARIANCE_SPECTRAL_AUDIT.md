# TP2-G6-B-R1: Covariance Spectral and Tensor-Degeneracy Audit

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Subprogramme:** `TP2-G6: BRIDGE RESOLUTION PROGRAMME`  
**Milestone:** `TP2-G6-B-R1 (Work Package 4)`  
**Governance Standard:** Universal Autonomous Project Governance v3.0.0 & MRC v1.0.1  
**Target Bridge:** `B3 — Covariance Spectrum / Multidirectional Dispersion`  
**Target Problem:** Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0$, $f = 0$)  
**Target Status:** `UNRESOLVED`  

---

## 1. Objective and Problem Context

A central open question of Bridge $B_3$ is whether accumulated stochastic quadratic variation production (Branch D) guarantees genuine 3D multidirectional stochastic dispersion, or whether high scalar production can coexist with a degenerate, low-rank covariance tensor.

Recall the stochastic covariance tensor defined in `TP2-G3` (`CLM-002`):
\[
C_s := 2\nu \int_s^T \mathbb{E}\left[ (D_r J_\omega(A_r, r))(D_r J_\omega(A_r, r))^\top \right] dr \succeq 0.
\]
The scalar variance budget is the trace:
\[
V_s := \operatorname{tr}(C_s) = 2\nu \int_s^T \mathbb{E}\left[ \|D_r J_\omega(A_r, r)\|_F^2 \right] dr.
\]
The purpose of Work Package 4 is to audit the relationship between the scalar trace $\operatorname{tr}(C_s)$ and the full eigenvalue spectrum:
\[
\lambda_1(C_s) \ge \lambda_2(C_s) \ge \lambda_3(C_s) \ge 0.
\]
Specifically: **Can an exact smooth Navier–Stokes flow have $\operatorname{tr}(C_s) > 0$ while $\lambda_2(C_s) = \lambda_3(C_s) = 0$?**

---

## 2. Rigorous Proof of Extreme Covariance Degeneracy

### Theorem 1 (Maximal Covariance Rank Deficiency in Navier–Stokes)
There exist exact, globally smooth, divergence-free solutions to the 3D incompressible Navier–Stokes equations on the periodic torus $\mathbb{T}^3$ for which:
\[
\operatorname{tr}(C_s) > 0 \quad \text{for all } s < T,
\]
while the covariance tensor is **strictly rank 1**:
\[
\boxed{ \lambda_2(C_s) \equiv 0, \quad \lambda_3(C_s) \equiv 0, \quad \det(C_s) \equiv 0, \quad \frac{\lambda_{\min}(C_s)}{\operatorname{tr}(C_s)} \equiv 0 }.
\]

### Proof
Consider the unforced periodic shear flow on $\mathbb{T}^3$:
\[
u(x, y, z, t) = (U(y, t), 0, 0), \quad U(y, t) = A e^{-\nu k^2 t} \sin(ky).
\]
As proved in `CLM-005` (WP2, Family 1), this is an exact solution to 3D Navier–Stokes on $\mathbb{T}^3$.
1. The vorticity vector is aligned strictly along the $z$-axis:
   \[
   \omega(x, y, z, t) = (0, 0, -U_y(y, t)) = -U_y e_3.
   \]
2. The vorticity gradient tensor is:
   \[
   J_\omega = \nabla \omega = -U_{yy} (e_3 \otimes e_2).
   \]
3. The Cauchy deformation tensor is:
   \[
   D_r = I + \alpha(r, T) (e_1 \otimes e_2), \quad \text{where } \alpha(r, T) = \int_r^T U_y(y(\tau), \tau) d\tau.
   \]
4. Multiplying $D_r$ by $J_\omega$:
   \[
   D_r J_\omega = (I + \alpha e_1 \otimes e_2)(-U_{yy} e_3 \otimes e_2) = -U_{yy} (e_3 \otimes e_2) + 0 = -U_{yy} (e_3 \otimes e_2).
   \]
5. Computing the matrix outer product:
   \[
   (D_r J_\omega)(D_r J_\omega)^\top = U_{yy}^2 (e_3 \otimes e_2)(e_2 \otimes e_3) = U_{yy}^2 (e_3 \cdot e_3) (e_3 \otimes e_3) = U_{yy}^2 \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \\ 0 & 0 & 1 \end{pmatrix}.
   \]
6. Taking the expectation and integrating over $r \in [s, T]$:
   \[
   C_s = 2\nu \int_s^T \mathbb{E}\left[ U_{yy}^2(A_r, r) \right] dr \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & 0 \\ 0 & 0 & 1 \end{pmatrix}.
   \]
Let $\mathcal{I}_s := 2\nu \int_s^T \mathbb{E}[U_{yy}^2(A_r, r)] dr$. For any non-trivial solution ($A > 0, k \ge 1$), $\mathcal{I}_s > 0$ for all $s < T$.
The eigenvalues of $C_s$ are:
\[
\lambda_1(C_s) = \mathcal{I}_s = \operatorname{tr}(C_s) > 0, \quad \lambda_2(C_s) = 0, \quad \lambda_3(C_s) = 0.
\]
The determinant is identically zero: $\det(C_s) = \lambda_1 \lambda_2 \lambda_3 \equiv 0$. $\blacksquare$

---

## 3. General Condition for Covariance Rank and Spectral Gap

What geometric conditions are required for $C_s$ to achieve full rank ($\operatorname{rank} C_s = 3$) and a positive spectral gap $\lambda_{\min}(C_s) > 0$?

### Proposition 1 (Dyadic Rank Representation)
For any fluid flow, the integrand of the covariance tensor is a sum of rank-1 matrices:
\[
(D_r J_\omega)(D_r J_\omega)^\top = \sum_{j=1}^3 (D_r \partial_j \omega) \otimes (D_r \partial_j \omega).
\]
Therefore, $C_s$ is full-rank if and only if the collection of vectors $\{D_r \partial_j \omega(A_r, r)\}_{j=1}^3$ spans all three dimensions of $\mathbb{R}^3$ over the Brownian trajectories:
\[
\operatorname{span}\left\{ D_r \partial_j \omega(A_r(\omega_0), r) : j \in \{1, 2, 3\}, r \in [s, T], \omega_0 \in \Omega \right\} = \mathbb{R}^3.
\]

### Corollary 1.1 (Planar and Unidirectional Vorticity Failure)
If the vorticity direction field $\xi(x, t) = \frac{\omega(x, t)}{|\omega(x, t)|}$ is spatially uniform across the flow domain ($\xi(x, t) \equiv \xi_0$), then $\partial_j \omega = (\partial_j |\omega|) \xi_0$.  
Consequently:
\[
D_r \partial_j \omega = (\partial_j |\omega|) D_r \xi_0.
\]
All three columns of $D_r J_\omega$ are collinear along the single vector $D_r \xi_0$.  
The matrix $(D_r J_\omega)(D_r J_\omega)^\top$ is strictly rank 1 for every realization, and $C_s$ has $\operatorname{rank}(C_s) \le 1$.

---

## 4. Consequences for Bridge $B_3$ and the Negative Evidence Ledger

This audit establishes a permanent, negative evidence barrier for Bridge $B_3$:

$$\boxed{ \mathbf{NS\text{-}OBS\text{-}016\ (CONFIRMED\ \&\ EXPANDED):} \quad \operatorname{tr}(C_s) > 0 \not\implies \lambda_{\min}(C_s) > 0 }$$

1. **Failure of Trace as a Dispersion Proxy:**
   A lower bound on the scalar quadratic variation $Q_s = -\partial_s V_s > 0$ or accumulated production $J_n(a) > 0$ does **not** imply multidirectional dispersion. A flow can have arbitrarily large scalar production $Q_s \to \infty$ while its covariance tensor remains strictly 1D degenerate.
2. **Requirement for Multidirectional Regularity:**
   Any future regularity bridge relying on stochastic dispersion cannot operate at the trace level. It must explicitly enforce a **spectral gap condition**:
   \[
   \frac{\lambda_{\min}(C_s)}{\operatorname{tr}(C_s)} \ge c_0 > 0.
   \]
   In periodic shear, this ratio is identically $0$. In 2D flows, this ratio is identically $0$.
3. **Bridge Target Status:**
   Bridge $B_3$ cannot be closed by scalar quadratic variation identities alone; it requires genuine 3D vorticity-direction twisting ($\nabla \xi \ne 0$) across Brownian dispersion paths.
