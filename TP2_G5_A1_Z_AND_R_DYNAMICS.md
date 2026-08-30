# TP2-G5-A1 — Z and R Dynamics

Set
\[
Z_\tau=D_\tau\omega(a_\tau,t_\tau),\qquad
Y_\tau=D_\tau G(a_\tau,t_\tau),\qquad R_\tau=|Z_\tau|^2.
\]
The exact G3 martingale is
\[
\boxed{dZ_\tau=\sqrt{2\nu}\,Y_\tau\,dB_\tau.}
\]
With N=||Y||_F^2, Ito's formula gives
\[
\boxed{dR_\tau=2\nu N_\tau d\tau+dM^R_\tau},
\qquad
( \sigma_R)_\ell=2\sqrt{2\nu}\,Z_\tau^TY_\tau e_\ell.
\]
Thus dM^R=sigma_R dot dB and, under stopped integrability,
\[
\frac{d}{d\tau}{\mathbb E}R_\tau=2\nu{\mathbb E}N_\tau.
\]
Because d tau=-d s,
\[
\partial_s{\mathbb E}|Z_s|^2=-2\nu{\mathbb E}||D_sJ_\omega||_F^2,
\]
matching the accepted G3 second-moment orientation.
