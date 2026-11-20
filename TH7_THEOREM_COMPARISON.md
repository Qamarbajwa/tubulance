# TH7 LITERATURE THEOREM COMPARISON: VISCOUS VORTICITY INFLUX

## 1. Magnitude-Direction Decomposition in the Literature
The decomposition $\Delta(q \boldsymbol{\xi}) = \boldsymbol{\xi} \Delta q + 2(\nabla q\cdot\nabla)\boldsymbol{\xi} + q \Delta \boldsymbol{\xi}$ with $\boldsymbol{\xi}\cdot\Delta\boldsymbol{\xi} = -\|\nabla\boldsymbol{\xi}\|_F^2$ connects directly to:

1. **Constantin & Fefferman (1993)**: Explored the geometric direction field $\boldsymbol{\xi} = \hat{\boldsymbol{\omega}}$ and showed that direction Lipschitz regularity depletes the nonlinear vortex stretching term.
2. **Gibbon (2008)**: Proved that enstrophy dissipation $-2\nu \|\nabla\boldsymbol{\omega}\|_{L^2}^2$ controls the global $L^2$ volume integral, but does not prevent pointwise local viscous concentration.
3. **Maximum Principles for Parabolic PDE**: In scalar heat equations $\partial_t u = \nu \Delta u$, the maximum principle enforces $\sup u(t) \le \sup u(0)$. In Navier-Stokes, vortex stretching breaks the scalar maximum principle, while the vector Laplacian $\nu \Delta\boldsymbol{\omega}$ locally redistributes enstrophy into troughs.

