# TH6 LITERATURE THEOREM COMPARISON: CANDIDATE BOUND B1

## 1. Mathematical Statement of Candidate B1
For any smooth solution of 3D incompressible Navier-Stokes in a periodic domain, along any material trajectory $\mathbf{X}(t)$:
$$\ln\left(\frac{|\boldsymbol{\omega}(\mathbf{X}(t_2), t_2)|}{|\boldsymbol{\omega}(\mathbf{X}(t_1), t_1)|}\right) \le \int_{t_1}^{t_2} \lambda_3(\mathbf{X}(s), s) \, ds$$

## 2. Comparison with Classical Theorems

| Theorem / Criterion | Mathematical Statement | Assumptions & Domain | Comparison to Candidate B1 |
|:---|:---|:---|:---||
| **Beale-Kato-Majda (1984)** | $\int_0^T \|\boldsymbol{\omega}\|_{L^\infty} dt < \infty \implies$ Smooth | $H^s(\mathbb{R}^3), s > 5/2$ | BKM controls global $L^\infty$ vorticity; B1 gives pointwise trajectory growth bounded by strain eigenvalue $\lambda_3$. |
| **Constantin-Fefferman (1993)** | Direction of $\boldsymbol{\omega}$ Lipschitz $\implies$ Regular | $\mathbb{R}^3$, direction $\hat{\boldsymbol{\omega}}$ | Connects geometric alignment to regularity; B1 focuses on the principal strain eigenvalue $\lambda_3$. |
| **Gibbon (2008)** | $\frac{d}{dt}\|\boldsymbol{\omega}\|_{2m}^{2m} \le C \|\mathbf{S}\|_{L^\infty} \|\boldsymbol{\omega}\|_{2m}^{2m}$ | Periodic $L^{2m}$ norms | Gibbon establishes $L^p$ Eulerian bounds; B1 provides an exact pointwise Lagrangian bound along trajectories. |
| **Inviscid Euler Identity** | $|\boldsymbol{\omega}(t)| = |\boldsymbol{\omega}(0)| \exp(\int \lambda_\omega ds)$ | $\nu = 0$, exact | For Euler, B1 is a trivial consequence since $\lambda_\omega \le \lambda_3$. Under Navier-Stokes, B1 requires $\int V_{\log} ds \le \int (\lambda_3 - \lambda_\omega) ds$. |

