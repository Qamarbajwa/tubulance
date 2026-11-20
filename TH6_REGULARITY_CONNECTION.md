# TH6 REGULARITY CONNECTION & THE NONLINEAR GAP

## 1. What Candidate B1 Implies
If Candidate B1 holds universally along all trajectories, then the pointwise vorticity magnitude is bounded by:
$$\|\boldsymbol{\omega}(\cdot, t)\|_{L^\infty} \le \|\boldsymbol{\omega}(\cdot, 0)\|_{L^\infty} \exp\left( \sup_{\mathbf{X}} \int_0^t \lambda_3(\mathbf{X}(s), s) \, ds \right)$$

## 2. The Missing Mathematical Step (Why B1 Does Not Prove Regularity Alone)
The fundamental difficulty of 3D Navier-Stokes is that the strain tensor $\mathbf{S} = \frac{1}{2}(\nabla\mathbf{u} + \nabla\mathbf{u}^T)$ is nonlocally related to $\boldsymbol{\omega}$ via the singular Riesz transform (Biot-Savart law):
$$\mathbf{S}(\mathbf{x}) = \text{P.V.} \int_{\mathbb{R}^3} \mathbf{K}(\mathbf{x} - \mathbf{y}) \times \boldsymbol{\omega}(\mathbf{y}) \, d\mathbf{y}$$
Therefore, $\lambda_3$ scales as $O(|\boldsymbol{\omega}|)$ in $L^\infty$. Thus:
$$\frac{D|\boldsymbol{\omega}|}{Dt} \le \lambda_3 |\boldsymbol{\omega}| \sim C |\boldsymbol{\omega}|^2$$
which yields a Riccati-type differential inequality admitting finite-time blowup in the absence of a priori global strain bounds. B1 proves that vorticity amplification along trajectories is controlled by the history of the maximum strain rate $\lambda_3$, but does not independently bound $\int_0^T \lambda_3 dt$.
