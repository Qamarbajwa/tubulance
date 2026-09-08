# NS-OPENAI-B1-R1 — ENERGY BUDGET PURIFICATION, ANALYTICITY, AND CLOCK SENSITIVITY AUDIT

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-R1 — Autonomous Precursor Cascade Realizability Re-Audit`  
**Standard**: `Mathematical Research Constitution v1.0.1`  
**Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Risk Ceiling**: `R3`  
**Focus**: Rigorous Clean-Up of Energy Identities, Elimination of Unjustified Constants, Analyticity Firewall, and Clock Stability Audit  

---

## 1. Energy Budget Purification (Removal of Arbitrary Numerical Constants)

In `NS_OPENAI_B1_ENERGY_BUDGET.md`, the analysis used ungrounded numerical claims such as:
> *"The background flow has initial energy $E_B(0) \approx 100 \dots$ Total cascade energy is $\approx 3.65 \ll 100$."*

### 1.1 Strict Constitutional Correction
Under MRC Article 2.1, mathematical assertions must be derived rigorously from explicit initial data or scaling laws, not illustrative numbers.

1. **Purification of the Energy Identity**:
   For any smooth unforced solution on $\mathbb{T}^3$ with $f \equiv 0$:
   $$\frac{1}{2} \|u(t)\|_{L^2}^2 + \nu \int_0^t \|\nabla u(s)\|_{L^2}^2 \, ds = \frac{1}{2} \|u_0\|_{L^2}^2 \equiv E_0 < \infty.$$
2. **True Coupled Decomposition**:
   Writing $u = u_B + \sum_j w_j + v$, the kinetic energy contains **cross-terms**:
   $$E(t) = \frac{1}{2}\|u_B(t)\|_2^2 + \sum_j \frac{1}{2}\|w_j(t)\|_2^2 + \sum_{i \ne j} \int w_i \cdot w_j \, dx + \sum_j \int u_B \cdot w_j \, dx + \dots$$
   - In `NS-OPENAI-B1`, the cross-terms $\int u_B \cdot w_j dx$ and $\int w_i \cdot w_j dx$ were neglected.
   - During the active burst, $w_j$ reaches amplitude $A_j^\star \sim 2^{j(1/2+h)}$, while $u_B \sim 2^{j(1/2+h)}$.
   - The cross-term $\int u_B \cdot w_j dx$ is of the **exact same scaling order** as the pulse energy itself:
     $$\left| \int_{\operatorname{supp}(w_j)} u_B \cdot w_j \, dx \right| \asymp \|u_B\|_{L^\infty} \|w_j\|_{L^\infty} \operatorname{Vol}_j \asymp 2^{j(1+2h)} \cdot 2^{-j(3/2-h)} = 2^{j(3h - 1/2)}.$$
   - Because $3h - 1/2 < 0$, the cross-term also decays to zero as $j \to \infty$.
   - However, for small $j$, the cross-terms create $\mathcal{O}(1)$ energy fluctuations that alter the background dissipation rate $\nu \|\nabla u_B\|_2^2$.
3. **Formal Resolution**:
   All ungrounded constants ($E_B(0) \approx 100$, $\Delta E \approx 3.65$) are hereby **expunged**.
   The valid mathematical theorem is:
   $$\boxed{\text{If } h < 1/6, \text{ the individual pulse energy } \mathcal{E}(W_j^\star) \asymp 2^{j(3h-1/2)} \to 0 \text{ is subcritical.}}$$

---

## 2. Smoothness vs Analyticity Audit (Assertion A13)

In `NS-OPENAI-B1`, Assertion A13 claimed that $u_0 \in C^\omega(\mathbb{T}^3)$ (real-analytic) because:
$$\sum_{j=1}^\infty \|w_j(0)\|_{H^m} < \infty \quad \forall m \ge 0.$$

### 2.1 The Sobolev vs Gevrey Distinction
Belonging to $\bigcap_{m=0}^\infty H^m(\mathbb{T}^3)$ proves that $u_0$ is **smooth ($C^\infty$)**, but does **NOT** prove that $u_0$ is **real-analytic ($C^\omega$)**!
A function $f \in C^\infty(\mathbb{T}^3)$ is real-analytic if and only if there exists a uniform radius of analyticity $\rho > 0$ such that:
$$\|f\|_{H^m} \le C \frac{m!}{\rho^m} \quad \forall m \ge 0 \iff \sum_{k \in \mathbb{Z}^3} e^{2\rho |k|} |\widehat{f}(k)|^2 < \infty.$$

In `NS_OPENAI_B1_INFINITE_CASCADE_AUDIT.md`:
$$\|w_j(0)\|_{H^m} \le C_m a_j(0) 2^{j m / 2} \sim 2^{j m / 2} \exp\left( - C_1 2^{jh} \right).$$
Summing over $j$:
$$\|u_{0, \text{pert}}\|_{H^m} \le \sum_{j=1}^\infty 2^{j m / 2} \exp\left( - C_1 2^{jh} \right).$$
The maximum of $g(x) = 2^{x m / 2} \exp(-C_1 2^{x h})$ occurs at $2^{x h} = \frac{m \ln 2}{2 C_1 h}$.
Substituting this peak value gives:
$$\|u_{0, \text{pert}}\|_{H^m} \sim \left( \frac{m}{C} \right)^{m / (2h)} \sim (m!)^{1 / (2h)}.$$
- If $h = 0.05 = 1/20$, then $1 / (2h) = 10$!
- The Sobolev norms grow like $(m!)^{10}$!
- This corresponds to **Gevrey class $s = 10$**, which is **strictly non-analytic** ($s > 1$)!

$$\boxed{\mathbf{ANALYTICITY\ REFUTED:}\quad u_{0, \text{pert}} \text{ is } C^\infty \text{ (Gevrey class } s = 1/(2h) = 10\text{), NOT } C^\omega!}$$
Assertion A13 is formally **retracted**.

---

## 3. Autonomous Clock Sensitivity Re-Audit (Assertion A14)

In `NS-OPENAI-B1`, Assertion A14 claimed the clock is natively encoded by initial radial positions: $r_{0, j} \leftrightarrow t_j$.

### 3.1 The Hyper-Singular Clock Sensitivity
The background radial inflow near the singularity is:
$$u_r(r, t) \asymp - \frac{c_r}{\sqrt{t_* - t}} = - c_r \tau^{-1/2}.$$
Integrating the trajectory $r(t)$ from $r_{0, j}$ to $r_j = 2^{-j/2}$ over the interval $\tau_j = 2^{-j}$:
$$r_{0, j} - r_j = \int_{t_j - \tau_j}^{t_j} |u_r(s)| \, ds \asymp c_r \sqrt{\tau_j} = c_r 2^{-j/2}.$$
Taking the derivative of arrival time $t_j$ with respect to initial position $r_{0, j}$:
$$\frac{\partial t_j}{\partial r_{0, j}} = \frac{1}{|u_r(r_{0, j}, t_j)|} \asymp \sqrt{\tau_j} = 2^{-j/2}.$$
Inverting this to find the sensitivity of arrival time to spatial placement:
$$\boxed{\frac{\partial \tau_j}{\partial r_{0, j}} \asymp 2^{j/2} \xrightarrow[j \to \infty]{} +\infty!}$$

An infinitesimal spatial placement error $\delta r_0 \sim 2^{-j}$ produces an arrival time error:
$$\delta t_j \asymp 2^{j/2} \delta r_0 \asymp 2^{-j/2} \gg \tau_j = 2^{-j}!$$
The error in arrival time is **drastically larger than the duration of the burst itself ($\Delta t_j = 2^{-j}$)**!
The ripple arrives completely out of sync with the core contraction.
Without active feedback phase-locking, the "space is the clock" mechanism is **structurally unstable**.
Assertion A14 is restored to **`HEURISTIC_UNSTABLE`**.
