# TH9-R EXACT VORTICITY-DIRECTION EQUATION DERIVATION

## 1. Mathematical Derivation
Starting from the Navier–Stokes vorticity equation $\frac{D\boldsymbol{\omega}}{Dt} = \mathbf{S}\boldsymbol{\omega} + \nu \Delta\boldsymbol{\omega}$ with $\boldsymbol{\omega} = q \boldsymbol{\xi}$ ($q = |\boldsymbol{\omega}|, \boldsymbol{\xi} = \boldsymbol{\omega}/q$):

$$\frac{Dq}{Dt} = \boldsymbol{\xi} \cdot \frac{D\boldsymbol{\omega}}{Dt} = \boldsymbol{\xi}^T \mathbf{S} (q\boldsymbol{\xi}) + \nu (\boldsymbol{\xi}\cdot\Delta\boldsymbol{\omega}) = q \lambda_\omega + \nu (\boldsymbol{\xi}\cdot\Delta\boldsymbol{\omega})$$

Differentiating $\boldsymbol{\xi} = \boldsymbol{\omega}/q$:
$$\frac{D\boldsymbol{\xi}}{Dt} = \frac{1}{q}\frac{D\boldsymbol{\omega}}{Dt} - \frac{\boldsymbol{\xi}}{q}\frac{Dq}{Dt} = \mathbf{S}\boldsymbol{\xi} - \lambda_\omega \boldsymbol{\xi} + \frac{\nu}{q}\left[\Delta\boldsymbol{\omega} - (\boldsymbol{\xi}\cdot\Delta\boldsymbol{\omega})\boldsymbol{\xi}\right] = \mathbf{R}_{\text{strain}} + \mathbf{R}_{\text{visc}}$$

Since both $\mathbf{R}_{\text{strain}}$ and $\mathbf{R}_{\text{visc}}$ are projected onto $(I - \boldsymbol{\xi}\boldsymbol{\xi}^T)$, they satisfy $\boldsymbol{\xi}\cdot\mathbf{R}_{\text{strain}} = 0$ and $\boldsymbol{\xi}\cdot\mathbf{R}_{\text{visc}} = 0$ identically.
