# TP2-G4-A2: STRAIN FRAME, DEFORMATION FRAME & PRESSURE HESSIAN AUDIT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Milestone:** `TP2-G4-A2`  
**Governance Standard:** Autonomous Project Governance v2.9.4  
**Date:** 2026-08-25T00:27:30Z  

---

## 1. Separation of the Two Characteristic Frames

A fundamental source of past mathematical confusion in turbulence modeling is the conflation of the instantaneous Eulerian strain eigenframe with the finite-time Lagrangian deformation frame. We strictly distinguish them:

| Property | Instantaneous Eulerian Strain Frame | Finite-Time Lagrangian Deformation Frame |
|---|---|---|
| **Governing Tensor** | $S(x, t) = \frac{1}{2}(\nabla u + (\nabla u)^T)$ | $\Gamma_s(x) = D_{s, T}(x)^T D_{s, T}(x) = (\nabla A_{s, T})^{-T} (\nabla A_{s, T})^{-1}$ |
| **Basis Vectors** | Orthonormal eigenvectors $e_1, e_2, e_3$ | Right singular vectors $v_1, v_2, v_3$ of $D_{s, T}$ |
| **Spectrum** | $\lambda_1 \le \lambda_2 \le \lambda_3$ with $\sum \lambda_i = 0$ | $\sigma_1^2 \ge \sigma_2^2 \ge \sigma_3^2 > 0$ with $\sigma_1 \sigma_2 \sigma_3 = 1$ |
| **Temporal Nature** | Local instantaneous velocity gradient | Nonlocal time-integrated trajectory deformation |
| **Governing Dynamics** | Local Riccati + non-local pressure Hessian | Linear matrix transport ODE driven by $A(s)$ |

---

## 2. Derivation of the Strain Evolution Equation

Applying the gradient $\nabla$ to the Navier–Stokes momentum equation $\partial_t u + (u \cdot \nabla)u + \nabla p = \nu \Delta u$:
\[
D_t A = -A^2 - \operatorname{Hess}(p) + \nu \Delta A, \quad \operatorname{Hess}(p)_{ij} := \partial_i \partial_j p.
\]
Decomposing $A = S + \Omega$ into symmetric strain $S$ and skew-symmetric rotation $\Omega = \frac{1}{2}(A - A^T)$:
\[
A^2 = (S + \Omega)(S + \Omega) = S^2 + S \Omega + \Omega S + \Omega^2.
\]
Taking the symmetric part of $D_t A$:
\[
\boxed{ D_t S = -S^2 - \Omega^2 - \operatorname{Hess}(p) + \nu \Delta S }.
\]
Note that $S \Omega + \Omega S$ is skew-symmetric, so it vanishes from the strain equation, leaving only the centrifugal term $-\Omega^2 = \frac{1}{4}(|\omega|^2 I - \omega \otimes \omega)$.

---

## 3. Strain Eigenframe Rotation Dynamics

Let $S = \sum_{i=1}^3 \lambda_i e_i e_i^T$ with simple spectrum $\lambda_1 < \lambda_2 < \lambda_3$.
Differentiating along particle paths:
\[
D_t S = \sum_{i=1}^3 (D_t \lambda_i) e_i e_i^T + \sum_{i=1}^3 \lambda_i (D_t e_i) e_i^T + \sum_{i=1}^3 \lambda_i e_i (D_t e_i)^T.
\]
Projecting onto the off-diagonal frame element $(e_j, e_i)$ for $j \neq i$:
\[
e_j^T (D_t S) e_i = \lambda_i e_j^T (D_t e_i) + \lambda_j (D_t e_j)^T e_i = (\lambda_i - \lambda_j) e_j \cdot (D_t e_i).
\]
Substituting the strain evolution equation $D_t S = -S^2 - \Omega^2 - \operatorname{Hess}(p) + \nu \Delta S$, and noting that $e_j^T S^2 e_i = \lambda_i^2 \delta_{ji} = 0$:
\[
\boxed{ e_j \cdot (D_t e_i) = \frac{-e_j^T \Omega^2 e_i - e_j^T \operatorname{Hess}(p) e_i + \nu e_j^T (\Delta S) e_i}{\lambda_i - \lambda_j} \quad (i \neq j) }.
\]

### 3.1 Role of Deviatoric Pressure Hessian
Let $\operatorname{Hess}(p) = \frac{1}{3}(\Delta p) I + \Pi^{\text{dev}}$, where $\Pi^{\text{dev}}$ is the trace-free deviatoric pressure Hessian.
Since $e_j^T I e_i = \delta_{ji} = 0$, isotropic pressure drops out:
\[
e_j^T \operatorname{Hess}(p) e_i = e_j^T \Pi^{\text{dev}} e_i.
\]
This rigorously recovers the `TH9-R` result: the deviatoric pressure Hessian acts as the dominant physical torque driving angular rotation between strain eigenvectors.

---

## 4. Coupling Between Strain Frame and Deformation Frame

Define the frame overlap matrix $R \in \mathbb{R}^{3 \times 3}$:
\[
R_{ij} := |v_i \cdot e_j|^2 \ge 0, \quad \sum_{j=1}^3 R_{ij} = \|v_i\|^2 = 1, \quad \sum_{i=1}^3 R_{ij} = \|e_j\|^2 = 1.
\]
$R$ is a **doubly stochastic matrix** quantifying the geometric alignment between the time-integrated singular frame $v_i$ and the instantaneous strain eigenframe $e_j$.

### 4.1 Direct vs Indirect Action of Pressure Hessian
- **Direct Action**: Pressure Hessian $\Pi^{\text{dev}}$ acts directly on the instantaneous strain frame rotation $\dot{e}_i$.
- **Indirect Action**: Pressure Hessian influences the deformation frame $v_i$ exclusively through the time-integrated path history of $A(s) = S(s) + \Omega(s)$ via $\partial_s \Gamma_s = -A_s^T \Gamma_s - \Gamma_s A_s$.
- **Independence**: High instantaneous strain rotation $\dot{e}_i$ does **not** imply simultaneous deformation frame rotation $\dot{v}_i$, because $\Gamma_s$ represents cumulative historical stretching.
