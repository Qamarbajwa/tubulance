# TP2-G6-C1: RELATIVE SEPARATION ENERGY AND ORIENTATION DYNAMICS

## Work Package WP5: Energy, Log-Separation, and Unit-Vector Evolution

---

### 1. Purpose and Geometric Quantities

This work package derives the exact equations of motion for:
1. **Relative Separation Energy**: $R_s = |\delta A_s|^2 = \delta A_s \cdot \delta A_s$.
2. **Radial Distance**: $r_s = \sqrt{R_s} = |\delta A_s|$.
3. **Logarithmic Separation**: $\log r_s = \frac{1}{2} \log R_s$.
4. **Unit Relative Orientation Vector**: $e_s = \frac{\delta A_s}{r_s} \in \mathbb{S}^2$ (for $r_s > 0$).

All constants, Itô corrections, and geometric tensor projections are verified explicitly in dimension $d = 3$ for both Coupling C-SYNC and Coupling C-IND.

---

### 2. Relative Separation Energy Dynamics ($R_s = |\delta A_s|^2$)

#### 2.1 Synchronous Coupling (C-SYNC)
From WP3, $d(\delta A_s) = - \mathcal{S}_s \delta A_s ds$. Since this is a pathwise ODE:
$$
\frac{d}{ds} R_s = \frac{d}{ds} (\delta A_s^T \delta A_s) = 2 \delta A_s^T \left( \frac{d \delta A_s}{ds} \right) = - 2 \delta A_s^T \mathcal{S}_s \delta A_s.
$$
Recall the decomposition $\mathcal{S}_s = \bar{S}_s + \bar{\Omega}_s$ into symmetric strain $\bar{S}_s$ and skew-symmetric rotation $\bar{\Omega}_s$.
For any vector $v$, $v^T \bar{\Omega}_s v = 0$. Therefore:
$$
\boxed{
\frac{d}{ds} R_s = - 2\, \delta A_s^T \bar{S}_s\, \delta A_s = - 2\, (e_s^T \bar{S}_s e_s) R_s.
}
$$
**Key Finding**: In C-SYNC, the relative energy is governed **exclusively by the path-averaged strain tensor** $\bar{S}_s$. Rotational vorticity $\bar{\Omega}_s$ produces no energy change.

#### 2.2 Independent Coupling (C-IND)
Under C-IND, $\delta A_s$ satisfies the Itô SDE:
$$
d(\delta A_s) = - \delta u_s\, ds + \sqrt{4\nu}\, dB_s, \qquad \delta u_s = u(A_s^{(2)}, s) - u(A_s^{(1)}, s).
$$
Applying Itô's formula to the scalar function $f(x) = |x|^2 = \sum_{i=1}^3 x_i^2$:
$$
\frac{\partial f}{\partial x_i} = 2x_i, \qquad \frac{\partial^2 f}{\partial x_i \partial x_j} = 2\delta_{ij}.
$$
The stochastic differential is:
$$
d R_s = 2 \sum_{i=1}^3 \delta A_s^i\, d(\delta A_s^i) + \frac{1}{2} \sum_{i=1}^3 \sum_{j=1}^3 2\delta_{ij}\, d(\delta A_s^i)\, d(\delta A_s^j).
$$
Evaluating the quadratic variation:
$$
d(\delta A_s^i)\, d(\delta A_s^j) = (\sqrt{4\nu}\, dB_s^i)(\sqrt{4\nu}\, dB_s^j) = 4\nu \delta_{ij}\, ds.
$$
Thus, the second-order Itô trace correction is:
$$
\sum_{i=1}^3 4\nu\, ds = 3 \times (4\nu)\, ds = 12\nu\, ds.
$$
Combining terms:
$$
\boxed{
d R_s = - 2\, \delta A_s \cdot \delta u_s\, ds + 12\nu\, ds + 4\sqrt{\nu}\, \delta A_s \cdot dB_s.
}
$$
Expressed in terms of path-averaged strain $\bar{S}_s$:
$$
d R_s = \left[ - 2 (e_s^T \bar{S}_s e_s) R_s + 12\nu \right] ds + 4\sqrt{\nu}\, r_s\, (e_s \cdot dB_s).
$$
**Key Constant Confirmation**: The positive drift term is strictly $+12\nu ds$, representing the isotropic 3D relative Brownian energy growth.

---

### 3. Radial Separation and Logarithmic Distance Dynamics

#### 3.1 Synchronous Coupling (C-SYNC)
Since $R_s = r_s^2$, $\frac{d R_s}{ds} = 2 r_s \frac{dr_s}{ds}$. Substituting:
$$
\boxed{
\frac{d r_s}{ds} = - (e_s^T \bar{S}_s e_s)\, r_s.
}
$$
Dividing by $r_s$ (on the set $r_s > 0$):
$$
\boxed{
\frac{d \log r_s}{ds} = - e_s^T \bar{S}_s e_s.
}
$$
Integrating backwards from $t$ to $s$:
$$
\log r_s = \log |h| + \int_s^t e_\tau^T \bar{S}_\tau e_\tau\, d\tau \implies r_s = |h| \exp\left( \int_s^t e_\tau^T \bar{S}_\tau e_\tau\, d\tau \right).
$$

#### 3.2 Independent Coupling (C-IND)
For C-IND, we apply Itô's formula to $r_s = \sqrt{R_s}$:
$$
f(R) = R^{1/2}, \qquad f'(R) = \frac{1}{2} R^{-1/2} = \frac{1}{2r}, \qquad f''(R) = - \frac{1}{4} R^{-3/2} = - \frac{1}{4r^3}.
$$
The Itô correction is:
$$
\frac{1}{2} f''(R_s) (d R_s^{\text{mart}})^2 = \frac{1}{2} \left(-\frac{1}{4r_s^3}\right) (4\sqrt{\nu} r_s)^2 ds = - \frac{1}{8r_s^3} (16\nu r_s^2) ds = - \frac{2\nu}{r_s}\, ds.
$$
The first-order drift contribution is:
$$
f'(R_s) \left( -2 r_s (e_s^T \bar{S}_s e_s) + 12\nu \right) ds = \left( - (e_s^T \bar{S}_s e_s) r_s + \frac{6\nu}{r_s} \right) ds.
$$
Summing the drift terms:
$$
\left( \frac{6\nu}{r_s} - \frac{2\nu}{r_s} \right) ds = + \frac{4\nu}{r_s}\, ds.
$$
Therefore:
$$
\boxed{
d r_s = \left[ - (e_s^T \bar{S}_s e_s) r_s + \frac{4\nu}{r_s} \right] ds + \sqrt{4\nu}\, (e_s \cdot dB_s).
}
$$
Now for logarithmic separation $\log r_s = \frac{1}{2} \log R_s$, using Itô's formula with $g(R) = \frac{1}{2} \log R$:
$$
g'(R) = \frac{1}{2R}, \qquad g''(R) = - \frac{1}{2R^2}.
$$
The drift is:
$$
\frac{1}{2R_s} \left( -2 R_s (e_s^T \bar{S}_s e_s) + 12\nu \right) - \frac{1}{4R_s^2} (16\nu R_s) = - e_s^T \bar{S}_s e_s + \frac{6\nu}{r_s^2} - \frac{4\nu}{r_s^2} = - e_s^T \bar{S}_s e_s + \frac{2\nu}{r_s^2}.
$$
Therefore:
$$
\boxed{
d \log r_s = \left[ - e_s^T \bar{S}_s e_s + \frac{2\nu}{r_s^2} \right] ds + \frac{\sqrt{4\nu}}{r_s}\, (e_s \cdot dB_s).
}
$$
**Crucial Geometric Note**: The term $+ \frac{2\nu}{r_s^2} ds$ represents the centrifugal drift in 3D: Brownian motion pushes the two particles apart when their separation $r_s$ becomes small.

---

### 4. Unit Orientation Dynamics ($e_s \in \mathbb{S}^2$)

For Coupling C-SYNC, differentiating $e_s = \frac{\delta A_s}{r_s}$:
$$
\frac{d e_s}{ds} = \frac{1}{r_s} \frac{d\delta A_s}{ds} - \frac{\delta A_s}{r_s^2} \frac{dr_s}{ds} = \frac{-\mathcal{S}_s \delta A_s}{r_s} - e_s \left( - e_s^T \bar{S}_s e_s \right).
$$
Substituting $\mathcal{S}_s = \bar{S}_s + \bar{\Omega}_s$:
$$
\boxed{
\frac{d e_s}{ds} = - \left[ \bar{S}_s e_s - (e_s^T \bar{S}_s e_s) e_s \right] - \bar{\Omega}_s e_s.
}
$$
- **Strain Alignment**: The term $- [\bar{S}_s e_s - (e_s^T \bar{S}_s e_s) e_s] = - (I - e_s \otimes e_s) \bar{S}_s e_s$ projects the strain onto the tangent space of the unit sphere $\mathbb{S}^2$, driving $e_s$ toward the eigenvectors of $\bar{S}_s$.
- **Vorticity Precession**: The term $- \bar{\Omega}_s e_s = \frac{1}{2} \bar{\omega}_s \times e_s$ rotates $e_s$ around the local vorticity vector $\bar{\omega}_s$.

---

### 5. Collision and Zero-Separation Analysis

Define the collision stopping time:
$$
\tau_0 = \inf \left\{ s \in [0, t] : |\delta A_s| = 0 \right\}.
$$

#### 5.1 Synchronous Coupling (C-SYNC)
- Under $u \in C^1(\mathbb{T}^3)$, $\mathcal{S}_s$ is uniformly bounded: $\|\mathcal{S}_s\| \le \|\nabla u\|_{L^\infty} < \infty$.
- The solution to $\frac{d}{ds} \delta A_s = - \mathcal{S}_s \delta A_s$ is given by the time-ordered matrix exponential $\delta A_s = \Phi(s, t) h$.
- Because $\det(\Phi(s, t)) = \exp(-\int_s^t \operatorname{tr}(\mathcal{S}_\tau) d\tau) = 1$, the matrix $\Phi(s, t)$ is non-singular for all $s \in [0, t]$.
- **Conclusion**: For any initial $h \ne 0$, $\delta A_s \ne 0$ for all $s \in [0, t]$. **Collision cannot occur**: $\tau_0 = -\infty$ (or $\tau_0 < 0$). Trajectories never intersect.

#### 5.2 Independent Coupling (C-IND)
- Under C-IND, $\delta A_s$ is a 3D diffusion with non-degenerate diffusion matrix $4\nu I$.
- By Kakutani's classical theorem (1944) on Brownian paths in $\mathbb{R}^d$ ($d \ge 3$):
  *Points are polar sets for 3D Brownian motion*.
- The probability that two independent Brownian motions collide in 3D is strictly zero:
  $$
  \mathbb{P}(\tau_0 \in [0, t]) = 0.
  $$
- The centrifugal drift $+ \frac{4\nu}{r_s}$ acts as a repulsive potential at the origin, ensuring almost sure avoidance of collision.
- **Conclusion**: The orientation vector $e_s$ and logarithmic distance $\log r_s$ are almost surely well-defined for all $s \in [0, t]$.
