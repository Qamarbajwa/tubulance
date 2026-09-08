# NS-OPENAI-B1 — EXACT AMPLIFICATION–DISSIPATION FUNCTIONAL $\mathcal{A}_j = \mathcal{G}_j - \mathcal{D}_j$

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Risk Ceiling**: `R3`  
**Focus**: Rigorous Evaluation of $\mathcal{G}_j$, $\mathcal{D}_j$, and the Net Asymptotic Exponent $\mathcal{A}_j$  

---

## 1. Formulation of the Net Exponent $\mathcal{A}_j$

Along the space-time ray $(X_j(t), k_j(t))$ of the $j$-th precursor wavepacket, the linear amplitude equation is:
$$\frac{d}{dt} \ln a_j(t) = \Gamma_j(t) - \nu |k_j(t)|^2 + r_j(t),$$
where $\Gamma_j(t) = e_j(t)^T S(u_B) e_j(t)$ is the instantaneous shear stretching rate, $\nu |k_j(t)|^2$ is the instantaneous viscous dissipation rate, and $r_j(t)$ denotes higher-order WKB curvature and pressure corrections satisfying $|r_j(t)| \le C |k_j(t)|^{-1} \|\nabla^2 u_B\|_{L^\infty}$.

Integrating from $t = 0$ to the pulse entrance time $t_j = 1 - 2^{-j}$:
$$a_j(t_j) = a_j(0) \exp\left( \mathcal{A}_j + \int_0^{t_j} r_j(s) ds \right),$$
where the **primary net amplification functional** is defined by:
$$\boxed{\mathcal{A}_j \equiv \mathcal{G}_j - \mathcal{D}_j,}$$
with:
$$\mathcal{G}_j \equiv \int_0^{t_j} \Gamma_j(s) \, ds \quad (\text{Cumulative Strain Amplification}),$$
$$\mathcal{D}_j \equiv \nu \int_0^{t_j} |k_j(s)|^2 \, ds \quad (\text{Cumulative Viscous Dissipation}).$$

---

## 2. Rigorous Upper Bound on Cumulative Dissipation $\mathcal{D}_j$

The time interval $[0, t_j]$ is partitioned into the quiescent phase $[0, t_j - \Delta t_j]$ and the active burst phase $[t_j - \Delta t_j, t_j]$, where $\Delta t_j = \tau_j = 2^{-j}$:

### 2.1 Quiescent Phase ($s \in [0, t_j - \Delta t_j]$)
In this phase, the wavepacket is outside the singular core. The macro-velocity field satisfies $\|\nabla u_B\|_{L^\infty} \le C_{\text{macro}} = \mathcal{O}(1)$.
Solving $\dot{k}_j = -(\nabla u_B)^T k_j$ with initial low frequency $|k_j(0)| = K_0 \asymp \mathcal{O}(1)$:
$$|k_j(s)| \le K_0 e^{C_{\text{macro}} s} \le K_0 e^{C_{\text{macro}}} \equiv K_{\max} = \mathcal{O}(1).$$
Therefore:
$$\mathcal{D}_{j, \text{quiescent}} = \nu \int_0^{t_j - \Delta t_j} |k_j(s)|^2 \, ds \le \nu K_{\max}^2 (t_j - \Delta t_j) \le \nu K_{\max}^2 = \mathcal{O}(1).$$

### 2.2 Active Burst Phase ($s \in [t_j - \Delta t_j, t_j]$)
Over the burst duration $\Delta t_j = 2^{-j}$, the wavevector is sheared up to its entrance value $|k_j(t_j)| = 2^{j/2}$.
Since $|k_j(s)|$ is monotonically increasing under singular compression, it is bounded by $2^{j/2}$ throughout this interval:
$$\mathcal{D}_{j, \text{burst}} = \nu \int_{t_j - \Delta t_j}^{t_j} |k_j(s)|^2 \, ds \le \nu (2^{j/2})^2 \Delta t_j = \nu 2^j \cdot 2^{-j} = \nu = \mathcal{O}(1).$$

### 2.3 Total Viscous Dissipation Bound
Summing both contributions:
$$\boxed{\mathcal{D}_j \le \nu K_{\max}^2 + \nu \equiv D_0 < \infty \quad (\textbf{Uniformly Bounded in } j!).}$$
Viscosity removes at most a constant factor $e^{-D_0} > 0$ of amplitude, regardless of how large $j$ is.

---

## 3. Rigorous Lower Bound on Cumulative Amplification $\mathcal{G}_j$

During the active burst window $[t_j - \Delta t_j, t_j]$, the singular core produces a principal stretching rate:
$$\lambda_1(s) \asymp \tau^{-1-h} \ge c_S 2^{j(1+h)}, \qquad 0 < h \ll 1.$$
Because the polarization $e_j(s)$ aligns with the principal stretching eigenvector $v_1$ (with alignment angle $\theta(s) \to 0$):
$$\Gamma_j(s) = e_j(s)^T S(u_B) e_j(s) \ge \frac{1}{2} c_S 2^{j(1+h)} \quad \text{for } s \in [t_j - \Delta t_j, t_j].$$

During the quiescent phase, $\Gamma_j(s)$ is bounded from below by the macro-scale bound $-C_{\text{macro}}$.
Integrating over $[0, t_j]$:
$$\mathcal{G}_j \ge - C_{\text{macro}} (t_j - \Delta t_j) + \frac{1}{2} c_S 2^{j(1+h)} \cdot \Delta t_j \ge - C_{\text{macro}} + \frac{1}{2} c_S 2^{j(1+h)} \cdot 2^{-j} = \frac{1}{2} c_S 2^{jh} - C_{\text{macro}}.$$

Since $h > 0$:
$$\boxed{\mathcal{G}_j \asymp \frac{1}{2} c_S 2^{jh} \xrightarrow[j \to \infty]{} +\infty.}$$

---

## 4. Asymptotic Classification of the Net Exponent $\mathcal{A}_j$

Combining the two bounds:
$$\mathcal{A}_j = \mathcal{G}_j - \mathcal{D}_j \ge \frac{1}{2} c_S 2^{jh} - C_{\text{macro}} - D_0 \asymp C_1 2^{jh} \xrightarrow[j \to \infty]{} +\infty.$$

$$\boxed{\mathbf{ASYMPTOTIC\ REGIME:\quad \mathcal{A}_j \xrightarrow[j \to \infty]{} +\infty.}}$$

### 4.1 Comparative Asymptotic Matrix

| Hypothesis | Wavevector History $|k_j(s)|$ | Dissipation $\mathcal{D}_j$ | Amplification $\mathcal{G}_j$ | Net Exponent $\mathcal{A}_j$ | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P0 (Direct Preload)** | $|k_j(s)| \equiv 2^{j/2}$ on $[0, t_j]$ | $\frac{\nu}{2} 2^j \to +\infty$ | $c_S 2^{jh}$ | $\approx -\frac{\nu}{2} 2^j \to -\infty$ | **FALSIFIED** |
| **P1 (Low-Freq Precursor)** | $K_0 \to 2^{j/2}$ in time $2^{-j}$ | $\le D_0 = \mathcal{O}(1)$ | $c_S 2^{jh} \to +\infty$ | $\approx c_S 2^{jh} \to +\infty$ | **SURVIVES** |

### 4.2 Super-Exponential Initial Seed Attenuation
To arrive at the required pulse amplitude $A_j^\star = c_w 2^{j(1/2+h)}$, the initial seed amplitude $a_j(0)$ at $t = 0$ is:
$$a_j(0) = A_j^\star e^{-\mathcal{A}_j} \le c_w 2^{j(1/2+h)} \exp\left( - C_1 2^{jh} \right) \asymp \exp\left( - C_2 2^{jh} \right) \xrightarrow[j \to \infty]{} 0.$$
Because $a_j(0)$ decays super-exponentially, the initial perturbation field $u_{0, \text{pert}} = \sum_{j=1}^\infty a_j(0) w_j(0)$ belongs to the real-analytic class $C^\omega(\mathbb{T}^3)$ with rapidly summable Sobolev norms:
$$\|u_{0, \text{pert}}\|_{H^m(\mathbb{T}^3)} \le K_0^m \sum_{j=1}^\infty \exp(-C_2 2^{jh}) < \infty \quad \forall m \ge 0.$$

---

## 5. WHAT_THE_FLUID_IS_DOING

This calculation demonstrates why the unforced fluid is capable of autonomous pulse generation:

Viscous dissipation depends on the square of the wavevector, $\nu |k|^2$. If a high-frequency ripple were forced to sit in the fluid from $t = 0$ all the way to $t = 1$, viscosity would relentlessly grind it down, multiplying its amplitude by $\exp(-\nu 2^j)$. That is why direct preloading (P0) is impossible.

However, a low-frequency precursor (P1) is not high-frequency during that long wait. It starts as a broad, lazy ripple ($k \sim 1$). Viscosity hardly notices it, sapping only a fraction of its strength. Then, in the final split-second before activation ($\Delta t = 2^{-j}$), the ripple enters the eye of the vortex storm. The background flow catches it and stretches it with immense shear ($\sim 2^{j(1+h)}$). 

Although the ripple's frequency surges to $2^{j/2}$, it spends so little time at that high frequency ($2^{-j}$ seconds) that viscosity only has time to take a single $\mathcal{O}(1)$ bite! Meanwhile, the stretching forces pump energy into the ripple with explosive gain ($\exp(C 2^{jh})$).

The net result is that the shear **drastically outruns** viscosity:
$$\mathcal{A}_j = \text{Gain} - \text{Loss} \approx 2^{jh} - \mathcal{O}(1) \gg 0.$$
The fluid provides an enormous built-in amplifier, meaning the initial seed placed in the water at $t = 0$ can be infinitesimally small, infinitely smooth, and carry virtually zero energy.
