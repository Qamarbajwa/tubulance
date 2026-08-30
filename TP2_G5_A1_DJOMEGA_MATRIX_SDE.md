# TP2-G5-A1 — Exact Matrix SDE for Y=D J_omega

Let A=J_u, G=J_omega, S=(A+A^T)/2, Omega=(A-A^T)/2, and
T^S_{ik}=(\partial_kS_{ij})omega_j. Define
\[
C_\ell=D(\partial_\ell G).
\]
The gradient transport equation and reverse-history SDE are
\[
(\partial_t+u\cdot\nabla-\nu\Delta)G=SG-GA+T^S,
\]
\[
dG=(-SG+GA-T^S)d\tau+
\sqrt{2\nu}\sum_\ell(\partial_\ell G)dB^\ell_\tau.
\]
Combining with dD=DA d tau gives
\[
\boxed{dY=B_Yd\tau+\sqrt{2\nu}\sum_\ell C_\ell dB^\ell_\tau},
\qquad
\boxed{B_Y=D(\Omega G+GA-T^S).}
\]
Equivalently, with K^A_{ik}=(\partial_kA_{ij})omega_j=T^S_{ik}-(Omega G)_{ik},
\[
\boxed{B_Y=D(GA-K^A).}
\]
The exact order is GA, not AG. The unverified pattern D(K-AG) has both a
sign and ordering mismatch.

Consistency routes:
1. Endpoint composition gives DA; gradient transport gives -SG+GA-T^S;
   their sum is D(Omega G+GA-T^S).
2. The Cauchy martingale calculation gives the spatial-noise coefficient
   D(partial_ell G), while the same compatibility calculation gives the
   deterministic terms above.

No deformation-gradient Brownian term appears because the Brownian forcing
is additive and spatially constant.
