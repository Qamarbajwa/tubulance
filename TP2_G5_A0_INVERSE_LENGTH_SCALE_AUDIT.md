# TP2-G5-A0 — Inverse-Length-Scale Audit

## Closest established analogue

Gibbon, *A hierarchy of length scales for weak solutions of the
three-dimensional Navier–Stokes equations*, Comm. Math. Sci. 10 (2012),
DOI [10.4310/CMS.2012.v10.n1.a7](https://doi.org/10.4310/CMS.2012.v10.n1.a7),
[arXiv:1012.3604](https://arxiv.org/abs/1012.3604), defines time-averaged
inverse length scales from moments of vorticity on a periodic box. The lowest
scale recovers the inverse Kolmogorov scale; higher moments have rapidly
growing Reynolds-number exponents.

The classical local Eulerian quantity

\[
 |\nabla\omega|/|\omega|
\]

is an inverse-vorticity length (where `omega != 0`). In project notation,
`kappa_omega=||J_omega||/|omega|` is its Frobenius version.

## Comparison with Xi

`kappa_omega^2` is the local inverse-vorticity-length factor, but

\[
 \Xi=\frac{\|DJ_\omega\|_F^2}{|D\omega|^2}
 =\kappa_\omega^2\Theta
\]

on the regular domain. The deformation `D` appears in both numerator and
denominator, and `Theta` records relative deformation orientation. Therefore
Xi is not simply an Eulerian inverse length and not merely a stochastic
reweighting of Gibbon's hierarchy. Equivalence would require a theorem
controlling the deformation action on both the vorticity and its gradient,
including the induced Cauchy-energy weight.

## Verdict

`kappa_omega^2`: known analogue / N0 foundation.  
`Xi`: related but distinct; no exact equivalent found in the audited sources.  
`E_mu[Xi]`: project-specific weighted observable; no audited theorem gives an
a-priori scale-critical bound.  Gibbon's time-averaged Eulerian hierarchy is
not evidence for such a bound.
