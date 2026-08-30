# TP2-G5-A1 — Forwardization and Convention Freeze

Status: DERIVED_WITH_LIMITATIONS. Scope is exact dynamics only; no A2
regularity or coercivity claim.

Let t_tau=T-tau, a_tau=A_{t_tau}, D_tau=D_{t_tau}, and use Convention M:

\[
[A]_{ij}=\partial_j u_i,\qquad [G]_{ij}=\partial_j\omega_i,\qquad
S=\tfrac12(A+A^T),\qquad \Omega=\tfrac12(A-A^T).
\]

Write G=J_omega(a_tau,t_tau),
\[
T^S_{ik}=(\partial_kS_{ij})\omega_j,\qquad
K^A_{ik}=(\partial_kA_{ij})\omega_j.
\]
Since Omega omega=0 in three-dimensional vorticity dynamics,
A omega=S omega and K^A=T^S-Omega G.

Under the accepted G3 orientation the forwardized history is
\[
da_\tau=-u(a_\tau,t_\tau)d\tau+\sqrt{2\nu}\,dB_\tau.
\]
The additive Brownian increment has no spatial derivative, so endpoint
composition gives the right-multiplication equation
\[
dD_\tau=D_\tau A(a_\tau,t_\tau)d\tau.
\]

Route A: applying Ito to the vorticity equation along the reverse history:
\[
d\omega=(-A\omega)d\tau+\sqrt{2\nu}\,G\,dB_\tau.
\]
Therefore
\[
d(D\omega)=(DA\omega-DA\omega)d\tau+\sqrt{2\nu}\,DG\,dB_\tau.
\]

Route B: differentiating
\[
(\partial_t+u\cdot\nabla-\nu\Delta)\omega=S\omega
\]
under Convention M gives
\[
(\partial_t+u\cdot\nabla-\nu\Delta)G=SG-GA+T^S.
\]
Reverse Ito transport gives
\[
dG=(-SG+GA-T^S)d\tau+
\sqrt{2\nu}\sum_\ell(\partial_\ell G)dB^\ell_\tau.
\]
Both routes agree exactly on the Z martingale and have the same sign.

The result is restricted to classical solution intervals in T^3 or a
decaying whole space, with no wall local-time term. It is not a Leray-Hopf
pathwise statement.
