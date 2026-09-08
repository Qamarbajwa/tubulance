# NS-EXT-OPENAI-001-R1 — DIRECT TORUS TRANSFER RE-AUDIT

**Programme**: `EXTERNAL_ASSIMILATION_AND_TRANSFER`  
**Subprogramme**: `OPENAI_NAVIER_STOKES_BLOWUP_ASSIMILATION`  
**Target Domain**: Periodic Flat 3-Torus $\mathbb{T}^3 = \mathbb{R}^3 / \mathbb{Z}^3$  

---

## 1. Taxonomic Error Identified in `NS-EXT-OPENAI-001`

In increment `NS-EXT-OPENAI-001`, the direct periodic torus formulation was claimed to provide *"100% elimination of $F_3$"*.

This assertion conflated the global spatial cutoff at infinity with local matching and gluing errors that arise within the periodic domain.
Under rigorous re-audit, the errors generated during construction must be decomposed into **six distinct geometric and analytical operations**.

---

## 2. Six-Component Breakdown of Localization and Gluing Errors

| Operation # | Geometric / Analytical Operation | Mathematical Mechanism of Error Generation | Status on Direct $\mathbb{T}^3$ | Governing Classification |
| :--- | :--- | :--- | :--- | :--- |
| **G1** | **Whole-Space Spatial Cutoff** | Commutator terms $[(u\cdot\nabla), \chi]u - \nu [\Delta, \chi]u$ used to enforce spatial decay as $|x| \to \infty$ in $\mathbb{R}^3$. | Completely absent on compact manifold $\mathbb{T}^3$; no boundary at infinity. | `REMOVED_ON_DIRECT_TORUS` |
| **G2** | **Radial Transition Matching** | Matching between inner self-similar core ($r \le R_0 \ell_r$) and intermediate annulus ($r \sim \ell_r$). | Occurs locally at scale $r \sim \tau^{1/2} \ll 1$; independent of global torus topology. | `PERSISTS_ON_TORUS` |
| **G3** | **Annular Pulse Realization** | Discrepancy between target stress tensor $T$ and discrete sum of wave fluxes $\sum \langle w_j \otimes w_j \rangle$. | Local wavepacket geometry in narrow rings; unaffected by global boundary. | `PERSISTS_ON_TORUS` |
| **G4** | **Temporal Boundary Cutoffs** | Truncation of forcing and wavepackets at initial time $t = 0$ and post-blowup $t > T_*$. | Time line $[0, T_*)$ is identical on $\mathbb{R}^3$ and $\mathbb{T}^3$. | `PERSISTS_ON_TORUS` |
| **G5** | **Periodic Lattice Compatibility** | Compatibility of exterior azimuthal flow $u_\theta(r)$ with periodic boundary conditions $x_i \sim x_i + 1$. | Cylindrical symmetry $\partial_\theta \equiv 0$ is incompatible with cubic torus symmetry; requires periodic corner transition layer. | `PERSISTS_ON_TORUS` |
| **G6** | **Pressure Zero-Mean Normalization** | Ensuring $\int_{\mathbb{T}^3} p(x, t) dx = 0$ to fix the gauge on compact $\mathbb{T}^3$. | Gauge fixing introduces spatial-mean adjustment $\bar{p}(t) = \frac{1}{|\mathbb{T}^3|}\int p dx$. Does not generate force if $p$ is periodic. | `REMOVED_ON_DIRECT_TORUS` |

---

## 3. Detailed Audit of Periodic Compatibility (G5)

A major technical subtlety overlooked in `NS-EXT-OPENAI-001` is **G5: Periodic Lattice Compatibility**.
- In $\mathbb{R}^3$, the exterior solution $u^{\text{ext}} = u_\theta(r, t) e_\theta$ extends to arbitrary radius $r \to \infty$ with circular symmetry.
- On the periodic torus $\mathbb{T}^3 = [0, 1)^3$, circular symmetry is broken by the cubic periodic boundary:
  $$\text{At } x = \pm 1/2, \ y = 0 \implies r = 1/2.$$
  $$\text{At corners } x = \pm 1/2, \ y = \pm 1/2 \implies r = \sqrt{2}/2 \approx 0.707.$$
- One **cannot** simply wrap a purely axisymmetric swirling flow $u_\theta(r) e_\theta$ onto $\mathbb{T}^3$ without creating an $\mathcal{O}(1)$ velocity and stress discontinuity at the boundary of the fundamental cell!
- To embed the flow into $\mathbb{T}^3$, an additional spatial transition layer must be constructed that transitions $u_\theta(r) e_\theta$ into a periodic shear lattice (such as an array of 4 counter-rotating Taylor–Green vortex cells).
- This transition layer generates non-zero commutator and residual forcing on the torus.

---

## 4. Synthesis of Direct Torus Transfer

$$\boxed{\begin{aligned}
\textbf{Corrected Assessment: } &\text{Working directly on } \mathbb{T}^3 \text{ eliminates only G1 (whole-space infinity cutoff)} \\
&\text{and G6 (pressure gauge). It does NOT eliminate G2 (radial matching),} \\
&\text{G3 (annular stress realization), G4 (temporal cutoffs), or G5 (periodic lattice} \\
&\text{cubic compatibility). Therefore, } F_3 \text{ is only partially simplified, NOT 100\% eliminated.}
\end{aligned}}$$
