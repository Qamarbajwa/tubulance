# TP2-G5-A4 — Scale-Critical Hypothetical Window

## Conditional contract

Assume only for scenario analysis that a smooth periodic solution exists on

\[
[0,T_*),\qquad T_*<\infty,
\]

and choose \(t_n\uparrow T_*\) and terminal points \(x_n\) by a dangerous-vorticity rule, for example \(|\omega(x_n,t_n)|=\|\omega(t_n)\|_\infty\). Write \(M_n=|\omega(x_n,t_n)|\). The implication \(M_n\to\infty\) is made only when the selected continuation theorem justifies it; it is not assumed as a definition of singularity.

Fix \(a>0\), set \(L_n=a/M_n\), and \(s_n=t_n-L_n\) when \(s_n\ge0\). Since vorticity has time weight \(2\) under \(u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2t)\), \(M_n\mapsto\lambda^2M_n\) and \(L_n\mapsto\lambda^{-2}L_n\). Thus \(L_n\) has the Navier–Stokes time dimension and is scale-covariant.

The selected window is intrinsic and does not assert regularity on the window. Analyticity radii, strain times, enstrophy scales, vorticity-gradient scales, and BKM/Serrin quantities are catalogued as conditional alternatives only: each either requires extra hypotheses or already contains continuation-critical control. No alternative is promoted to the primary window.

The fixed unit torus qualification remains active: scaling weights and rescaled-family reasoning do not create an unrestricted exact symmetry of one fixed domain.

