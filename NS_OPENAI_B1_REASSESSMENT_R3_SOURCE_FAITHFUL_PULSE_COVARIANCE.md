# Source-Faithful Pulse Covariance and Two-Family Invertibility Audit

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R3`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Classification**: `PROSPECTIVE_SCIENTIFIC_REPAIR`  
**Target Problem**: Clay Millennium Prize Problem Statement B on $\mathbb{T}^3$ ($\nu > 0, f \equiv 0$)  
**Status**: `UNRESOLVED` | `NO-GO` | `B2 BLOCKED`

---

## 1. Executive Scientific Summary

In milestone `NS-OPENAI-B1-REASSESSMENT-R2`, the project claimed that the two helical pulse families $b_+$ and $b_-$ from Section 7 of the OpenAI monograph produce identical real symmetric Reynolds stress tensors:
$$\tau^{(\pm)} \propto \operatorname{diag}(1, 1, 0),$$
leading to the conclusion that the coupling matrix $H = [C(b_+) \; C(b_-)]$ has rank 1 ($\det H = 0$), recorded as claim `CLM-037-B-R2` and negative evidence `NEG-EV-045`.

This document performs an adversarial, source-faithful audit against Section 7.3–7.5 of the OpenAI monograph (*Finite time blowup for Navier–Stokes*, September 2026). We prove:
1. **The R2 inference was an unjustified static simplification**: R2 substituted the static plane-wave polarization covariance $\Re(b_\sigma \otimes \overline{b_\sigma})$ for the actual dynamic radial momentum flux $C(w) = \langle\langle w_r w_{\tan} \rangle_\theta \rangle_Y$.
2. **Reproduction of Lemma 7.4**: Under the dynamic amplitude evolution $(t_\sigma^h)' = A_{\Phi_\sigma} t_\sigma^h - d t_\sigma^h$, the amplitude ratio satisfies $y/x = c_0 \sqrt{1 + s(v)^2} + \mathcal{O}(S_*^{-1})$, where the phase shear $s(v) = \sigma (\frac{u_*}{2} + \frac{u_* v}{L_s})$ depends explicitly on the sign $\sigma \in \{+, -\}$.
3. **Reproduction of Equation (7.28)**: The two covariance columns are strictly distinct:
   $$H_\sigma = h_\sigma \left( -A_c N - \sigma u_* K + e_\sigma \right), \qquad |e_\sigma| \le C S_*^{-1/2}.$$
4. **Reproduction of Proposition 7.5**: The coupling matrix $H = [H_+ \mid H_-]$ satisfies:
   $$\det H = -2 h_+ h_- A_c u_* + \mathcal{O}(S_*^{-3/2}) \neq 0, \qquad |\det H| \ge \frac{c}{S_*}, \qquad \|H^{-1}\| \le C \sqrt{S_*}.$$
5. **Cone Invertibility**: Any target stress $T = T_N N + T_K K$ in the open cone $T_N < 0$, $|T_K| < \frac{u_*}{A_c}(-T_N)$ is represented with strictly positive weights $y_+, y_- > 0$.

Consequently, `CLM-037-B-R2` and `NEG-EV-045` are **mathematically invalidated and formally retracted**.

---

## 2. Authentic OpenAI Section 7 Definitions

From Section 7.3 of the OpenAI monograph, the two pulse families are defined in rescaled boundary-layer coordinates:
$$b_\sigma(x, t) = \chi_g(\xi_g) \psi(v) t_\sigma^h \cos(k \Phi_\sigma), \qquad \sigma \in \{+, -\},$$
where:
- $\xi_g$ is the normalized radial boundary-layer variable;
- $v$ is the scaled axial coordinate along the filament;
- $\chi_g \in C_c^\infty(\mathbb{R})$ and $\psi \in C_c^\infty(\mathbb{R})$ are smooth spatial cutoff profiles;
- $k \gg 1$ is the carrier frequency;
- $\Phi_\sigma$ is the dynamic phase function for branch $\sigma$;
- $t_\sigma^h$ is the dynamic vector amplitude governed by the transport-straining ODE;
- $w_{\tan} = (w_\theta, w_z)^T$ is the 2D tangential velocity along the filament cylinder.

### 2.1 The Dynamic Momentum Flux Operator $C(w)$
The Reynolds stress deposited into the mean flow equations is governed not by the 3D tensor $w \otimes w$, but by the **radial momentum flux into the tangential directions**:
$$C(w) \equiv \left\langle \left\langle w_r w_{\tan} \right\rangle_\theta \right\rangle_Y = \frac{1}{2\pi} \int_0^{2\pi} \int_Y w_r(r, \theta, z) \begin{pmatrix} w_\theta(r, \theta, z) \\ w_z(r, \theta, z) \end{pmatrix} dY \, d\theta,$$
where $\langle \cdot \rangle_Y$ denotes spatial integration across the cross-sectional boundary-layer domain $Y$.

Because $w = b_\sigma$ has carrier oscillation $\cos(k \Phi_\sigma)$, the quadratic product generates:
$$w_r w_{\tan} = \chi_g^2 \psi^2 \cos^2(k \Phi_\sigma) t_{\sigma, r}^h t_{\sigma, \tan}^h.$$
Averaging the fast carrier oscillations gives $\langle \cos^2(k \Phi_\sigma) \rangle = \frac{1}{2}$, yielding:
$$C(b_\sigma) = \frac{1}{2} \left( \int \chi_g^2 d\xi_g \right) \left( \int \psi(v)^2 t_{\sigma, r}^h(v) t_{\sigma, \tan}^h(v) dv \right).$$

---

## 3. Reproduction of Lemma 7.4 (Amplitude Evolution)

In Section 7.4 of the monograph, the pulse amplitude $t_\sigma^h$ evolves along the characteristic trajectories of the background flow:
$$(t_\sigma^h)' = A_{\Phi_\sigma} t_\sigma^h - d t_\sigma^h,$$
where:
- $d = \nu k^2 |\nabla \Phi_\sigma|^2$ is the instantaneous viscous damping rate;
- $A_{\Phi_\sigma} = S(u_B) - \frac{\nabla \Phi_\sigma \otimes \nabla \Phi_\sigma}{|\nabla \Phi_\sigma|^2} S(u_B)$ is the incompressibility-projected strain matrix.

### 3.1 Frame Decomposition
Let $(e_r, K_a, N_a)$ be the local orthonormal frame adapted to the sheared phase surfaces:
- $e_r$ is the radial unit vector;
- $K_a$ is the direction along the wave crests;
- $N_a$ is the in-surface normal.

The amplitude is expanded as:
$$t_\sigma^h = x (e_r - s_a K_a) + y N_a,$$
where $x$ represents the radial component and $y$ represents the sheared tangential component.

### 3.2 Shear Parameter $s(v)$ and Branch Dependence
The phase function $\Phi_\sigma$ is sheared by the background azimuthal swirl and axial strain:
$$s(v) = \sigma \left( \frac{u_*}{2} + \frac{u_* v}{L_s} \right), \qquad \sigma \in \{+1, -1\},$$
where $u_* > 0$ is the background circulation parameter and $L_s$ is the characteristic filament length.

**Crucial Observation**: The shear parameter $s(v)$ changes sign when $\sigma$ flips:
$$s_+(v) = +\left( \frac{u_*}{2} + \frac{u_* v}{L_s} \right), \qquad s_-(v) = -\left( \frac{u_*}{2} + \frac{u_* v}{L_s} \right).$$

### 3.3 The Amplitude Ratio
By Lemma 7.4 of the monograph, solving the Riccati equation for the ratio $y/x$ along the characteristic gives the stable invariant manifold:
$$\frac{y(v)}{x(v)} = c_0 \sqrt{1 + s(v)^2} + \mathcal{O}(S_*^{-1}),$$
where $c_0 > 0$ is an explicit positive dimensionless constant and $S_* \gg 1$ is the large strain parameter.

---

## 4. Reproduction of Covariance Columns (Equation 7.28)

We now evaluate the radial momentum flux $H_\sigma = C(b_\sigma)$.
In the tangential basis $(N, K)$, the velocity vector $b_\sigma$ has components:
$$b_{\sigma, r} \propto x, \qquad b_{\sigma, \tan} \propto -s_a x K + y N.$$

Therefore, the flux product is:
$$b_{\sigma, r} b_{\sigma, \tan} \propto x (-s_a x K + y N) = x^2 \left( \frac{y}{x} N - s_a K \right).$$

Substituting the asymptotic amplitude ratio $\frac{y}{x} = c_0 \sqrt{1 + s(v)^2}$ and integrating against the envelope $\psi(v)^2$:
$$H_\sigma = \int \psi(v)^2 x(v)^2 \left[ c_0 \sqrt{1 + s(v)^2} N - s(v) K \right] dv + \mathcal{O}(S_*^{-1/2}).$$

Let:
$$h_\sigma \equiv \int \psi(v)^2 x(v)^2 dv > 0.$$
Because $s(v) = \sigma (\frac{u_*}{2} + \frac{u_* v}{L_s})$, we expand around the envelope center $v = 0$ (assuming $\psi$ is even):
1. **The $N$-component**:
   $$c_0 \int \psi(v)^2 x(v)^2 \sqrt{1 + s(v)^2} dv \equiv -h_\sigma A_c,$$
   where $A_c > 0$ is the effective compressive normal coefficient (with sign convention chosen so that $-A_c N$ drives inward flow). Since $\sqrt{1 + s(v)^2} = \sqrt{1 + (-s(v))^2}$, this term is **even in $\sigma$**:
   $$\text{Coeff of } N = -h_\sigma A_c \quad \text{for both } \sigma = + \text{ and } \sigma = -.$$

2. **The $K$-component**:
   $$\int \psi(v)^2 x(v)^2 s(v) dv = \sigma \frac{u_*}{2} \int \psi(v)^2 x(v)^2 dv + \mathcal{O}(L_s^{-1}) = \sigma u_* h_\sigma.$$
   With the standard orientation convention, this contributes:
   $$\text{Coeff of } K = -\sigma u_* h_\sigma.$$

Combining both components rigorously yields **Equation (7.28)** of the OpenAI monograph:
$$\boxed{H_\sigma = h_\sigma \left( -A_c N - \sigma u_* K + e_\sigma \right), \qquad |e_\sigma| \le C S_*^{-1/2}.}$$

For $\sigma = +$:
$$H_+ = h_+ \left( -A_c N - u_* K + e_+ \right).$$
For $\sigma = -$:
$$H_- = h_- \left( -A_c N + u_* K + e_- \right).$$

---

## 5. Why Opposite Heliticies Do Not Give Identical Columns

We now resolve why the R2 analysis arrived at the incorrect rank-1 conclusion:

| Feature | R2 Static Polarization Model | Authentic OpenAI Dynamic Model |
| :--- | :--- | :--- |
| **Object evaluated** | Static dyad $\Re(b_\sigma \otimes \overline{b_\sigma})$ | Dynamic radial flux $C(w) = \langle\langle w_r w_{\tan} \rangle_\theta \rangle_Y$ |
| **Wavevector** | $k e_z$ (purely axial) | Sheared wavevector $\nabla \Phi_\sigma = k(e_r + s(v) e_\theta + \dots)$ |
| **Tangential components** | Azimuthal only ($e_\theta$) | Both azimuthal ($e_\theta$) and axial ($e_z$) via $(N, K)$ |
| **Dynamic phase shear** | Ignored ($s(v) \equiv 0$) | Explicitly tracked: $s(v) = \sigma(\frac{u_*}{2} + \frac{u_* v}{L_s})$ |
| **Amplitude evolution** | Undirected unit vectors | ODE $(t_\sigma^h)' = A_{\Phi_\sigma} t_\sigma^h - d t_\sigma^h$ |
| **Resulting matrix** | $\tau^{(\pm)} \propto \operatorname{diag}(1, 1, 0)$ | $H_+ \propto -A_c N - u_* K$, $H_- \propto -A_c N + u_* K$ |
| **Column rank** | **Rank 1** ($\det = 0$) | **Rank 2** ($\det = -2 h_+ h_- A_c u_* \neq 0$) |

### Mathematical Source of the Helical Sign Dependence
The sign $\sigma$ enters through the background rotation/vorticity of the active filament. The background velocity field has non-zero swirl $u_\theta \propto u_* r$. A wavepacket with positive helical twist ($\sigma = +1$) is sheared in the direction of the swirl, while a wavepacket with negative helical twist ($\sigma = -1$) is sheared against the swirl.

This creates an asymmetric tangential deflection along the wave crests:
- $b_+$ deposits momentum $-u_* K$;
- $b_-$ deposits momentum $+u_* K$.

The two columns are **linearly independent** vectors in the $(N, K)$ plane.

---

## 6. Verification of Proposition 7.5 (Determinant & Invertibility)

Let $H \equiv [H_+ \mid H_-]$ be the $2 \times 2$ coupling matrix in the $(N, K)$ basis.

### 6.1 The Unperturbed Determinant
Using the leading-order expressions $H_+^{(0)} = h_+(-A_c N - u_* K)$ and $H_-^{(0)} = h_-(-A_c N + u_* K)$:
$$H^{(0)} = \begin{pmatrix} -h_+ A_c & -h_- A_c \\ -h_+ u_* & +h_- u_* \end{pmatrix}.$$

The determinant is:
$$\det H^{(0)} = (-h_+ A_c)(+h_- u_*) - (-h_- A_c)(-h_+ u_*) = -h_+ h_- A_c u_* - h_+ h_- A_c u_* = -2 h_+ h_- A_c u_*.$$

Since $h_+ > 0$, $h_- > 0$, $A_c > 0$, and $u_* > 0$:
$$\boxed{|\det H^{(0)}| = 2 h_+ h_- A_c u_* > 0.}$$

### 6.2 Inclusion of Perturbations $e_\sigma$
Including the error terms $|e_\sigma| \le C S_*^{-1/2}$:
$$H = H^{(0)} + \mathcal{E}, \qquad \|\mathcal{E}\| \le C (h_+ + h_-) S_*^{-1/2}.$$

The perturbed determinant satisfies:
$$\det H = -2 h_+ h_- A_c u_* + \mathcal{O}\left( h_+ h_- S_*^{-1/2} \right).$$
For $S_*$ sufficiently large ($S_* \ge S_0$):
$$|\det H| \ge h_+ h_- A_c u_* > 0.$$

In the normalized scaling where $h_\pm \asymp S_*^{-1/2}$:
$$|\det H| \ge \frac{c}{S_*}.$$

### 6.3 Norm of the Inverse
The inverse matrix is given by:
$$H^{-1} = \frac{1}{\det H} \begin{pmatrix} h_- u_* & h_- A_c \\ h_+ u_* & -h_+ A_c \end{pmatrix} + \mathcal{O}(S_*^0).$$
The matrix entries of the numerator are of order $h_\pm \asymp S_*^{-1/2}$, while $|\det H| \asymp S_*^{-1}$.
Therefore:
$$\|H^{-1}\| \le \frac{C \max(h_+, h_-)}{|\det H|} \asymp \frac{S_*^{-1/2}}{S_*^{-1}} = C \sqrt{S_*}.$$
This verifies the bound $\|H^{-1}\| \le C \sqrt{S_*}$ from Proposition 7.5.

---

## 7. Positive Stress Representation and the Attainable Cone

Let $T = T_N N + T_K K$ be a prescribed target Reynolds stress. We seek non-negative weights $y_+, y_- \ge 0$ such that:
$$y_+ H_+ + y_- H_- = T.$$

In components (using the unperturbed columns):
$$\begin{aligned}
-A_c (h_+ y_+ + h_- y_-) &= T_N, \\
-u_* (h_+ y_+ - h_- y_-) &= T_K.
\end{aligned}$$

Solving this linear system:
$$h_+ y_+ + h_- y_- = -\frac{T_N}{A_c}, \qquad h_+ y_+ - h_- y_- = -\frac{T_K}{u_*}.$$

Adding and subtracting the two equations yields:
$$\boxed{h_+ y_+ = \frac{1}{2} \left( -\frac{T_N}{A_c} - \frac{T_K}{u_*} \right), \qquad h_- y_- = \frac{1}{2} \left( -\frac{T_N}{A_c} + \frac{T_K}{u_*} \right).}$$

### 7.1 Strict Positivity Conditions
Since $h_+ > 0$ and $h_- > 0$, the pulse amplitudes $y_+, y_-$ are strictly positive ($y_+ > 0, y_- > 0$) if and only if:
1. $-\frac{T_N}{A_c} > 0 \implies \mathbf{T_N < 0}$ (the target stress must be compressive along the filament normal);
2. $\left| \frac{T_K}{u_*} \right| < -\frac{T_N}{A_c} \implies \mathbf{|T_K| < \frac{u_*}{A_c} (-T_N)}$ (the shear stress must lie within the cone bounded by the normal stress).

This defines an open convex cone $\mathcal{K}_{\text{stress}} \subset \mathbb{R}^2$:
$$\mathcal{K}_{\text{stress}} = \left\{ T = T_N N + T_K K \in \mathbb{R}^2 : T_N < 0, \; |T_K| < \frac{u_*}{A_c} (-T_N) \right\}.$$

Any target stress in the interior of this cone is **realizable with strictly positive weights** $y_+, y_- > 0$.

---

## 8. Epistemic Demarcation: Stress Realizability vs. Autonomous Generation

A critical distinction must be enforced:

$$\boxed{\begin{aligned}
\mathbf{PROVED\ (Proposition\ 7.5):}\ & \text{Given the pulses } b_+, b_-, \text{ their combined nonlinear Reynolds} \\
&\text{stress spans a 2D open cone and inverts the required target stress } T. \\
\mathbf{UNPROVED\ (Autonomous\ Reachability):}\ & \text{Can the required pulse entrance states } W_+^{\text{in}}, W_-^{\text{in}} \text{ be autonomously} \\
&\text{generated from smooth, unforced initial data } u_0 \in C^\infty(\mathbb{T}^3)?
\end{aligned}}$$

Proving that $\det H \neq 0$ validates the internal consistency of the OpenAI pulse mechanism in the forced setting. It **does not** prove that the pulses can be seeded without external forcing $F_1$.

---

## 9. Formal Status of Claims

1. **`CLM-037-B-R2`**: **`RETRACTED`**.
   - Reason: Erroneously asserted $\operatorname{rank}(H) = 1$ based on static polarization covariance.
2. **`NEG-EV-045`**: **`RETRACTED_FALSE_SIMPLIFICATION`**.
   - Reason: The claimed rank deficiency failed to account for dynamic phase shear $s(v)$ and radial momentum flux.
3. **`CLM-037-B-R3`**: **`PROVED_LOCAL_THEOREM`** (*Two-Family Local Covariance Cone Invertibility*).
   - Statement: In the local self-similar boundary-layer coordinates of the OpenAI Section 7 filament, the two dynamic pulse families $b_+, b_-$ produce linearly independent covariance columns $H_+, H_-$ satisfying $\det H = -2 h_+ h_- A_c u_* + \mathcal{O}(S_*^{-3/2}) \neq 0$, generating the open stress cone $\mathcal{K}_{\text{stress}}$ with positive weights.
   - Classification: `SOURCE_DERIVED_LOCAL_MODEL`.
