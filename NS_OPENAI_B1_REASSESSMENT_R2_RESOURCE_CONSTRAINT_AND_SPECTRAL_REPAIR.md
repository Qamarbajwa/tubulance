# Resource Constraint Definition and Spectral Lower Bound Repair

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R2`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Classification**: `PROSPECTIVE_CORRECTION`  
**Corrects**: R1 spectral lower bound argument, missing cost definition

---

## 1. The Missing Resource Constraint

### 1.1 What R1 Failed to Define

The R1 argument (Sections 4–5 of `NS_OPENAI_B1_REASSESSMENT_UNCERTAINTY_BARRIER.md`) jumps directly from "backward cost diverges" to "no-go". The intermediate step — defining a finite energy budget and proving it is exceeded — was omitted.

### 1.2 Proper Definition

Let $\mathcal{E}_0$ be the total energy of the smooth initial datum $u_0 \in C^\infty(\mathbb{T}^3)$ for the full unforced Navier–Stokes system. The perturbation $w_0$ seeding the $j$-th pulse must satisfy:
$$\|w_0\|_{L^2}^2 \leq \mathcal{E}_0.$$

**Definition 1.1 (Realization Cost)**:  
For a target $W_j^\star$ at time $t_j$, the **minimum realization cost** under the linearized operator $\mathcal{U}(t_j, 0)$ is:
$$\mathfrak{C}_{\varepsilon, j} \equiv \inf \left\{ \|w_0\|_{L^2} : w_0 \in L^2_{\mathrm{div}}(\mathbb{T}^3), \; \|\mathcal{U}(t_j, 0) w_0 - W_j^\star\|_{L^2} \leq \varepsilon \right\}.$$

**Definition 1.2 (Budget Violation)**:  
The autonomous realization is **budget-infeasible** if:
$$\mathfrak{C}_{\varepsilon, j} > \mathcal{E}_0^{1/2} \quad \text{for all } \varepsilon < \varepsilon_{\mathrm{tol}}.$$

### 1.3 Finite-but-Large versus Genuinely Infinite

For each fixed $j$, $\mathfrak{C}_{\varepsilon, j}$ is a **finite** positive number (by the dense range theorem of the previous section). The barrier is that:
$$\mathfrak{C}_{\varepsilon, j} \to +\infty \quad \text{as } j \to \infty,$$
not that $\mathfrak{C}_{\varepsilon, j} = \infty$ for any fixed $j$.

Consequently, the conclusion is:
- At any **fixed** scale $j$, the pulse can be approximately realized with finite (though possibly enormous) initial energy.
- The **cascade** requires all scales $j \leq J$ simultaneously, so the total budget $\sum_j \|w_{0,j}\|_{L^2}^2$ diverges.
- The physically relevant obstruction is the **growth rate** of $\mathfrak{C}_{\varepsilon, j}$, not a single-scale impossibility.

---

## 2. Spectral Lower Bound Repair

### 2.1 The Gap in R1

The R1 divergence integral (Section 4 of the Gramian document) uses:
$$\mathcal{I}_j \geq \exp\left( \inf_{\xi \in P_j^c} Q_{t_j}(\xi) \right) \int_{P_j^c} |\widehat{W_j^\star}(\xi)|^2 \, d\xi.$$

But $P_j^c = \{ \xi : Q_{t_j}(\xi) > C_{\max} \}$, so $\inf_{\xi \in P_j^c} Q_{t_j}(\xi) = C_{\max}$. This only gives:
$$\mathcal{I}_j \geq e^{C_{\max}} \cdot \delta_j \|W_j^\star\|_{L^2}^2,$$
which is a **constant** (independent of $j$) times the leakage fraction. The claimed super-exponential divergence does NOT follow from this step alone.

### 2.2 The Correct Argument: High-Cost Sub-Region

Define the **high-cost region** $H_j$ with an explicit threshold $L_j \gg C_{\max}$:
$$H_j \equiv \left\{ \xi \in \mathbb{R}^3 : Q_{t_j}(\xi) \geq L_j \right\}, \qquad L_j = \frac{\nu}{8} 2^{-jh} \exp(2 \cdot 2^{jh}).$$

This $L_j$ is chosen so that any mode with $|\xi_\perp| \geq \frac{1}{2} 2^{j/2}$ satisfies $Q_{t_j}(\xi) \geq L_j$, since:
$$Q_{t_j}(\xi) \geq \lambda_\perp |\xi_\perp|^2 \geq \nu 2^{-j(1+h)} e^{2 \cdot 2^{jh}} \cdot \frac{1}{4} 2^j = \frac{\nu}{4} 2^{-jh} e^{2 \cdot 2^{jh}} \geq L_j.$$

Now the lower bound becomes:
$$\mathcal{I}_j \geq \exp(L_j) \int_{H_j} |\widehat{W_j^\star}(\xi)|^2 \, d\xi.$$

### 2.3 Spectral Mass in $H_j$

By the Heisenberg–Nazarov uncertainty bound (Lemma 3.1 of the CLM-038 document), for a compactly-supported envelope with transverse width $\delta r_j \asymp 2^{-j/2}$:
$$\int_{|\xi_\perp| \geq \frac{1}{2} 2^{j/2}} |\widehat{W_j^\star}(\xi)|^2 \, d\xi \geq c_V \|W_j^\star\|_{L^2}^2 > 0.$$

Since $\{ \xi : |\xi_\perp| \geq \frac{1}{2} 2^{j/2} \} \subset H_j$, we have:
$$\int_{H_j} |\widehat{W_j^\star}(\xi)|^2 \, d\xi \geq c_V \|W_j^\star\|_{L^2}^2.$$

### 2.4 Corrected Divergence

$$\boxed{\mathcal{I}_j \geq c_V \|W_j^\star\|_{L^2}^2 \exp\left( \frac{\nu}{8} 2^{-jh} \exp(2 \cdot 2^{jh}) \right) \to +\infty.}$$

The divergence is now established via the **explicitly constructed high-cost region** $H_j$, not via an incorrect infimum over all of $P_j^c$.

---

## 3. Corrected Cost Lower Bound

Combining the repaired spectral bound with the dense range framework:

**Theorem 3.1 (Corrected Cost Divergence)**:  
Let $W_j^\star$ be any divergence-free target pulse localized in an annular filament of thickness $\delta r_j \asymp 2^{-j/2}$, within the exact affine benchmark. Then:

$$\mathfrak{C}_{\varepsilon, j}^2 \geq c_V \|W_j^\star\|_{L^2}^2 \exp\left( \frac{\nu}{8} 2^{-jh} \exp(2 \cdot 2^{jh}) \right) - \varepsilon^2.$$

For $j$ sufficiently large:
$$\ln \mathfrak{C}_{\varepsilon, j} \geq \frac{\nu}{16} 2^{-jh} \exp(2 \cdot 2^{jh}) + \mathcal{O}(j) \to +\infty \quad \text{super-exponentially.}$$

**Proof context**: EXACT_AFFINE_BENCHMARK only. The background $u_B = A(t)x$ is NOT periodic on $\mathbb{T}^3$.

---

## 4. Gramian Reconstruction Notes

### 4.1 Fourier Radius vs Physical Radius

The R1 document sometimes compares spectral semi-axis $R_\perp$ (a Fourier-space quantity with units $\mathrm{length}^{-1}$) directly with physical width $\delta r_j$ (units of length). The correct comparison is:

- Physical width: $\delta r_j \asymp 2^{-j/2}$ (in metres)
- Fourier bandwidth: $\Delta k_\perp \gtrsim 1/\delta r_j \asymp 2^{j/2}$ (in $\mathrm{m}^{-1}$)
- Gramian semi-axis: $R_\perp \asymp \sqrt{C_0 / \lambda_\perp}$ (in $\mathrm{m}^{-1}$)

The mismatch ratio is:
$$\frac{\Delta k_\perp}{R_\perp} \asymp \frac{2^{j/2}}{2^{j(1+h)/2} \exp(-2^{jh})} = \frac{\exp(2^{jh})}{2^{jh/2}} \to +\infty.$$

This confirms that the physical bandwidth **vastly exceeds** the Gramian's admissible radius. The inequality is correct; the issue is only that one must state both sides in the same units (wavenumber, not mixed length/wavenumber).

### 4.2 Factor-of-Two Specification

The precise Gramian eigenvalue for the transverse direction is:
$$\lambda_\perp = 2\nu \int_{t_j^-}^{t_j} e^{2\Sigma(t_j, s)} \, ds.$$

With $\sigma(s) = \sigma_j$ constant over $[t_j^-, t_j]$ of duration $\Delta t_j = 2^{-j}$:
$$\lambda_\perp = 2\nu \cdot \frac{e^{2\sigma_j \Delta t_j} - 1}{2\sigma_j} = \frac{\nu}{\sigma_j} \left( e^{2\Sigma_j} - 1 \right).$$

With $\sigma_j = 2^{j(1+h)}$ and $\Sigma_j = \sigma_j \Delta t_j = 2^{jh}$:
$$\lambda_\perp = \frac{\nu}{2^{j(1+h)}} \left( e^{2 \cdot 2^{jh}} - 1 \right) = \nu 2^{-j(1+h)} \left( e^{2 \cdot 2^{jh}} - 1 \right).$$

For $j \geq 1$: $e^{2 \cdot 2^{jh}} - 1 \geq \frac{1}{2} e^{2 \cdot 2^{jh}}$, so the asymptotic $\lambda_\perp \asymp \nu 2^{-j(1+h)} e^{2 \cdot 2^{jh}}$ is correct within a factor of 2.
